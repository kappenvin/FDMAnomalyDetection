
import pytorch_lightning as pl
import mlflow.pytorch

class MLflowModelCheckpoint(pl.Callback):
    def __init__(self):
        super().__init__()
        self.best_val_f1_scores = {"epoch": [], "f1_score": []}
    def on_validation_end(self, trainer, pl_module):
        current_score = trainer.callback_metrics.get('val_f1_score')
        if current_score > trainer.callback_metrics.get('best_val_f1_score', float('-inf')):
            mlflow.pytorch.log_model(pl_module, "best_model")