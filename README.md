graph TD
Root["Project Root"]
Config["config/"]
Src["src/"]
Train["train.py"]

    Root --> Config
    Root --> Src
    Root --> Train

    Config --> DataConfig["data_config.yaml"]
    Config --> ModelConfig["model_config.yaml"]
    Config --> TrainConfig["training_config.yaml"]

    Src --> Data["data/"]
    Src --> Models["models/"]
    Src --> Training["training/"]
    Src --> Utils["utils/"]
    Src --> SrcInit["__init__.py"]

    Data --> DataInit["__init__.py"]
    Data --> Dataset["dataset.py"]
    Data --> Transforms["transforms.py"]

    Models --> ModelsInit["__init__.py"]
    Models --> VitModel["vit_model.py"]

    Training --> TrainingInit["__init__.py"]
    Training --> Trainer["trainer.py"]
    Training --> Optimizer["optimizer.py"]

    Utils --> UtilsInit["__init__.py"]
    Utils --> LoggingUtils["logging_utils.py"]
