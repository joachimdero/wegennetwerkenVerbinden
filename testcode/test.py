import arcpy
import os

# Parameters
input_folder = r"D:\\Insync\\Team GIS\\Projecten\\WRapp\\WR verrijkingsapp\\AWVtest\\Test2"
output_gdb = r"D:\\Insync\\Team GIS\\Projecten\\WRapp\\WR verrijkingsapp\\AWVtest\\werkomgeving.gdb"

# Specifieke bestanden waarvoor een kopie zonder 'e' nodig is en de bijbehorende velden
target_files = {
    "eWegsegment.shp": "WS_OIDN, B_WK_OIDN, E_WK_OIDN, MORF, WEGCAT, BEHEER, METHODE, STATUS, LSTRNMID, RSTRNMID, TGBEP",
    "eWegknoop.shp": "WK_OIDN, TYPE",
    "eAttEuropweg.dbf": "EU_OIDN, WS_OIDN, EUNUMMER",
    "eAttGenumweg.dbf": "GW_OIDN, WS_OIDN, IDENT8, RICHTING, VOLGNUMMER",
    "eAttNationweg.dbf": "NW_OIDN, WS_OIDN, IDENT2",
    "eAttRijstroken.dbf": "RS_OIDN, WS_OIDN, AANTAL, RICHTING, VANPOS, TOTPOS",
    "eAttWegbreedte.dbf": "WB_OIDN, WS_OIDN, BREEDTE, VANPOS, TOTPOS",
    "eAttWegverharding.dbf": "WV_OIDN, WS_OIDN, TYPE, VANPOS, TOTPOS",
    "eRltOgkruising.dbf": "OK_OIDN, TYPE, BO_WS_OIDN, ON_WS_OIDN",
}

# Controleer of de input folder bestaat
if not os.path.exists(input_folder):
    print(f"De opgegeven input map bestaat niet: {input_folder}")
else:
    print(f"Input map gevonden: {input_folder}")

# Controleer of de output_gdb bestaat, zo niet, maak een nieuwe
if not arcpy.Exists(output_gdb):
    print(f"GDB bestaat niet, maak een nieuwe aan: {output_gdb}")
    arcpy.CreateFileGDB_management(os.path.dirname(output_gdb), os.path.basename(output_gdb))
else:
    print(f"GDB gevonden: {output_gdb}")


# Functie om een subset van velden te exporteren
def export_subset(input_path, output_path, field_names, is_feature_class):
    # Haal de beschikbare velden op in de shapefile of tabel
    available_fields = [f.name for f in arcpy.ListFields(input_path)]
    print(f"Beschikbare velden in {input_path}: {available_fields}")

    # Controleer of de gevraagde velden bestaan
    fields_to_keep = field_names.split(", ")
    for field in fields_to_keep:
        if field not in available_fields:
            raise ValueError(f"Veld '{field}' bestaat niet in {input_path}")

    # Maak een veldmapping
    field_mappings = arcpy.FieldMappings()
    for field in fields_to_keep:
        field_map = arcpy.FieldMap()
        field_map.addInputField(input_path, field)
        field_mappings.addFieldMap(field_map)

    # Exporteer naar de output_path
    if is_feature_class:
        arcpy.FeatureClassToFeatureClass_conversion(
            input_path, os.path.dirname(output_path), os.path.basename(output_path), field_mapping=field_mappings
        )
    else:
        arcpy.TableToTable_conversion(
            input_path, os.path.dirname(output_path), os.path.basename(output_path), field_mapping=field_mappings
        )


# Loop door alle bestanden in de map en submappen
for root, dirs, files in os.walk(input_folder):
    for file in files:
        file_path = os.path.join(root, file)

        # Controleer of het bestand een shapefile of dbf-bestand is
        if file.lower().endswith(".shp") or file.lower().endswith(".dbf"):
            base_name = os.path.splitext(file)[0]  # Naam zonder extensie

            # 1. Exacte kopie naar de geodatabase
            print(f"Exacte kopie maken van: {file_path}")
            if file.lower().endswith(".shp"):
                # arcpy.FeatureClassToGeodatabase_conversion([file_path], output_gdb)
                arcpy.ExportFeatures_conversion(file_path,os.path.join(output_gdb,base_name))
            else:
                # arcpy.TableToGeodatabase_conversion(file_path, output_gdb)
                arcpy.ExportTable_conversion(file_path,os.path.join(output_gdb,base_name))

            # 2. Kopie zonder 'e' met geselecteerde velden
            if file in target_files:
                # Haal de velden op die overgezet moeten worden
                target_fields = target_files[file]
                new_name = base_name[1:]  # Verwijder de eerste letter 'e'
                new_output = os.path.join(output_gdb, new_name)
                is_feature_class = file.lower().endswith(".shp")

                # Kopie met alleen geselecteerde velden
                print(f"Kopie zonder 'e' van {file_path} met velden: {target_fields}")
                try:
                    export_subset(file_path, new_output, target_fields, is_feature_class)
                except ValueError as e:
                    print(f"Fout bij exporteren van {file_path}: {e}")

print("Exporteren voltooid.")
