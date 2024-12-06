import torch
from torchvision import transforms
from PIL import Image
import os
import pandas as pd


def resize_and_save_image_and_change_path_dataframe(
    input_image_path, output_image_path, new_size
):
    # Open the image file
    image = Image.open(input_image_path)

    # Define the transformation: resize
    transform = transforms.Compose(
        [
            transforms.Resize(new_size),  # Resize to new_size
        ]
    )

    # Apply the transformation
    image_resized = transform(image)

    file_name_short = os.path.basename(
        input_image_path
    )  # 2024-07-13_14-06-03layer_1.jpg
    name, _ = os.path.splitext(file_name_short)

    output_path_final = os.path.join(
        output_image_path, name + f"{new_size}_resized.jpg"
    )

    # Save the resized image
    image_resized.save(output_path_final)
    print(f"Image saved to {output_image_path}")
    return output_path_final


df = pd.read_csv(r"C:\Anomaly_detection_3D_printing\data\csv_files\final_data.csv")
df_copy = df.copy()

new_size = (224, 224)

df_copy = df.copy()
output_directory = r"C:\Anomaly_detection_3D_printing\data\Images\resized\224x224"
os.makedirs(output_directory, exist_ok=True)
for index, row in df.iterrows():
    image_path = df.at[index, "ImageFilePath"]
    file_name_short = os.path.basename(image_path)
    output_directory_final = resize_and_save_image_and_change_path_dataframe(
        image_path, output_directory, new_size
    )
    df_copy.at[index, "ImageFilePath"] = output_directory_final

output_directory_csv = r"C:\Anomaly_detection_3D_printing\data\csv_files"
os.makedirs(output_directory_csv, exist_ok=True)

output_path = os.path.join(output_directory_csv, f"final_data_{new_size}_resized.csv")
df_copy.to_csv(
    output_path,
    index=False,
)
