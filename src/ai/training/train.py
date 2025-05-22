# Standard library imports
import os
import sys
import time
import json

# Third-party imports
import torch
from torch.utils.data import Dataset, DataLoader
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
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

df_train = pd.read_csv(csv_path_train).head(100)
df_val = pd.read_csv(csv_path_val).head(100)


# create the dataclasses and dataloaders
transform_training = create_train_transform(config["transforms"])
transform_val = create_val_transform(config["transforms"])

train_dataset = DataClass_own_data_faster(df_train, transform=transform_training)
val_dataset = DataClass_own_data_faster(df_val, transform=transform_val)

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


def save_hyperparameters(trial, log_dir, f1_score, acc_score=None):
    params = {
        "trial_number": trial.number,
        "params": trial.params,
        "best_f1_score": f1_score,
        "best_accuracy": acc_score,
    }

    file_path = os.path.join(log_dir, f"hyperparameters_trial_{trial.number}.json")

    with open(file_path, "w") as f:
        json.dump(params, f, indent=4)


def objective(trial, train_dataloader, val_dataloader):

    g = torch.Generator()
    g.manual_seed(42)
    pl.seed_everything(42, workers=True)

    # Define the hyperparameters to tune
    batch_size = 64
    learning_rate = trial.suggest_categorical("learning_rate", [1e-5, 1e-5, 1e-5, 1e-5])
    weight_decay = 0

    # Create dataloaders with the suggested batch size
    train_dataloader = train_dataloader
    val_dataloader = val_dataloader

    # Initialize the model with suggested hyperparameters
    model = ViTLightningModule(
        pretrained=True,
        num_labels=5,
        patch=16,
        learning_rate=learning_rate,
        name="base",
        weight_decay=weight_decay,
        optimizer="Adam",
    )

    # define the logger
    logger = TensorBoardLogger(
        "tb_logs/", name=f"vit_base_16_Adam_variance_test_optuna_trial_{trial.number}"
    )
    # save best model based on f1_score
    checkpoint_callback = ModelCheckpoint(
        monitor="val_f1_score",
        mode="max",
        save_top_k=2,
        filename="best_model_{epoch:02d}-{val_f1_score:.2f}",
    )

    accuracy_callback = ModelCheckpoint(
        monitor="val_accuracy",
        mode="max",
        save_top_k=2,
        filename="best_accuracy_model_{epoch:02d}-{val_accuracy:.2f}",
    )
    early_stop_callback = EarlyStopping(monitor="val_f1_score", mode="max", patience=5)
    # Create a PyTorch Lightning trainer
    trainer = pl.Trainer(
        accelerator="gpu",
        min_epochs=1,
        max_epochs=20,
        fast_dev_run=False,
        logger=logger,
        callbacks=[early_stop_callback, checkpoint_callback, accuracy_callback],
    )

    # Train the model
    trainer.fit(model, train_dataloader, val_dataloader)

    # Get the best validation score
    best_f1_score = checkpoint_callback.best_model_score.item()
    best_accuracy = accuracy_callback.best_model_score.item()
    print(f"Best validation score: {best_f1_score}")

    # Save hyperparameters
    log_dir = logger.log_dir
    save_hyperparameters(trial, log_dir, best_f1_score, best_accuracy)

    # Return the best validation accuracy
    return best_f1_score


def run_optuna_study():
    # save best hyperparameters
    search_space = {"learning_rate": [1e-5, 1e-5, 1e-5, 1e-5]}
    base_logger = TensorBoardLogger("tb_logs/", name="vit_base_16_optuna_study")

    study = optuna.create_study(
        sampler=optuna.samplers.GridSampler(seed=42, search_space=search_space),
    )
    study.optimize(objective, n_trials=4)  # Adjust n_trials as needed

    print("Best trial:")
    best_trial = study.best_trial
    print("  Params: ")
    for key, value in best_trial.params.items():
        print(f"    {key}: {value}")

    # Save the best hyperparameters
    best_log_dir = os.path.join(base_logger.log_dir, "best_trial")
    os.makedirs(best_log_dir, exist_ok=True)
    save_hyperparameters(best_trial, best_log_dir, study.best_value)

    return study


start_time = time.time()


study = run_optuna_study()


end_time = time.time()

elapsed_time = end_time - start_time
print(f"Elapsed time for training: {elapsed_time/60} minutes")


# You can now use the returned study object for further analysis if needed
print(f"Best value: {study.best_value}")
print(f"Best params: {study.best_params}")
