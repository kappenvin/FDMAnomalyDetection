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

        # define the metrices
        self.train_acc = torchmetrics.Accuracy(
            task="multiclass", num_classes=num_labels, average="weighted"
        )
        self.train_f1_score = torchmetrics.F1Score(
            task="multiclass", num_classes=num_labels, average="weighted"
        )
        self.val_acc = torchmetrics.Accuracy(
            task="multiclass", num_classes=num_labels, average="weighted"
        )
        self.val_f1_score = torchmetrics.F1Score(
            task="multiclass", num_classes=num_labels, average="weighted"
        )

        self.test_f1_score = torchmetrics.F1Score(
            task="multiclass", num_classes=num_labels, average="weighted"
        )

        self.test_acc = torchmetrics.Accuracy(
            task="multiclass", num_classes=num_labels, average="weighted"
        )

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
        self.train_acc(predictions_train, target_train)
        self.train_f1_score(predictions_train, target_train)

        
        metrics =  {
                "train_loss": loss_train,
                "train_accuracy": self.train_acc.compute().item(),
                "train_f1_score": self.train_f1_score.compute().item(),
            }
        self.logger.log_metrics(metrics, step=int(self.current_epoch))

        return loss_train

    def validation_step(self, batch):
        loss_val, predictions_val, target_val, logits_val = self.common_step(batch)
        self.val_acc(predictions_val, target_val)  # is like self.accuracy.update()
        self.val_f1_score(predictions_val, target_val)

        metrics={
                "val_loss": loss_val,
                "val_accuracy": self.val_acc.compute().item(),
                "val_f1_score": self.val_f1_score.compute().item(),
            }

        self.log("val_f1_score", self.val_f1_score(predictions_val, target_val), on_epoch=True, prog_bar=True)
        self.logger.log_metrics(metrics, step=int(self.current_epoch))
            

        return loss_val

    def test_step(self, batch):
        loss_test, predictions_test, target_test, logits = self.common_step(batch)
        self.test_acc(predictions_test, target_test)
        self.test_f1_score(predictions_test, target_test)

    
        metrics={
                "test_loss": loss_test,
                "test_accuracy": self.test_acc.compute().item(),
                "test_f1_score": self.test_f1_score.compute().item(),
            },
        self.logger.log_metrics(metrics, step=int(self.current_epoch))
        

        return loss_test

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
