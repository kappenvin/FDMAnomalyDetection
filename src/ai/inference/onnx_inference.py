"""
Script to load and run a quantized ONNX model for anomaly detection in 3D printing images.

This script:
1. Loads a quantized ONNX model
2. Preprocesses input images
3. Runs inference on the model
4. Interprets and returns the results

Usage:
    python run_onnx.py --image_path path/to/image.jpg
    python run_onnx.py --folder_path path/to/images/folder
"""

import numpy as np
from PIL import Image
import onnxruntime as ort
import torch
from torchvision.transforms import v2
from PIL import Image
import torch.nn.functional as F


IMAGE_MEAN = [0.485, 0.456, 0.406]
IMAGE_STD = [0.229, 0.224, 0.225]
IMAGE_SIZE = (224, 224)

# Define the path to the ONNX model

MODEL_PATH = r"C:\Anomaly_detection_3D_printing\models\model.onnx"


def create_inference_transform(mean: list, std: list, image_size: tuple):
    return v2.Compose(
        [
            v2.Resize(image_size),
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(mean=mean, std=std),
        ]
    )


image_path = r"C:\Anomaly_detection_3D_printing\data\Images\Prusa\underextrusion10\black\Supporttest2676295\spaghetti\2024-07-12_16-28-40layer_96.jpg"

inference_transform = create_inference_transform(
    mean=IMAGE_MEAN, std=IMAGE_STD, image_size=IMAGE_SIZE
)

pil_image = Image.open(image_path).convert("RGB")

transformed_tensor = inference_transform(pil_image)

input_tensor_for_onnx = transformed_tensor.unsqueeze(0)

onnx_input = input_tensor_for_onnx.numpy()
# Load the ONNX model

session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])

# Get input and output names
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name


print(f"Running inference with input shape: {onnx_input.shape}")
outputs = session.run([output_name], {input_name: onnx_input})


output_tensor = outputs[0]
predicted_class_index = np.argmax(output_tensor, axis=1)
print(predicted_class_index[0])

logits_tensor = torch.from_numpy(output_tensor)
probabilities_tensor = F.softmax(logits_tensor, dim=1)
probabilities_np = probabilities_tensor.numpy()

print(f"Probabilities: {probabilities_np}")
