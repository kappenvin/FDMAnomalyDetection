## Configuration Files

- `data_config.yaml`: Configuration for data preprocessing and loading.
- `model_config.yaml`: Configuration for the model architecture.
- `training_config.yaml`: Configuration for training parameters.

## Source Code

- `src/data`: Contains data loading and transformation scripts.
  - `dataset.py`: Dataset class for loading and processing data.
  - `transforms.py`: Data transformation utilities.
- `src/models`: Contains model definitions.
  - `vit_model.py`: Vision Transformer model implementation.
- `src/training`: Contains training-related scripts.
  - `trainer.py`: Training loop and logic.
  - `optimizer.py`: Optimizer configuration.
- `src/utils`: Contains utility scripts.
  - `logging_utils.py`: Logging utilities.

## Training

To train the model, run the following commands :

```bash
cd src

python main.py
```
