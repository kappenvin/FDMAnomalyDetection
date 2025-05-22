# Standard library imports
import os
import time

# Third-party imports
import torch
from torch.utils.data import DataLoader
import pytorch_lightning as pl
from pytorch_lightning.loggers import MLFlowLogger
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
import pandas as pd
import yaml
import mlflow
import mlflow.pytorch
import pdb

# Local imports
from dataset import DataClass_own_data_faster
from model import ViTLightningModule
from transforms import create_train_transform, create_val_transform

# MLflow setup
EXPERIMENT_NAME = "ViT_Test_anomalydetection"
mlflow.set_tracking_uri("http://localhost:5000")
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"



def setup_mlflow():
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        mlflow.create_experiment(EXPERIMENT_NAME)
    mlflow.set_experiment(EXPERIMENT_NAME)


# Load config
with open(r"C:\Anomaly_detection_3D_printing\training\config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)


def train_model():

    # Set seeds for reproducibility
    pl.seed_everything(42, workers=True)

    # Load and prepare data
    df_train = pd.read_csv(
        r"C:\Anomaly_detection_3D_printing\data\csv_files\train_gray_black_resized.csv"
    ).head(100)
    df_val = pd.read_csv(
        r"C:\Anomaly_detection_3D_printing\data\csv_files\val_gray_black_resized.csv"
    ).head(100)

    # Create transforms and datasets
    transform_training = create_train_transform(config["transforms"])
    transform_val = create_val_transform(config["transforms"])

    train_dataset = DataClass_own_data_faster(df_train, transform=transform_training)
    val_dataset = DataClass_own_data_faster(df_val, transform=transform_val)

    # Create dataloaders
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

    with mlflow.start_run(run_name="vit_training") as run:
        # Initialize model
        model = ViTLightningModule(
            pretrained=True,
            num_labels=5,
            patch=16,
            learning_rate=1e-4,  # You can adjust these parameters
            name="base",
            weight_decay=0,
            optimizer="Adam",
        )

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

        # Define callbacks
        early_stop_callback = EarlyStopping(
            monitor="val_f1_score", mode="max", patience=5
        )

        logger=MLFlowLogger(experiment_name=EXPERIMENT_NAME,log_model=True,tracking_uri=os.getenv("MLFLOW_TRACKING_URI"),run_id=run.info.run_id)
        print(logger._artifact_location)
        checkpoint_callback = ModelCheckpoint(
            monitor="val_f1_score",
            mode="max",
            save_top_k=2,
            filename="best-model-{epoch:02d}-{val_f1_score:.2f}",
        )

        
        # Configure trainer
        trainer = pl.Trainer(
            accelerator="gpu",
            devices=1,
            min_epochs=1,
            max_epochs=3,
            callbacks=[early_stop_callback, checkpoint_callback],
            enable_progress_bar=True,
            logger=logger,
        )

        # Train the model
        trainer.fit(model, train_dataloader, val_dataloader)

        # Log best metrics
        #best_f1_score = checkpoint_callback.best_model_score.item()

        #mlflow.log_metrics({"best_f1_score": best_f1_score})
        print(trainer.callback_metrics.get('val_f1_score'))

        # Log best model
        #mlflow.pytorch.log_model(model, "best_model", registered_model_name="vit_model")

        return  model


if __name__ == "__main__":
    # Setup MLflow
    setup_mlflow()

    # Time the training
    start_time = time.time()

    # Train the model
    trained_model = train_model()

    # Calculate training time
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60

    print(f"Training completed in {elapsed_time:.2f} minutes")
    #print(f"Best F1 Score: {best_f1_score:.4f}")
