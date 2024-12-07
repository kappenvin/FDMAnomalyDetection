FDMAnomalyDetection/
├── config/
│ ├── data_config.yaml
│ ├── model_config.yaml
│ └── training_config.yaml
├── src/
│ ├── **init**.py
│ ├── data/
│ │ ├── **init**.py
│ │ ├── dataset.py
│ │ └── transforms.py
│ ├── models/
│ │ ├── **init**.py
│ │ └── vit_model.py
│ ├── training/
│ │ ├── **init**.py
│ │ ├── trainer.py
│ │ └── optimizer.py
│ └── utils/
│ ├── **init**.py
│ └── logging_utils.py
└── train.py
