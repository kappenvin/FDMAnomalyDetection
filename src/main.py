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
from data.dataset import DataClass_own_data_faster
from training.model import ViTLightningModule
from data.transforms import create_train_transform, create_val_transform
import mlflow
import mlflow.pytorch

# MLflow setup
EXPERIMENT_NAME = "ViT_Test_anomalydetection"

os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"
mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "default_value_if_not_set")
mlflow.set_tracking_uri(mlflow_tracking_uri)


def get_or_create_experiment(experiment_name):

    if experiment := mlflow.get_experiment_by_name(experiment_name):
        return experiment.experiment_id
    else:
        return mlflow.create_experiment(experiment_name)


experiment_id = get_or_create_experiment(EXPERIMENT_NAME)



# override Optuna's default logging to ERROR only
optuna.logging.set_verbosity(optuna.logging.ERROR)

# load the config files

config_file_names = [
    r"C:\Anomaly_detection_3D_printing\configs\data_config.yaml",
    r"C:\Anomaly_detection_3D_printing\configs\training_config.yaml",
    r"C:\Anomaly_detection_3D_printing\configs\callback_logging_config.yaml"
]

data_config= yaml.load(open(config_file_names[0], "r"), Loader=yaml.SafeLoader)
training_config = yaml.load(open(config_file_names[1], "r"), Loader=yaml.SafeLoader)
callback_logging_config = yaml.load(open(config_file_names[2], "r"), Loader=yaml.SafeLoader)
        


# Read in the data

csv_path_train = (
   data_config["data"]["train_csv_path"]
)
csv_path_val = (
    data_config["data"]["val_csv_path"]
)


# get only the first 100 rows for testing
df_train = pd.read_csv(csv_path_train).head(100)
df_val = pd.read_csv(csv_path_val).head(100)


# create the dataclasses and dataloaders
transform_training = create_train_transform(data_config)
transform_val = create_val_transform(data_config)

train_dataset = DataClass_own_data_faster(df_train, transform=transform_training)
val_dataset = DataClass_own_data_faster(df_val, transform=transform_val)


def objective(trial):

    learning_rate = trial.suggest_categorical("learning_rate", training_config["optuna"]["search_space"]["learning_rate"])

    current_run_name = f"trial_{trial.number}_lr_{learning_rate:.0e}"

    with mlflow.start_run(run_name=current_run_name,experiment_id=experiment_id, nested=True) as child_run:
        # Use the run_id of this child run in the MLFlowLogger
        child_run_id = child_run.info.run_id

        pl.seed_everything(42, workers=True)

        # define parameters

        train_dataloader = DataLoader(
            train_dataset,
            batch_size=training_config["training"]["batch_size"],
            shuffle=True,
            num_workers=training_config["training"]["num_workers"],
        )
        val_dataloader = DataLoader(
            val_dataset,
            batch_size=training_config["training"]["batch_size"],
            shuffle=False,
            num_workers=training_config["training"]["num_workers"],
        )

        

        # Initialize model
        model = ViTLightningModule(
            pretrained=True,
            num_labels=5,
            patch=training_config["model"]["patch_size"],
            learning_rate=learning_rate,
            name=training_config["model"]["name"],
            weight_decay=training_config["model"]["weight_decay"],
            optimizer=training_config["model"]["optimizer"],
        )

        # Define hyperparameters
        hyperparameters = {
                "learning_rate": model.learning_rate,
                "weight_decay": model.weight_decay,
                "optimizer": model.optimizer,
                "batch_size": training_config["training"]["batch_size"],
                "model_type": f"ViT_{training_config['model']['name']}",
            }
        
        # tags for training
        tags={
                    "project": "3D Printing Anomaly Detection",
                    "optimizer_engine": "optuna",
                    "model_family": "ViT",
                    "feature_set_version": "1",
                }
        # Create the MLFlowLogger once
        mlflow_logger = MLFlowLogger(
            experiment_name=EXPERIMENT_NAME,
            run_name=current_run_name,
            run_id=child_run_id,
            tracking_uri=mlflow_tracking_uri,
            log_model=True,
            tags=tags,
        )

        # log the hyperparameters
        mlflow_logger.log_hyperparams(hyperparameters)


        # Keep only EarlyStopping callback
        early_stop_callback = EarlyStopping(
            monitor="val_f1_score", mode="max", patience=5
        )

        #TODO: delete the local model checkpoints or define a custom logger 


        # ModelCheckpoint for tracking best models but not saving locally
        checkpoint_callback = ModelCheckpoint(
            monitor="val_f1_score",
            mode="max",
            save_top_k=2,
            save_last=True,
        )

        # Trainer
        trainer = pl.Trainer(
            accelerator="gpu",
            min_epochs=1,
            max_epochs=2,
            fast_dev_run=False,
            callbacks=[early_stop_callback, checkpoint_callback],
            enable_progress_bar=True,
            logger=mlflow_logger,
        )

        # Train
        trainer.fit(model, train_dataloader, val_dataloader)

        # The best checkpoint path
        best_model_path = checkpoint_callback.best_model_path

        # The best F1 score
        best_f1_score = checkpoint_callback.best_model_score.item()

        # Log the best score using the MLFlowLogger's experiment client
        mlflow_logger.experiment.log_metric(
            mlflow_logger.run_id,
            key="best_f1_score",
            value=float(best_f1_score)
        )

        # 1. Load the best checkpoint
        best_model_path = checkpoint_callback.best_model_path
        best_model = ViTLightningModule.load_from_checkpoint(best_model_path)
        
        # 2. Log the best model to MLflow Model Registry
        mlflow.pytorch.log_model(
            pytorch_model=best_model,
            artifact_path="model_artifacts",
            registered_model_name="vit_model",
            run_id=mlflow_logger.run_id
        )

        return best_f1_score


def run_optuna_study(run_name="parent run"):

    with mlflow.start_run(run_name=run_name,experiment_id=experiment_id, nested=True) as parent_run:
        print(f"Parent run_id: {parent_run.info.run_id}")
        
        study = optuna.create_study(
            direction="maximize",
        )

        study.optimize(objective, n_trials=2)


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