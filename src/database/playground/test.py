import pandas as pd
import cv2

file_path_slicer_settings = (
    r"C:\Anomaly_detection_3D_printing\data\csv_files\Parameter_3D_Druck_neu.xlsx"
)
file_path_images = r"C:\Anomaly_detection_3D_printing\data\csv_files\final_data.csv"
slicer_settings = pd.read_excel(file_path_slicer_settings)
images = pd.read_csv(file_path_images)

print(slicer_settings.head())
print(images.head())

# Simple function to iterate through DataFrame and read images
# Print the column names to check which one contains image paths
print("Images DataFrame columns:", images.columns.tolist())

# Assuming 'Path' or similar column contains image file paths - adjust as needed
image_column = "ImageFilePath"  # Replace with actual column name from your DataFrame

# Simple loop to read images
for idx, row in images.iterrows():
    try:
        # Get image path from DataFrame
        img_path = row[image_column]
        slicer_settings = row["SlicerSettings"]

        # Read image with OpenCV
        img = cv2.imread(img_path)

        # Print basic info about the image
        print(
            f"Image {idx}: {img_path}, Shape: {img.shape if img is not None else 'Failed to load'}"
        )

        # Optional: Do something with the image
        cv2.imshow("Image", img)
        key = cv2.waitKey(0)  # Wait indefinitely until a key is pressed
        if key == ord("q"):  # Check if 'q' key was pressed
            cv2.destroyAllWindows()

    except Exception as e:
        print(f"Error with image {idx}: {e}")

    # Limit to 5 images for testing
    if idx >= 4:
        break

# cv2.destroyAllWindows()  # Uncomment if using imshow
