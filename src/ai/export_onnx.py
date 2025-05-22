from training.model import ViTLightningModule
import torch
import torch
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantType



ckpt_path = r'C:\Anomaly_detection_3D_printing\mlartifacts\708455617614171859\dd52127e64554a6b9779154f2f912e44\artifacts\model\checkpoints\epoch=1-step=4\epoch=1-step=4.ckpt'

model = ViTLightningModule.load_from_checkpoint(ckpt_path)
model.to("cpu")
model.eval()

dummy_input = torch.randn(1, 3, 224, 224)

# Step 2: Define a dummy input
dummy_input = torch.randn(1, 3, 224, 224)

# Step 3: Export to ONNX
onnx_path = "model.onnx"
torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    opset_version=14,
    input_names=["input"],
    output_names=["output"],
)
print(f"Model has been successfully exported to {onnx_path}")

# Step 4: Validate the ONNX model
onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)
print("ONNX model is valid!")

# Step 5 (Optional): Quantize the ONNX model
quantized_model_path = "model_quantized.onnx"
quantize_dynamic(
    onnx_path,
    quantized_model_path,
    weight_type=QuantType.QInt8
)
print(f"Quantized model saved to {quantized_model_path}")