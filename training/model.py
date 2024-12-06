import timm
import torch
import torch.nn as nn
import torchmetrics
import pytorch_lightning as pl


class ViTLightningModule(pl.LightningModule):
    def __init__(
        self,
        pretrained,
        num_labels=5,
        learning_rate=2e-04,
        weight_decay=0.01,
        patch=16,
        name="base",
        optimizer="Adam",
        momentum=0,
    ):
        super(ViTLightningModule, self).__init__()

        self.save_hyperparameters()

        patch_size = "16" if patch == 16 else "32"
        self.model = timm.create_model(
            f"vit_{name}_patch{patch_size}_224", pretrained=pretrained
        )

        self.model.head = nn.Linear(self.model.head.in_features, num_labels)
        self.criterion = nn.CrossEntropyLoss()
        self.learning_rate = learning_rate

        self.weight_decay = weight_decay
        self.optimizer = optimizer
        self.momentum = momentum

    def forward(self, x):
        x = self.model(x)
        return x

    def common_step(self, batch):
        data, target = batch
        logits = self(data)  # forwrad pass for the model --> it is the output
        loss = self.criterion(logits, target)
        predictions = logits.argmax(dim=1)

        return loss, predictions, target, logits

    def training_step(self, batch):
        loss_train, predictions_train, target_train, logits_train = self.common_step(
            batch
        )

        return loss_train, predictions_train, target_train, logits_train

    def validation_step(self, batch):
        loss_val, predictions_val, target_val, logits_val = self.common_step(batch)

        return loss_val, predictions_val, target_val, logits_val

    def test_step(self, batch):
        loss_test, predictions_test, target_test, logits = self.common_step(batch)

        return loss_test, predictions_test, target_test, logits

    def configure_optimizers(self):
        optimizers = {
            "Adam": torch.optim.Adam(
                self.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay
            ),
            "SGD": torch.optim.SGD(
                self.parameters(),
                lr=self.learning_rate,
                weight_decay=self.weight_decay,
                momentum=self.momentum,
            ),
        }
        return optimizers[self.optimizer]
