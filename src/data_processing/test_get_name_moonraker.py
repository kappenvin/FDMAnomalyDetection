from Klipper_class import KlipperPrinter

url = "http://192.168.2.170/"
printer = KlipperPrinter(url)

test_string = (
    " Kamerahalterung_Pizero v4_0.2mm_PLA_Generic Klipper Printer_22m13s.gcode"
)
# extract for orcaslicer
# Split the string by the first underscore occurrence
parts = test_string.split("_0", 1)

# Output the results
print(f"Partname: {parts[0]}")
