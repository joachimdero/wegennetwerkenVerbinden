import arcpy
from log_config import logger


arcpy.env.overwriteOutput = True


def maak_grens_buffer(wegsegmenten_wr, grenslijn):
    # selecteer grenslijn die gebruikt mag worden
    logger.info(f"-maak_grens_buffer:{wegsegmenten_wr, grenslijn}")
    grenslijn_vlawal = "grenslijn_vlawal"
    arcpy.MakeFeatureLayer_management(
        in_features=grenslijn,
        out_layer=grenslijn_vlawal
    )
    arcpy.SelectLayerByLocation_management(
        in_layer=grenslijn_vlawal,
        overlap_type='INTERSECT',
        select_features=wegsegmenten_wr,
        selection_type="NEW_SELECTION"
    )
    grenslijn_vlawal_buffer = "grenslijn_vlawal_buffer5m"
    arcpy.analysis.Buffer(
        in_features=grenslijn_vlawal,
        out_feature_class=grenslijn_vlawal_buffer,
        buffer_distance_or_field="5 Meters",
        line_side="FULL",
        line_end_type="ROUND",
        dissolve_option="NONE",
        dissolve_field=None,
        method="PLANAR"
    )
    logger.info(f"resultaat:{grenslijn_vlawal_buffer}")
    return grenslijn_vlawal_buffer


def maak_wegsegment_buffer_en_wbn(wegsegmenten_wr, grenslijn_vlawal_buffer, wbn):
    logger.info(
        f"-maak_wegsegment_buffer_en_wbn:{wegsegmenten_wr, grenslijn_vlawal_buffer, wbn}")
    wegsegmenten_wr_lyr = "wegsegmenten_wr_lyr"
    arcpy.MakeFeatureLayer_management(
        in_features=wegsegmenten_wr,
        out_layer=wegsegmenten_wr_lyr
    )
    arcpy.SelectLayerByLocation_management(
        in_layer=wegsegmenten_wr_lyr,
        overlap_type="INTERSECT",
        select_features=grenslijn_vlawal_buffer,
        selection_type="NEW_SELECTION"
    )

    wegsegment_wr_buffer = "wegsegment_wr_buffer2m"
    arcpy.analysis.Buffer(
        in_features=wegsegmenten_wr_lyr,
        out_feature_class=wegsegment_wr_buffer,
        buffer_distance_or_field="2 Meters",
        line_side="FULL",
        line_end_type="ROUND",
        dissolve_option="NONE",
        dissolve_field=None,
        method="PLANAR"
    )

    wbn_selectie = "wbn_selectie"
    arcpy.MakeFeatureLayer_management(
        in_features=wbn,
        out_layer=wbn_selectie
    )
    arcpy.SelectLayerByLocation_management(
        in_layer=wbn_selectie,
        overlap_type="INTERSECT",
        select_features=wegsegmenten_wr_lyr,
        selection_type="NEW_SELECTION"
    )
    wbn_dissolve = "wbn_dissolve"
    arcpy.Dissolve_management(
        in_features=wbn_selectie,
        out_feature_class=wbn_dissolve
    )

    logger.info(f"resultaat:{wegsegment_wr_buffer, wbn_selectie}")
    return wegsegment_wr_buffer, wbn_selectie


