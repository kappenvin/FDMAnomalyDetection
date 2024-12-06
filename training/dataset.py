from torch.utils.data import DataLoader, Dataset
from PIL import Image


class DataClass_own_data_faster(Dataset):
    """
    A custom dataset class to load images and corresponding labels from a pandas dataframe.

    Args:
        data (pd.DataFrame): reads in the csv file

        transform (callable):Transform to be applied on an image sample.

    """

    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform
        self.image_paths = data["ImageFilePath"].tolist()
        self.labels = data["Class"].astype(int).tolist()
        self.images = []
        for img_path in self.image_paths:
            img = Image.open(img_path).convert("RGB")
            self.images.append(img)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, label
