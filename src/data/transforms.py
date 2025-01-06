import torch
from torchvision.transforms import v2
import yaml
import pdb

from icecream import ic


def create_train_transform(config):
    return v2.Compose(
        [
            (
                v2.RandomHorizontalFlip()
                if config["transforms"]["augmentation"]["random_horizontal_flip"]
                else None
            ),
            v2.RandomRotation(config["transforms"]["augmentation"]["rotation_degrees"]),
            v2.RandomGrayscale(p=config["transforms"]["augmentation"]["grayscale_prob"]),
            v2.ColorJitter(**config["transforms"]["augmentation"]["color_jitter"]),
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(
                mean=config["transforms"]["normalization"]["mean"], std=config["transforms"]["normalization"]["std"]
            ),
        ]
    )


def create_val_transform(config):
    return v2.Compose(
        [
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(
                mean=config["transforms"]["normalization"]["mean"], std=config["transforms"]["normalization"]["std"]
            ),
        ]
    )


if __name__ == "__main__":
    config_file_path= r"C:\Anomaly_detection_3D_printing\configs\data_config.yaml"
    config=yaml.load(open(config_file_path, "r"), Loader=yaml.SafeLoader)

    train_transform = create_train_transform(config)
    val_transform = create_val_transform(config)

    
    ic(train_transform)
