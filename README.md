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

### Entity Relationship Diagram

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│   Parts         │       │   ImageData      │       │ SlicerSettings  │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────┤ parts_id (FK)    │──────►│ id (PK)         │
│ name            │       │ slicer_settings_ │       │ slicer_profile  │
│ url             │       │ id (FK)          │       │ sparse_infill_  │
│ general_image   │       │ id (PK)          │       │ density         │
└─────────────────┘       │ image (BLOB)     │       │ sparse_infill_  │
                          │ timestamp        │       │ pattern         │
                          │ label            │       │ sparse_infill_  │
                          │ layer            │       │ speed           │
                          └──────────────────┘       │ first_layer_bed_│
                                                     │ temperature     │
                                                     │ bed_temperature_│
                                                     │ other_layers    │
                                                     │ first_layer_    │
                                                     │ nozzle_temp     │
                                                     │ nozzle_temp_    │
                                                     │ other_layers    │
                                                     │ travel_speed    │
                                                     │ first_layer_    │
                                                     │ height          │
                                                     │ layer_height_   │
                                                     │ other_layers    │
                                                     │ line_width      │
                                                     │ retraction_     │
                                                     │ length          │
                                                     │ filament_flow_  │
                                                     │ ratio           │
                                                     │ printer_name    │
                                                     └─────────────────┘
```