def maak_selectie_aan_grens(wegsegmenten, grenslijn_vlawal_buffer, wegsegment_wr_buffer,
                            wallonie_manueleSelectie_nietgebruiken, wbn_selectie):
    logger.info(
        f"-MAAK SELECTIE AAN GRENS:{wegsegmenten, grenslijn_vlawal_buffer, wegsegment_wr_buffer, wallonie_manueleSelectie_nietgebruiken}")
    f_selectie = "selectie"
    logger.info(
        f"velden in: {arcpy.Describe(wegsegmenten).catalogPath}, {({f.name for f in arcpy.ListFields(wegsegmenten)})}")
    if f_selectie not in {f.name for f in arcpy.ListFields(wegsegmenten)}:
        logger.info(f"addfield {f_selectie}")
        arcpy.AddField_management(
            in_table=wegsegmenten,
            field_name=f_selectie,
            field_type="TEXT",
            field_length=200
        )
    arcpy.CalculateField_management(
        in_table=wegsegmenten,
        field=f_selectie,
        expression='"test"',
        expression_type="PYTHON3"
    )
    wegsegmenten_lyr = "wegsegmenten_lyr"
    arcpy.MakeFeatureLayer_management(
        in_features=wegsegmenten,
        out_layer=wegsegmenten_lyr
    )
    logger.info(f"{wegsegmenten_lyr}: {arcpy.GetCount_management(wegsegmenten_lyr)[0]} features")
    arcpy.management.SelectLayerByLocation(
        in_layer=wegsegmenten_lyr,
        overlap_type="COMPLETELY_WITHIN",
        select_features=grenslijn_vlawal_buffer,
        search_distance=None,
        selection_type="NEW_SELECTION",
        invert_spatial_relationship="NOT_INVERT"
    )
    logger.info(f"{wegsegmenten_lyr}: {arcpy.GetCount_management(wegsegmenten_lyr)[0]} features geselecteerd van layer {wegsegmenten_lyr} in {grenslijn_vlawal_buffer}")
    wegsegmenten_eerste_selectie_lyr = "wegsegmenten_eerste_selectie_lyr"
    arcpy.MakeFeatureLayer_management(
        in_features=wegsegmenten_lyr,
        out_layer=wegsegmenten_eerste_selectie_lyr
    )
    logger.info(
        f"{wegsegmenten_eerste_selectie_lyr}: {arcpy.GetCount_management(wegsegmenten_eerste_selectie_lyr)[0]} features")

    # eerste volledige selectie
    logger.info(f"eerste volledige selectie")
    arcpy.management.SelectLayerByLocation(
        in_layer=wegsegmenten_eerste_selectie_lyr,
        overlap_type="COMPLETELY_WITHIN",
        select_features=wegsegment_wr_buffer,
        search_distance=None,
        selection_type="NEW_SELECTION",
        invert_spatial_relationship="NOT_INVERT"
    )
    logger.info(
        f"{wegsegmenten_eerste_selectie_lyr}: {arcpy.GetCount_management(wegsegmenten_eerste_selectie_lyr)[0]} features geselecteerd")
    arcpy.CalculateField_management(
        in_table=wegsegmenten_eerste_selectie_lyr,
        field=f_selectie,
        expression='"niet geselecteerd : in grenslijn_vlawal_buffer, in wegsegment_wr_buffer"',
        expression_type="PYTHON3"
    )
    # tweede selectie
    logger.info(f"tweede volledige selectie")
    arcpy.management.SelectLayerByLocation(
        in_layer=wegsegmenten_eerste_selectie_lyr,
        overlap_type="COMPLETELY_WITHIN",
        select_features=wbn_selectie,
        search_distance=None,
        selection_type="NEW_SELECTION",
        invert_spatial_relationship="NOT_INVERT"
    )
    logger.info(
        f"{wegsegmenten_eerste_selectie_lyr}: {arcpy.GetCount_management(wegsegmenten_eerste_selectie_lyr)[0]} features geselecteerd")
    arcpy.CalculateField_management(
        in_table=wegsegmenten_eerste_selectie_lyr,
        field=f_selectie,
        expression="'niet geselecteerd : wbn_selectie'",
        expression_type="PYTHON3"
    )
    # derde selectie: gekende manueel geselecteerde segmenten
    logger.info(f"derde volledige selectie")
    arcpy.management.SelectLayerByLocation(
        in_layer=wegsegmenten_eerste_selectie_lyr,
        overlap_type="SHARE_A_LINE_SEGMENT_WITH",
        select_features=wallonie_manueleSelectie_nietgebruiken,
        search_distance=None,
        selection_type="NEW_SELECTION",
        invert_spatial_relationship="NOT_INVERT"
    )
    logger.info(
        f"{wegsegmenten_eerste_selectie_lyr}: {arcpy.GetCount_management(wegsegmenten_eerste_selectie_lyr)[0]} features geselecteerd")
    arcpy.CalculateField_management(
        in_table=wegsegmenten_eerste_selectie_lyr,
        field=f_selectie,
        expression="'niet geselecteerd : manuele selectie'",
        expression_type="PYTHON3"
    )

    logger.info(f"resultaat:{wegsegmenten}")


