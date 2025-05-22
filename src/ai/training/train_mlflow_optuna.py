# Standard library imports
import os
import sys
import time
import json

# Third-party imports
import torch
from torch.utils.data import Dataset, DataLoader
import pytorch_lightning as pl
from pytorch_lightning.loggers import MLFlowLogger
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
import torchvision.transforms.v2 as v2
import optuna
import pandas as pd
import yaml
import pdb  # For debugging

# Local imports
from dataset import DataClass_own_data_faster
from model import ViTLightningModule
from transforms import create_train_transform, create_val_transform
import mlflow
import mlflow.pytorch

# MLflow setup
EXPERIMENT_NAME = "ViT_Test_anomalydetection"
mlflow.set_tracking_uri("http://localhost:5000")
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"


def get_or_create_experiment(experiment_name):

    if experiment := mlflow.get_experiment_by_name(experiment_name):
        return experiment.experiment_id
    else:
        return mlflow.create_experiment(experiment_name)


experiment_id = get_or_create_experiment(EXPERIMENT_NAME)



# override Optuna's default logging to ERROR only
optuna.logging.set_verbosity(optuna.logging.ERROR)

# load the config file
with open(r"C:\Anomaly_detection_3D_printing\training\config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)


# Read in the data

csv_path_train = (
    r"C:\Anomaly_detection_3D_printing\data\csv_files\train_gray_black_resized.csv"
)
csv_path_val = (
    r"C:\Anomaly_detection_3D_printing\data\csv_files\val_gray_black_resized.csv"
)


# get only the first 100 rows for testing
df_train = pd.read_csv(csv_path_train).head(100)
df_val = pd.read_csv(csv_path_val).head(100)


# create the dataclasses and dataloaders
transform_training = create_train_transform(config["transforms"])
transform_val = create_val_transform(config["transforms"])

train_dataset = DataClass_own_data_faster(df_train, transform=transform_training)
val_dataset = DataClass_own_data_faster(df_val, transform=transform_val)


def objective(trial):

    learning_rate = trial.suggest_categorical("learning_rate", [1e-5, 1e-4, 1e-3, 1e-2])

    current_run_name = f"trial_{trial.number}_lr_{learning_rate:.0e}"
    with mlflow.start_run(
        experiment_id=experiment_id, run_name=current_run_name, nested=True
    ):
        pl.seed_everything(42, workers=True)

        # define parameters

        train_dataloader = DataLoader(
            train_dataset,
            batch_size=config["training"]["batch_size"],
            shuffle=True,
            num_workers=config["training"]["num_workers"],
        )
        val_dataloader = DataLoader(
            val_dataset,
            batch_size=config["training"]["batch_size"],
            shuffle=False,
            num_workers=config["training"]["num_workers"],
        )

        # Define hyperparameters

        weight_decay = 0

        # Initialize model
        model = ViTLightningModule(
            pretrained=True,
            num_labels=5,
            patch=config["model"]["patch_size"],
            learning_rate=learning_rate,
            name=config["model"]["name"],
            weight_decay=weight_decay,
            optimizer="Adam",
        )

        # Log parameters to MLflow
        # Log model parameters
        mlflow.log_params(
            {
                "learning_rate": model.learning_rate,
                "weight_decay": model.weight_decay,
                "optimizer": model.optimizer,
                "batch_size": config["training"]["batch_size"],
                "model_type": "ViT_base",
            }
        )

        # Keep only EarlyStopping callback
        early_stop_callback = EarlyStopping(
            monitor="val_f1_score", mode="max", patience=5
        )

        # ModelCheckpoint for tracking best models but not saving locally
        checkpoint_callback = ModelCheckpoint(
            monitor="val_f1_score",
            mode="max",
            save_top_k=2,
            save_last=True,
            dirpath=None,  # This prevents local saving
        )

        # Trainer
        trainer = pl.Trainer(
            accelerator="gpu",
            min_epochs=1,
            max_epochs=5,
            fast_dev_run=False,
            callbacks=[early_stop_callback, checkpoint_callback],
            enable_progress_bar=True,
            logger=MLFlowLogger(experiment_name=EXPERIMENT_NAME,run_name=current_run_name,tracking_uri="http://localhost:5000"),
        )

        # Train
        trainer.fit(model, train_dataloader, val_dataloader)

        # Get the best scores from the trainer's logged metrics
        best_f1_score = checkpoint_callback.best_model_score.item()

        mlflow.log_metrics(
            {
                "best_f1_score": float(best_f1_score),
            }
        )
        # Log best model
        mlflow.pytorch.log_model(model, "last try", registered_model_name="vit_model")

        return best_f1_score


def run_optuna_study(run_name="parent run"):

    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name, nested=True):

        study = optuna.create_study(
            direction="maximize",
        )

        study.optimize(objective, n_trials=2)

        # Log tags
        mlflow.set_tags(
            tags={
                "project": "Apple Demand Project",
                "optimizer_engine": "optuna",
                "model_family": "ViT",
                "feature_set_version": 1,
            }
        )

        print("Best trial:")
        print("  Value: ", study.best_value)
        print("  Params: ")
        for key, value in study.best_params.items():
            print(f"    {key}: {value}")

        return study


run_name = "test run"
start_time = time.time()


study = run_optuna_study(run_name=run_name)

end_time = time.time()
elapsed_time = (end_time - start_time) / 60

print(f"Elapsed time for training: {elapsed_time} minutes")
print(f"Best value: {study.best_value}")
print(f"Best params: {study.best_params}")
