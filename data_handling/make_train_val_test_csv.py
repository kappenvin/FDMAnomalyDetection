import os
import csv
import numpy as np
import pandas as pd
import pdb


# define the path to the images
data_path = r"C:\Anomaly_detection_3D_printing\data\Images\Prusa"

# define the columns
fieldnames = [
    "ImageFilePath",
    "Class",
    "SlicerSettings",
    "Printer",
    "PartName",
    "Colour",
]


# define the output csv file_name
df = pd.DataFrame(columns=fieldnames)

label_list = []
part_name_list = []
slicer_profile_list = []
printer_list = []
image_path_list = []
colour_list = []


prusa_slicer_settings = os.listdir(data_path)
for slicer in prusa_slicer_settings:
    slicer_path = os.path.join(data_path, slicer)
    if os.path.isdir(slicer_path):
        for colour in os.listdir(slicer_path):
            colour_path = os.path.join(slicer_path, colour)
            if os.path.isdir(colour_path):
                # check if it is a directory
                for part in os.listdir(colour_path):
                    part_path = os.path.join(colour_path, part)
                    if os.path.isdir(part_path):
                        for folder in os.listdir(part_path):
                            print(folder)

                            if folder.lower() in [
                                "good",
                                "underextrusion",
                                "stringing",
                                "spaghetti",
                                "overextrusion",
                            ]:
                                folder_path = os.path.join(part_path, folder)
                                print(folder_path)

                                for image in os.listdir(folder_path):
                                    image_path = os.path.join(folder_path, image)

                                    image_path_list.append(image_path)

                                    path_components = image_path.split(os.sep)

                                    # Extract the required parts
                                    label = path_components[-2]  # 'underextrusion'
                                    label = label.lower()
                                    part_name = path_components[-3]  # 'Extrusion-Test'
                                    colour = path_components[-4]  # 'black'
                                    slicer_profile = path_components[
                                        -5
                                    ]  # 'underextrusion3'
                                    printer = path_components[-6]  # 'Prusa'

                                    if label == "good":
                                        label = 0
                                    elif label == "underextrusion":
                                        label = 1
                                    elif label == "overextrusion":
                                        label = 2
                                    elif label == "spaghetti":
                                        label = 3
                                    elif label == "stringing":
                                        label = 4

                                    label_list.append(label)
                                    part_name_list.append(part_name)
                                    slicer_profile_list.append(slicer_profile)
                                    printer_list.append(printer)
                                    colour_list.append(colour)


label_list = np.array(label_list)
part_name_list = np.array(part_name_list)
slicer_profile_list = np.array(slicer_profile_list)
printer_list = np.array(printer_list)
image_path_list = np.array(image_path_list)
colour_list = np.array(colour_list)

df["ImageFilePath"] = image_path_list
df["Class"] = label_list
df["SlicerSettings"] = slicer_profile_list
df["Printer"] = printer_list
df["PartName"] = part_name_list
df["Colour"] = colour_list


# define the output path for the csv file
output_dir_csv = r"C:\Anomaly_detection_3D_printing\data\csv_files"
os.makedirs(os.path.dirname(output_dir_csv), exist_ok=True)

output_path_csv = os.path.join(output_dir_csv, "final_data.csv")


df.to_csv(output_path_csv, index=False)