def selectie_segmenten_wallonie(ws, wegsegmenten, wegsegmenten_wr, grenslijn, wallonie_manueleSelectie_nietgebruiken,
                                wbn, wegknopenWAL):
    logger.info(f"SELECTIE SEGMENTEN WALLONIE")
    logger.info(f"{arcpy.GetCount_management(wallonie_manueleSelectie_nietgebruiken)[0]} features in {wallonie_manueleSelectie_nietgebruiken}")
    arcpy.env.workspace = ws
    grenslijn_vlawal_buffer = maak_grens_buffer(wegsegmenten_wr, grenslijn)
    wegsegment_wr_buffer, wbn_selectie = maak_wegsegment_buffer_en_wbn(wegsegmenten_wr, grenslijn_vlawal_buffer, wbn)
    maak_selectie_aan_grens(wegsegmenten, grenslijn_vlawal_buffer, wegsegment_wr_buffer,
                            wallonie_manueleSelectie_nietgebruiken, wbn_selectie)
def verwijder_knopen(wegsegmenten, wegknopenWAL):
    f_selectie = "selectie"
    arcpy.AddField_management(
        in_table=wegknopenWAL,
        field_name=f_selectie,
        field_type="TEXT",
        field_length=200
    )
    arcpy.CalculateField_management(
        in_table=wegsegmenten,
        field=f_selectie,
        expression='"test"',
        expression_type="PYTHON3"
    )
    wegsegmenten_selectie = "wegsegmenten_selectie"
    arcpy.MakeFeatureLayer_management(
        in_features=wegsegmenten,
        out_layer=wegsegmenten_selectie,
        where_clause=f"selectie NOT LIKE '%niet geselecteerd%'"
    )
    wegknopenWAL_selectie = "wegknopenWAL_selectie"
    arcpy.MakeFeatureLayer_management(
        in_features=wegknopenWAL,
        out_layer=wegknopenWAL_selectie
    )
    arcpy.SelectLayerByLocation_management(
        in_layer=wegknopenWAL_selectie,
        overlap_type="INTERSECT",
        select_features=wegsegmenten_selectie,
        invert_spatial_relationship="INVERT"
    )
    arcpy.CalculateField_management(
        in_table=wegknopenWAL_selectie,
        field=f_selectie,
        expression="'niet geselecteerd'",
        expression_type="PYTHON3"
    )

# ------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    arcpy.env.workspace = "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten " \
                          "verbinden\\wegennettenVerbinden3.gdb"
    wegsegmenten = "wegsegmentWAL"
    wegknopen = "wegknoopWAL"
    wegsegmenten_wr = "wegsegmentVLA"
    grenslijn = r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\wegennetten verbinden\wegennetten " \
                r"verbinden.gdb\AdmGrensType_gewestgrens"
    wallonie_manueleSelectie_nietgebruiken = r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\wegennetten " \
                                             r"verbinden\wegennettenVerbinden2.gdb\Wallonie_manueleSelectie_nietgebruiken20240708"
    wbn = r"C:\GoogleTeamDrive\GISdata\grb.gdb\Wbn"
    grenslijn_vlawal_buffer = maak_grens_buffer(wegsegmenten_wr, grenslijn)
    wegsegment_wr_buffer, wbn_selectie = maak_wegsegment_buffer_en_wbn(wegsegmenten_wr, grenslijn_vlawal_buffer, wbn)
    maak_selectie_aan_grens(
        wegsegmenten=wegsegmenten,
        grenslijn_vlawal_buffer=grenslijn_vlawal_buffer,
        wegsegment_wr_buffer=wegsegment_wr_buffer,
        wallonie_manueleSelectie_nietgebruiken=wallonie_manueleSelectie_nietgebruiken,
        wbn_selectie=wbn_selectie
    )
    verwijder_knopen(wegsegmenten, wegknopen)
