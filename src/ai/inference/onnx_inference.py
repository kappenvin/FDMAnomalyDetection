import numpy as np
from PIL import Image
import onnxruntime as ort
import torch
from torchvision.transforms import v2
import torch.nn.functional as F
import sys
import os 
import time


IMAGE_MEAN = [0.485, 0.456, 0.406]
IMAGE_STD = [0.229, 0.224, 0.225]
IMAGE_SIZE = (224, 224)

# Define the path to the ONNX model

MODEL_PATH = r"/home/vincent/Documents/anomal_detection/models/model.onnx"
IMAGE_PATH= r"/home/vincent/Documents/anomal_detection/data/Images"
image_paths = [os.path.join(IMAGE_PATH, f) for f in os.listdir(IMAGE_PATH) if f.endswith(('.jpg', '.jpeg', '.png'))]



def create_inference_transform(mean: list, std: list, image_size: tuple):
    return v2.Compose(
        [
            v2.Resize(image_size),
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(mean=mean, std=std),
        ]
    )

def get_cpu_temp_sys():
    """Reads the CPU temperature from /sys/class/thermal/thermal_zone0/temp."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_raw = f.read()
        temp_celsius = float(temp_raw) / 1000.0
        return temp_celsius
    except FileNotFoundError:
        return "Error: Temperature file not found. Are you on a Raspberry Pi?"
    except Exception as e:
        return f"An error occurred: {e}"




image_path = r"/home/vincent/Documents/anomal_detection/src/ai/inference/2024-07-12_16-28-42layer_96.jpg"

inference_transform = create_inference_transform(
    mean=IMAGE_MEAN, std=IMAGE_STD, image_size=IMAGE_SIZE
)

# Load the ONNX model

session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
# Get input and output names from the model
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# start time measurement
total_start_time = time.time()

# run loop over images an track the time 
for i in range (5000):
    for image_path in image_paths:

        
        start_time = time.time()
        try:
            pil_image = Image.open(image_path).convert("RGB")
        except FileNotFoundError:
            print(f"Error: Image not found at {image_path}. Skipping.")
            continue
        except Exception as e:
            print(f"Error opening image {image_path}: {e}. Skipping.")
            continue

        transformed_tensor = inference_transform(pil_image)
        input_tensor_for_onnx = transformed_tensor.unsqueeze(0) # Add batch dimension
        onnx_input = input_tensor_for_onnx.numpy()

        # Run inference
        
        outputs = session.run([output_name], {input_name: onnx_input})

        output_tensor = outputs[0]
        predicted_class_index = np.argmax(output_tensor, axis=1)

        end_time = time.time()
        inference_time = end_time - start_time
        print(f"Inference time for {image_path}: {inference_time:.2f} seconds")
        cpu_temperature = get_cpu_temp_sys()
        print(f"CPU Temperature: {cpu_temperature:.2f}°C")
        time.sleep(1)

    total_time = time.time() - total_start_time

    print(f"Total inference time: {total_time:.2f} seconds")

"""
print(f"Running inference with input shape: {onnx_input.shape}")
outputs = session.run([output_name], {input_name: onnx_input})


output_tensor = outputs[0]
predicted_class_index = np.argmax(output_tensor, axis=1)
print(predicted_class_index[0])

logits_tensor = torch.from_numpy(output_tensor)
probabilities_tensor = F.softmax(logits_tensor, dim=1)
probabilities_np = probabilities_tensor.numpy()

print(f"Probabilities: {probabilities_np}")
"""