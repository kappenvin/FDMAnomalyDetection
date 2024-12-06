from sklearn.model_selection import train_test_split
import pandas as pd
import os


def stratified_part_split_second_train_val_test(
    df, test_size=0.2, val_size=0.25, random_state=42
):
    # Step 1: Group by PartName and get the most common Class for each part
    part_classes = (
        df.groupby("PartName")["Class"]
        .agg(lambda x: x.value_counts().index[0])
        .reset_index()
    )

    # Step 2: Perform stratified split on the grouped data
    train_val, test = train_test_split(
        part_classes,
        test_size=test_size,
        stratify=part_classes["Class"],
        random_state=random_state,
    )
    train, val = train_test_split(
        train_val,
        test_size=val_size,
        stratify=train_val["Class"],
        random_state=random_state,
    )

    # Step 3: Create masks for the original dataframe
    train_mask = df["PartName"].isin(train["PartName"])
    val_mask = df["PartName"].isin(val["PartName"])
    test_mask = df["PartName"].isin(test["PartName"])

    # Step 4: Split the original dataframe
    train_set = df[train_mask]
    val_set = df[val_mask]
    test_set = df[test_mask]

    # Step 5: Print verification information
    print("Train set shape:", train_set.shape)
    print("Validation set shape:", val_set.shape)
    print("Test set shape:", test_set.shape)

    print(
        "\nClass distribution in train set:\n",
        train_set["Class"].value_counts(normalize=False),
    )
    print(
        "\nClass distribution in validation set:\n",
        val_set["Class"].value_counts(normalize=False),
    )
    print(
        "\nClass distribution in test set:\n",
        test_set["Class"].value_counts(normalize=False),
    )

    print("\nNumber of unique PartNames in train set:", train_set["PartName"].nunique())
    print(
        "Number of unique PartNames in validation set:", val_set["PartName"].nunique()
    )
    print("Number of unique PartNames in test set:", test_set["PartName"].nunique())

    return train_set, val_set, test_set


data_path = (
    r"C:\Anomaly_detection_3D_printing\data\csv_files\final_data_(224, 224)_resized.csv"
)

output_path = r"C:\Anomaly_detection_3D_printing\data\csv_files"

if __name__ == "__main__":
    # Load the data
    df = pd.read_csv(data_path)

    # get only the black and white images
    df_gray_black = df.loc[df["Colour"].isin(["black", "gray"])]

    train_set, val_set, test_set = stratified_part_split_second_train_val_test(
        df_gray_black, test_size=0.25, val_size=0.2, random_state=42
    )

    train_set.to_csv(
        os.path.join(output_path, "train_gray_black_resized.csv"),
        index=False,
    )
    val_set.to_csv(
        os.path.join(output_path, "val_gray_black_resized.csv"),
        index=False,
    )
    test_set.to_csv(
        os.path.join(output_path, "test_gray_black_resized.csv"),
        index=False,
    )
