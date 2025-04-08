from database import db, Session, Base
from models import ImageData, SlicerSettings, Parts
from crud import get_image_data_by_column_value, delete_image_data_by_id
from schema_management import add_column_to_table


def main() -> None:
    # Create all tables if they don't exist
    Base.metadata.create_all(db)

    # Ensure required columns exist
    # add_column_to_table("layer", "INTEGER")

    # Create test data
    test_image_data = ImageData(
        slicer_settings_id=1, parts_id=1, label=1, layer=1, image=b"test"
    )
    test_slicer_settings = SlicerSettings(
        sparse_infill_density=100,
        sparse_infill_pattern="rectangular",
        sparse_infill_speed=100,
        first_layer_bed_temperature=100,
        bed_temperature_other_layers=100,
        first_layer_nozzle_temperature=100,
        nozzle_temperature_other_layers=100,
        travel_speed=100,
        first_layer_heigtht=100,
        layer_height_other_layers=100,
        line_width=100,
        retraction_lenght=100,
        filament_flow_ratio=100,
        printer="test",
    )
    test_parts = Parts(name="test", url="test", general_image=b"test")

    with Session() as session:
        session.add(test_image_data)
        session.add(test_slicer_settings)
        session.add(test_parts)
        session.commit()

        # Test query
        results = get_image_data_by_column_value(session, "label", 1)
        print(f"Found {len(results)} records with label=1:")
        for record in results:
            print(record)


if __name__ == "__main__":
    main()
