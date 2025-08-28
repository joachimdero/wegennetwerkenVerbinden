import os.path
import arcpy
from datetime import datetime
import wegennetwerkWallonieToWrvorm


def maak_grensverbinding(wegknopen_wr, wegknopen_wallonie, wegknopen_brussel, gewestgrens_lijn):
    arcpy.AddMessage(f"{tijd} -maak_grensverbinding:input{wegknopen_wr, wegknopen_wallonie, gewestgrens_lijn}")
    knooplayers = []
    for wegknopen in (wegknopen_wr, wegknopen_wallonie, wegknopen_brussel):
        knooplayer = os.path.basename(wegknopen) + '_lyr'
        knooplayers.append(knooplayer)
        arcpy.AddMessage(f"{tijd} maak layer {knooplayer}")
        arcpy.MakeFeatureLayer_management(
            in_features=wegknopen,
            out_layer=knooplayer
        )
        arcpy.management.SelectLayerByLocation(
            in_layer=knooplayer,
            overlap_type="INTERSECT",
            select_features=gewestgrens_lijn,
            search_distance="3 Meters",
            selection_type="NEW_SELECTION",
            invert_spatial_relationship="NOT_INVERT"
        )
    near_table = f"wegknopen_wr_near_wegknopen_WAL_BRU"
    arcpy.analysis.GenerateNearTable(
        in_features=knooplayers[0],
        near_features=[knooplayers[1], knooplayers[2]],
        out_table=near_table,
        search_radius="5 Meters",
        location="LOCATION",
        angle="NO_ANGLE",
        closest="ALL",
        closest_count=5,
        method="PLANAR",
        distance_unit="Meters"
    )

    near_segment = "wegknopen_wr_nearsegment_WAL_BRU"
    arcpy.management.XYToLine(
        in_table=near_table,
        out_featureclass=near_segment,
        startx_field="FROM_X",
        starty_field="FROM_Y",
        endx_field="NEAR_X",
        endy_field="NEAR_Y",
        line_type="NORMAL_SECTION",
        id_field="IN_FID",
        spatial_reference='PROJCS["Belge_Lambert_1972",GEOGCS["GCS_Belge_1972",DATUM["D_Belge_1972",SPHEROID["International_1924",6378388.0,297.0]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",150000.013],PARAMETER["False_Northing",5400088.438],PARAMETER["Central_Meridian",4.367486666666666],PARAMETER["Standard_Parallel_1",49.8333339],PARAMETER["Standard_Parallel_2",51.16666723333333],PARAMETER["Latitude_Of_Origin",90.0],UNIT["Meter",1.0]];-35872700 -30622700 10000;-971.2418235 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision',
        attributes="ATTRIBUTES"
    )
    grenssegment_layer = arcpy.MakeFeatureLayer_management(
        in_features=near_segment,
        out_layer=near_segment + "_lyr"
    )
    arcpy.management.SelectLayerByLocation(
        in_layer=grenssegment_layer,
        overlap_type="CROSSED_BY_THE_OUTLINE_OF",
        # select_features=near_segment,
        select_features=grenssegment_layer,
        search_distance=None,
        selection_type="NEW_SELECTION",
        invert_spatial_relationship="NOT_INVERT"
    )
    arcpy.DeleteFeatures_management(
        in_features=grenssegment_layer
    )

    grensknopen = "grensknopen"
    arcpy.Merge_management(
        inputs=knooplayers,
        output=grensknopen
    )

    return near_segment, grensknopen


# -----------------------------------
# PAS PATH AAN INDIEN JE IN EEN ANDERE OMGEVING WERKT
arcpy.env.workspace = r"C:\GoogleSharedDrives\Team GIS\Projecten\WRapp\wegennetten verbinden\wegennettenVerbinden.gdb"
# PAS PATH AAN INDIEN JE IN EEN ANDERE OMGEVING WERKT
ws_templates = r"C:\GoogleSharedDrives\Team GIS\Projecten\WRapp\wegennetten verbinden\wegennettenVerbindenTemplates.gdb"
arcpy.env.overwriteOutput = True
tijd = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
wegknopen_wr = "wegknoopVLA"
wegknopen_wallonie = "wegknoopWAL"
wegknopen_bru = "wegknoopBRU"


gewestgrens_lijn = os.path.join(ws_templates, "AdmGrensType_gewestgrens")
template_wegsegmenten = os.path.join(ws_templates, "wegsegment_template")
template_wegknopen = os.path.join(ws_templates, "wegknoop_template")
templates_tables = [
    os.path.join(ws_templates, "AttEuropweg_template"),
    os.path.join(ws_templates, "AttGenumweg_template"),
    os.path.join(ws_templates, "AttNationweg_template"),
    os.path.join(ws_templates, "AttRijstroken_template"),
    os.path.join(ws_templates, "AttWegbreedte_template"),
    os.path.join(ws_templates, "AttWegverharding_template"),
    os.path.join(ws_templates, "RltOgkruising_template")
]
if __name__ == '__main__':
    wegknopenWAL_selectie = "wegknopenWAL_selectie"
    arcpy.MakeFeatureLayer_management(
        in_features=wegknopen_wallonie,
        out_layer=wegknopenWAL_selectie
    )
    near_segment, grensknopen = maak_grensverbinding(
        wegknopen_wr=wegknopen_wr,
        wegknopen_wallonie=wegknopenWAL_selectie,
        wegknopen_brussel=wegknopen_bru,
        gewestgrens_lijn=gewestgrens_lijn
    )

    wegsegmenten_grens = wegennetwerkWallonieToWrvorm.to_wr(
        in_wegsegmenten=near_segment,
        f_wegsegmenten=["SHAPE@"],
        template=template_wegsegmenten,
        templates_tables=templates_tables,
        bron="GRENS"
    )

    wegennetwerkWallonieToWrvorm.set_begin_eind_knoop(
        in_wegsegmenten=wegsegmenten_grens,
        in_wegknopen=grensknopen
    )
