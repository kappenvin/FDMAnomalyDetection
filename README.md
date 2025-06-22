## Description

This project focuses on developing an automated system for identifying anomalies in Fused Deposition Modeling (FDM) 3D prints.

Key aspects include:

FDM Anomaly Detection: Real-time identification of print defects.
Nozzle-Mounted Camera: Utilized for precise image acquisition.
Four Distinct Error Types: Capability to classify between stringing, underextrusion, overextrusion and spaghetti failure.
Extensive Dataset: Trained on 85,000 images for high accuracy.

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
