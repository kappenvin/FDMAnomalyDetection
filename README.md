## FDM-Nozzle-Camera-Anomaly-Detection

This project focuses on developing an automated system for identifying anomalies in Fused Deposition Modeling (FDM) 3D prints.

**Key aspects:**

- **FDM Anomaly Detection**: Real-time identification of print defects.
- **Nozzle-Mounted Camera**: Utilized for precise image acquisition.
- **Four Distinct Error Types**: Capability to classify between stringing, underextrusion, overextrusion and spaghetti failure.
- **Extensive Dataset**: Trained, validated and tested on 85,000 images.

## Error Types

The system is capable of detecting and classifying four distinct types of 3D printing anomalies:

- **Stringing**: Thin plastic threads that form between separate parts of a print, typically caused by excessive temperature or improper retraction settings.

  <img src="pictures/Bilder_3D_Druck_Fehler_selbst/Stringing_example.jpg" alt="Stringing Example" width="300" height="200">

- **Underextrusion**: Insufficient material flow resulting in gaps, weak layer adhesion, or incomplete infill patterns, often due to clogged nozzles or low flow rates.

  <img src="pictures/Bilder_3D_Druck_Fehler_selbst/underextrusion_example.jpg" alt="Underextrusion Example" width="300" height="200">

- **Overextrusion**: Excessive material flow leading to blob formation, rough surface finish, and dimensional inaccuracies, usually caused by high flow rates or temperature settings.

  <img src="pictures/Bilder_3D_Druck_Fehler_selbst/overextrusion_example.jpg" alt="Overextrusion Example" width="300" height="200">

- **Spaghetti Failure**: Complete print failure where the print detaches from the bed and creates a tangled mess of filament, typically resulting from poor bed adhesion or layer shifting.

  <img src="pictures/Bilder_3D_Druck_Fehler_selbst/spaghetti_example.jpg" alt="Spaghetti Failure Example" width="300" height="200">

## Results

The project evaluates the performance of two models: ResNet50 and ViT-B/16, both trained on the same dataset. The results are presented in terms of accuracy for each class of anomalies, along with confusion matrices to visualize classification performance.

### Resnet50 Model Performance

<table>
<tr>
<td>

| Class          | Accuracy |
| -------------- | -------- |
| Normal         | 0.98     |
| Unterextrusion | 0.55     |
| Überextrusion  | 0.62     |
| Spaghetti      | 0.68     |
| Stringing      | 0.54     |

</td>
<td>
<img src="pictures/results/confusion_matrix_normalized_Resnet50_gray_black.png" alt="ResNet50 Confusion Matrix" width="400" height="300">
</td>
</tr>
</table>

### Vit-B/16 Model Performance

<table>
<tr>
<td>

| Class          | Accuracy |
| -------------- | -------- |
| Normal         | 0.93     |
| Unterextrusion | 0.62     |
| Überextrusion  | 0.74     |
| Spaghetti      | 0.80     |
| Stringing      | 0.65     |

</td>
<td>
<img src="pictures/results/confusion_matrix_normalized_Vit_base_16_Adam_lr_6e-6_black_gray.png" alt="ViT Confusion Matrix" width="400" height="300">
</td>
</tr>
</table>

## Database Structure

The system uses a PostgreSQL database to store image data, slicer settings, and part information. The database consists of three main tables with foreign key relationships.

### Tables Overview

| Table              | Purpose                                   | Primary Key |
| ------------------ | ----------------------------------------- | ----------- |
| **ImageData**      | Stores captured images and metadata       | `id`        |
| **SlicerSettings** | Stores 3D printing parameters             | `id`        |
| **Parts**          | Stores information about 3D printed parts | `id`        |

### Table Relationships

```
Parts  <────  ImageData (N) ────>  SlicerSettings
```

- One **Part** can have many **Images**
- One **SlicerSettings** profile can be used for many **Images**
- Each **Image** belongs to one **Part** and uses one **SlicerSettings** profile

### Table Schemas

#### ImageData

| Column               | Type         | Description                                                        |
| -------------------- | ------------ | ------------------------------------------------------------------ |
| `id`                 | INTEGER (PK) | Auto-increment primary key                                         |
| `image`              | BLOB         | Binary image data                                                  |
| `timestamp`          | DATETIME     | When image was captured                                            |
| `label`              | INTEGER      | Anomaly type (0=Normal, 1=Stringing, 2=Under, 3=Over, 4=Spaghetti) |
| `layer`              | INTEGER      | Print layer number                                                 |
| `parts_id`           | INTEGER (FK) | Foreign key to Parts table                                         |
| `slicer_settings_id` | INTEGER (FK) | Foreign key to SlicerSettings table                                |

#### SlicerSettings

| Column                            | Type         | Description                        |
| --------------------------------- | ------------ | ---------------------------------- |
| `id`                              | INTEGER (PK) | Auto-increment primary key         |
| `slicer_profile`                  | VARCHAR      | Profile name/identifier            |
| `sparse_infill_density`           | INTEGER      | Infill percentage (0-100)          |
| `sparse_infill_pattern`           | VARCHAR      | Infill pattern type                |
| `sparse_infill_speed`             | INTEGER      | Infill print speed (mm/s)          |
| `first_layer_bed_temperature`     | INTEGER      | First layer bed temp (°C)          |
| `bed_temperature_other_layers`    | INTEGER      | Other layers bed temp (°C)         |
| `first_layer_nozzle_temperature`  | INTEGER      | First layer nozzle temp (°C)       |
| `nozzle_temperature_other_layers` | INTEGER      | Other layers nozzle temp (°C)      |
| `travel_speed`                    | INTEGER      | Non-printing movement speed (mm/s) |
| `first_layer_height`              | FLOAT        | First layer height (mm)            |
| `layer_height_other_layers`       | FLOAT        | Standard layer height (mm)         |
| `line_width`                      | FLOAT        | Extrusion line width (mm)          |
| `retraction_length`               | FLOAT        | Filament retraction distance (mm)  |
| `filament_flow_ratio`             | FLOAT        | Flow rate multiplier               |
| `printer_name`                    | VARCHAR      | 3D printer identifier              |

#### Parts

| Column          | Type         | Description                |
| --------------- | ------------ | -------------------------- |
| `id`            | INTEGER (PK) | Auto-increment primary key |
| `name`          | VARCHAR      | Part name/identifier       |
| `url`           | VARCHAR      | Reference URL or file path |
| `general_image` | BLOB         | Representative part image  |
