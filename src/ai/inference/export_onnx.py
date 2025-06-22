# Add the project root to the Python path
import sys

sys.path.append(r"C:\Anomaly_detection_3D_printing")

from src.ai.training.model import ViTLightningModule
import torch
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantType
import os


ckpt_path = r"C:\Anomaly_detection_3D_printing\models\best_accuracy_model_epoch=04-val_accuracy=0.80.ckpt"
output_path = r"C:\Anomaly_detection_3D_printing\models"

model = ViTLightningModule.load_from_checkpoint(ckpt_path)
model.to("cpu")
model.eval()

dummy_input = torch.randn(1, 3, 224, 224)

# Step 2: Define a dummy input
dummy_input = torch.randn(1, 3, 224, 224)

# Step 3: Export to ONNX
onnx_path = os.path.join(output_path, "model.onnx")
torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    export_params=True,
    opset_version=14,
    do_constant_folding=True,
    dynamic_axes={
        "input": {0: "batch_size"},  # Variable batch size
        "output": {0: "batch_size"},  # Variable batch size
    },
    input_names=["input"],
    output_names=["output"],
)
print(f"Model has been successfully exported to {onnx_path}")

# Step 4: Validate the ONNX model
onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)
print("ONNX model is valid!")

# Step 5 (Optional): Quantize the ONNX model
quantized_model_dir = os.path.join(output_path, "quantized_models")
# Ensure directory exists
os.makedirs(quantized_model_dir, exist_ok=True)
quantized_model_path = os.path.join(quantized_model_dir, "model_quantized.onnx")
quantize_dynamic(onnx_path, quantized_model_path, weight_type=QuantType.QInt8)
print(f"Quantized model saved to {quantized_model_path}")
