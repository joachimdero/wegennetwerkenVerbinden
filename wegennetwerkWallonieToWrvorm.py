import arcpy
import os
import GeometryLineCalculateM
from Wegknoop import Wegknoop
from log_config import logger

from testcode.test_intersect import intersecttest
from wegsegment_classes import WegWallonie as WegWallonie  # importeren als WegWallonie om compatibiliteit te behouden


def merge_dissolve_wegsegmenten(in_wegsegmenten):
    logger.info(f"-wegenWallonie1: samenvoegen van inputbestanden (per "
          f"provincie) en verbeteringen aanbrengen aan de topologie (onterechte multiparts, wegen die elkaar net niet "
          f"raken,...)")
    logger.info(f"merge inputbestanden: {in_wegsegmenten}")
    wegsegmenten_tmp1: str = "wegsegmentWallonie_tmp1merge"
    arcpy.management.Merge(
        inputs=in_wegsegmenten,
        output=wegsegmenten_tmp1
    )

    # sorteer de data als voorbereiding om segmenten met identieke geometrie tot één feature te brengen
    logger.info("sorteer de data als voorbereiding om segmenten met identieke geometrie tot één feature te brengen")
    wegsegmenten_tmp2 = "wegsegmentWallonie_tmp2sort"
    arcpy.management.Sort(
        in_dataset=wegsegmenten_tmp1,
        out_dataset=wegsegmenten_tmp2,
        sort_field="SENS_BK DESCENDING;COMMU_NOM1 DESCENDING;COMMU_NOM2 DESCENDING;SENS_BK DESCENDING",
        spatial_sort_method="UR"
    )
    arcpy.management.DeleteIdentical(
        in_dataset=wegsegmenten_tmp2,
        fields="Shape",
        xy_tolerance=None,
        z_tolerance=0
    )
    # voer een eerste dissolve uit zonder eerst geometrie te wijzigen
    logger.info("voer een eerste dissolve uit zonder eerst geometrie te wijzigen")
    wegsegmenten_tmp3 = "wegsegmentWallonie_tmp3dissolve"
    arcpy.management.Dissolve(
        in_features=wegsegmenten_tmp2,
        out_feature_class=wegsegmenten_tmp3,
        dissolve_field="GEOREF_ID;NATUR_CODE;NATUR_DESC;CODE_WALTO;ICARRUEID1;RUE_NOM1;COMMU_NOM1;COMMU_INS1;ICARRUEID2;RUE_NOM2;COMMU_NOM2;COMMU_INS2;GESTION;VOIRIE_NOM;SENS_BK;NIVEAU;AMENAG",
        statistics_fields=None,
        multi_part="SINGLE_PART",
        unsplit_lines="DISSOLVE_LINES",
        concatenation_separator=""
    )

    return wegsegmenten_tmp3


def load_data(in_wegsegmenten=[], wegsegmenten_merge="wegsegmentWallonie_tmp1merge"):
    logger.info(f"MERGE INPUTBESTANDEN: {in_wegsegmenten} => {wegsegmenten_merge}")
    arcpy.CreateFeatureclass_management(
        out_path=arcpy.env.workspace,
        out_name=wegsegmenten_merge,
        geometry_type="POLYLINE",
        template=in_wegsegmenten[0],
        has_m="ENABLED",
        has_z="DISABLED",
        spatial_reference='PROJCS["Belge_Lambert_1972",GEOGCS["GCS_Belge_1972",DATUM["D_Belge_1972",SPHEROID["International_1924",6378388.0,297.0]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",150000.013],PARAMETER["False_Northing",5400088.438],PARAMETER["Central_Meridian",4.367486666666666],PARAMETER["Standard_Parallel_1",49.8333339],PARAMETER["Standard_Parallel_2",51.16666723333333],PARAMETER["Latitude_Of_Origin",90.0],UNIT["Meter",1.0]];-35872700 -30622700 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision'
    )
    arcpy.Append_management(
        inputs=in_wegsegmenten,
        target=wegsegmenten_merge
    )
    # sorteer de data als voorbereiding om segmenten met identieke geometrie tot één feature te brengen
    logger.info("sorteer de data als voorbereiding om segmenten met identieke geometrie tot één feature te brengen")
    wegsegmenten_tmp2 = "wegsegmentWallonie_tmp2sort"
    arcpy.management.Sort(
        in_dataset=wegsegmenten_merge,
        out_dataset=wegsegmenten_tmp2,
        sort_field="SENS_BK DESCENDING;COMMU_NOM1 DESCENDING;COMMU_NOM2 DESCENDING;SENS_BK DESCENDING",
        spatial_sort_method="UR"
    )
    arcpy.management.DeleteIdentical(
        in_dataset=wegsegmenten_tmp2,
        fields="Shape",
        xy_tolerance=None,
        z_tolerance=0
    )
    # voer een eerste dissolve uit zonder eerst geometrie te wijzigen
    logger.info("voer een eerste dissolve uit zonder eerst geometrie te wijzigen")
    wegsegmenten_tmp3 = "wegsegmentWallonie_tmp3dissolve"
    arcpy.management.Dissolve(
        in_features=wegsegmenten_tmp2,
        out_feature_class=wegsegmenten_tmp3,
        dissolve_field="GEOREF_ID;NATUR_CODE;NATUR_DESC;CODE_WALTO;ICARRUEID1;RUE_NOM1;COMMU_NOM1;COMMU_INS1"
                       ";ICARRUEID2;RUE_NOM2;COMMU_NOM2;COMMU_INS2;GESTION;VOIRIE_NOM;SENS_BK;NIVEAU;AMENAG",
        statistics_fields=None,
        multi_part="SINGLE_PART",
        unsplit_lines="DISSOLVE_LINES",
        concatenation_separator=""
    )

    return wegsegmenten_tmp3


def generalize_snap_wegsegmenten(in_wegsegmenten):
    logger.info(
        f"-start wegenWallonie2: oplossing segmenten die niet mooi aansluiten (gap of intersectie) en multipart")
    wegsegmenten_tmp4 = "wegsegmentWallonie_tmp4copyGeneralizeSnap"
    arcpy.CopyFeatures_management(
        in_features=in_wegsegmenten,
        out_feature_class=wegsegmenten_tmp4)

    # verwijder het teveel aan vertices (sommigen doen rare zaken in versie 2024) - zorgt dat vertices niet meer op elkaar aansluiten
    # logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}-Generalize")
    # arcpy.edit.Generalize(
    #     in_features=wegsegmenten_tmp4,
    #     tolerance="1 Decimeters"
    # )

    # maak eindpunten, verwijder dubbele of te kort bij mekaar en snap dan de lijnen er naar toe
    logger.info(
        f"-maak eindpunten, verwijder dubbele of te kort bij mekaar en snap dan de lijnen er naar toe")
    featurevertices_tmp1 = "wegsegmentWallonie_tmp4_featureVertices_tmp1"
    arcpy.management.FeatureVerticesToPoints(
        in_features=wegsegmenten_tmp4,
        out_feature_class=featurevertices_tmp1,
        point_location="BOTH_ENDS"
    )
    arcpy.management.DeleteIdentical(
        in_dataset=featurevertices_tmp1,
        fields="Shape",
        xy_tolerance="1 Meters",
        z_tolerance=10000000
    )
    logger.info(f"-snap")
    arcpy.edit.Snap(
        in_features=wegsegmenten_tmp4,
        snap_environment=f"{featurevertices_tmp1} END '1 Meters'"
    )
    # verminder (onterechte) multiparts en maak singleparts
    logger.info(f"-verminder (onterechte) multiparts en maak singleparts")
    wegsegmenten_tmp5 = "wegsegmentWallonie_tmp5dissolve"
    arcpy.management.Dissolve(
        in_features=wegsegmenten_tmp4,
        out_feature_class=wegsegmenten_tmp5,
        dissolve_field="GEOREF_ID;NATUR_CODE;NATUR_DESC;"
                       ";CODE_WALTO;ICARRUEID1;RUE_NOM1;COMMU_NOM1;COMMU_INS1;ICARRUEID2;RUE_NOM2"
                       ";COMMU_NOM2;COMMU_INS2;GESTION;VOIRIE_NOM;SENS_BK;NIVEAU;AMENAG",
        statistics_fields=None,
        multi_part="SINGLE_PART",
        unsplit_lines="DISSOLVE_LINES",
        concatenation_separator=""
    )
    return wegsegmenten_tmp5


def delete_intersectpoints_verschillend_niveau(intersect_fc):
    # delete punten waarbij 1 van de opeenliggende knopen een ander niveau heeft,
    # selfintersects bestaan niet met intersect tools
    points = {}
    with arcpy.da.SearchCursor(intersect_fc, ["SHAPE@", "NIVEAU", "FID_wegsegmentWallonie_tmp6copySnap"]) as sc:
        for row in sc:
            for pnt in row[0]:
                point_coords = (pnt.X, pnt.Y)
            if point_coords not in points:
                points[point_coords] = [row[1]]
            else:
                if row[1] not in points[point_coords]:
                    points[point_coords].append(row[1])

    points_brug = []
    for point in points:
        if len(points[point]) > 1:
            points_brug.append(point)
    logger.info(f"{len(points_brug)} intersection points zijn bruggen en worden verwijderd")

    with arcpy.da.UpdateCursor(intersect_fc, ["SHAPE@"]) as uc:
        for row in uc:
            for pnt in row[0]:
                point_coords = (pnt.X, pnt.Y)
                if point_coords in points_brug:
                    uc.deleteRow()
                    break


def snap_split_wegsegment_at_endpoint(in_wegsegmenten, out_wegsegmenten="wegsegmentWallonie_tmp7SplitAtPoint"):
    logger.info(f"-start snap_split_wegsegment_at_endpoint")
    wegsegmenten_tmp6 = "wegsegmentWallonie_tmp6copySnap"
    logger.info(f"CopyFeatures_management")
    arcpy.CopyFeatures_management(
        in_features=in_wegsegmenten,
        out_feature_class=wegsegmenten_tmp6)

    logger.info(f"FeatureVerticesToPoints")
    endpoints_tmp1 = "wegsegmentWallonie_tmp6_endpoints_tmp1"
    arcpy.management.FeatureVerticesToPoints(
        in_features=wegsegmenten_tmp6,
        out_feature_class=endpoints_tmp1,
        point_location="BOTH_ENDS"
    )
    arcpy.management.DeleteIdentical(
        in_dataset=endpoints_tmp1,
        fields="Shape",
        xy_tolerance="1 Meters",
        z_tolerance=10000000
    )
    logger.info(f"SplitLineAtPoint")
    arcpy.management.SplitLineAtPoint(
        in_features=wegsegmenten_tmp6,
        point_features=endpoints_tmp1,
        out_feature_class=out_wegsegmenten,
        search_radius="0.01 Meters"
    )

    logger.info(f"snap naar eindpunten")
    arcpy.edit.Snap(
        in_features=out_wegsegmenten,
        snap_environment=f"{endpoints_tmp1} END '1 Meters'"
    )

    return out_wegsegmenten


def to_wr(in_wegsegmenten, f_wegsegmenten, template, templates_tables, bron):
    # geef elke lijn wegenregister attributen en kalibratie
    segmenten_wal_wr = f"wegsegment{bron}"
    logger.info(f"{in_wegsegmenten} NAAR WEGENREGISTERVORM {segmenten_wal_wr}")
    nationaleweg = f"AttNationweg{bron}"
    genummerdeweg = f"AttGenumerdeWeg{bron}"
    rijstroken = f"AttRijstroken{bron}"
    wegbreedte = f"AttWegbreedte{bron}"
    wegverharding = f"AttWegverharding{bron}"

    arcpy.CreateFeatureclass_management(
        out_path=arcpy.env.workspace,
        out_name=segmenten_wal_wr,
        geometry_type="POLYLINE",
        template=template,
        has_m="ENABLED",
        has_z="ENABLED",
        spatial_reference=arcpy.Describe(in_wegsegmenten).spatialReference
    )

    logger.info(templates_tables)
    for table in templates_tables:
        arcpy.CreateTable_management(
            out_path=arcpy.env.workspace,
            out_name=f"{os.path.basename(table.split('_')[0])}{bron}",
            template=table
        )

    f_ic_wegsegment = [
        'Shape@', 'WS_OIDN', 'WS_UIDN', 'WS_GIDN', 'STATUS', 'LBLSTATUS', 'MORF', 'LBLMORF', 'WEGCAT', 'LBLWEGCAT',
        'LSTRNMID', 'LSTRNM', 'RSTRNMID', 'RSTRNM', 'BEHEER', 'LBLBEHEER', 'METHODE', 'LBLMETHOD', 'OPNDATUM',
        'BEGINTIJD', 'BEGINORG', 'LBLBGNORG', 'TGBEP', 'LBLTGBEP', 'legende', 'bron'
    ]
    f_ic_nationaleweg = [
        'NW_OIDN', 'WS_OIDN', 'IDENT2', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG'
    ]
    f_ic_genummerdeweg = [
        'GW_OIDN', 'WS_OIDN', 'IDENT8', 'RICHTING', "LBLRICHTING", "VOLGORDE",'BEGINTIJD', 'BEGINORG', 'LBLBGNORG'
    ]
    f_ic_rijstroken = [
        'RS_OIDN', 'WS_OIDN', 'WS_GIDN', 'AANTAL', 'RICHTING', 'LBLRICHT',
        'VANPOS', 'TOTPOS', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG'
    ]
    f_ic_wegbreedte = [
        'WB_OIDN', 'WS_OIDN', 'WS_GIDN', 'BREEDTE',
        'VANPOS', 'TOTPOS', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG'
    ]
    f_ic_wegverharding = [
        'WV_OIDN', 'WS_OIDN', 'WS_GIDN', 'TYPE', 'LBLTYPE',
        'VANPOS', 'TOTPOS', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG'
    ]

    with arcpy.da.Editor(arcpy.env.workspace) as edit:
        ic_wegsegment = arcpy.da.InsertCursor(segmenten_wal_wr, f_ic_wegsegment)
        ic_nationaleweg = arcpy.da.InsertCursor(nationaleweg, f_ic_nationaleweg)
        ic_genummerdeweg = arcpy.da.InsertCursor(nationaleweg, f_ic_genummerdeweg)
        ic_rijstroken = arcpy.da.InsertCursor(rijstroken, f_ic_rijstroken)
        ic_wegbreedte = arcpy.da.InsertCursor(wegbreedte, f_ic_wegbreedte)
        ic_wegverharding = arcpy.da.InsertCursor(wegverharding, f_ic_wegverharding)

        logger.info(f"aantal features in {in_wegsegmenten}: {arcpy.GetCount_management(in_wegsegmenten).getOutput(0)}")
        with arcpy.da.SearchCursor(in_wegsegmenten, f_wegsegmenten) as sc:
            fouten = []
            for i, row in enumerate(sc):
                fout = []
                if i % 10000 == 0 or i < 5:
                    logger.info(f"{i} wegsegmenten omgezet, {len(fouten)} konden niet verwerkt worden")
                if row[0] is None:
                    fout.append(f"ongeldige geometrie (None): {row}")
                    fouten.append(fout)
                elif row[0].getLength() == 0:
                    fout.append(f"ongeldige geometrie (lengte 0): {row}")
                    fouten.append(fout)
                elif row[0].firstPoint.equals(row[0].lastPoint):
                    fout.append(f"ongeldige geometrie (beginpunt = eindpunt): {row}")
                    fouten.append(fout)
                else:
                    geometry_wr = GeometryLineCalculateM.PolylineWithMValues(row[0]).out_geometry
                    row_tmp = [geometry_wr] + list(row[1:])
                    weg = WegWallonie(
                        geometrie=row[0],
                        nature_desc=row[1],
                        icarrueid1=row[2],
                        rue_nom1=row[3],
                        commu_nom1=row[4],
                        commu_ins1=row[5],
                        icarrueid2=row[6],
                        rue_nom2=row[7],
                        commu_nom2=row[8],
                        commu_ins2=row[9],
                        gestion=row[10],
                        voirie_nom=row[11],
                        sens_bk=row[12],
                        amenag=row[13],
                        bron=bron
                    )
                    row_new = weg.export_wegsegment_as_list()
                    ic_wegsegment.insertRow(row_new)
                    row_nationweg = weg.export_nationweg_as_list()
                    row_genumweg = weg.export_genummerdeweg_as_list()
                    row_rijstroken = weg.export_rijstroken_as_list()
                    row_wegbreedte = weg.export_wegbreedte_as_list()
                    row_wegverharding = weg.export_wegverharding_as_list()
                    if row_nationweg[2] is not None:
                        ic_nationaleweg.insertRow(row_nationweg)
                        ic_genummerdeweg.insertRow(row_genumweg)
                    ic_rijstroken.insertRow(row_rijstroken)
                    ic_wegbreedte.insertRow(row_wegbreedte)
                    ic_wegverharding.insertRow(row_wegverharding)
            logger.info(f"{i} wegsegmenten omgezet, {len(fouten)} konden niet verwerkt worden")

    if len(fouten) > 0:
        logger.info(f"er konden {len(fouten)} niet verwerkt worden: eerste 10: {fouten[:10]}")

    logger.info(f"wegsegment_tmp7: {segmenten_wal_wr}, {arcpy.Describe(segmenten_wal_wr).dataType}")
    return segmenten_wal_wr


def maak_knopen(in_wegsegmenten, template, bron):
    logger.info(f"MAAK KNOPEN")
    wegknopen_tmp1 = f"wegknoop{bron}_tmp1"
    arcpy.management.FeatureVerticesToPoints(
        in_features=in_wegsegmenten,
        out_feature_class=wegknopen_tmp1,
        point_location="BOTH_ENDS"
    )
    # maak lijst van knopen die uniek zijn in ligging, met de wegen die er op aansluiten
    knopen = {}
    with arcpy.da.SearchCursor(wegknopen_tmp1, ["SHAPE@XY", "WS_OIDN"]) as sc:
        for row in sc:
            if row[0] not in knopen:
                knopen[row[0]] = [row[1]]
            else:
                knopen[row[0]].append(row[1])

    wegknopen_tmp2 = f"wegknoop{bron}"
    arcpy.CreateFeatureclass_management(
        out_path=arcpy.env.workspace,
        out_name=wegknopen_tmp2,
        geometry_type="POINT",
        template=template,
        spatial_reference=arcpy.Describe(template).spatialReference
    )
    f_ic = ['Shape@XY', 'WK_OIDN', 'WK_UIDN', 'TYPE', 'LBLTYPE', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG']
    with arcpy.da.InsertCursor(wegknopen_tmp2, f_ic) as ic:
        for k, v in knopen.items():
            row_new = Wegknoop(k, v, bron="BRU").export_attr_as_list()
            ic.insertRow(row_new)

    return wegknopen_tmp2


def set_begin_eind_knoop(in_wegsegmenten, in_wegknopen):
    logger.info(f"-set_begin_eind_knoop")
    # Maak verwijzing naar begin- en eindknoop
    knoop = {}
    with arcpy.da.SearchCursor(in_wegknopen, ['SHAPE@', 'WK_OIDN']) as sc:
        for k in sc:
            xy = f'{round(k[0][0].X, 3)},{round(k[0][0].Y, 3)}'
            knoop[xy] = k[1]

    # vul begin- en eindknoop in
    with arcpy.da.UpdateCursor(in_wegsegmenten, ['SHAPE@', 'B_WK_OIDN', 'E_WK_OIDN']) as uc:
        fouten_set_begin_eind_knoop = []
        for row in uc:
            try:
                multiline = row[0]
                line = multiline[0]
                b_punt = f'{round(line[0].X, 3)},{round(line[0].Y, 3)}'
                e_punt = f'{round(line[-1].X, 3)},{round(line[-1].Y, 3)}'
                row[1] = knoop[b_punt]
                row[2] = knoop[e_punt]
                uc.updateRow(row)
            except Exception as e:
                fout_set_begin_eind_knoop = []
                if row[0] is None:
                    fout_set_begin_eind_knoop.append(f"ongeldige geometrie: {row}")
                else:
                    fout_set_begin_eind_knoop.append(f"andere fout: {row}")

                fouten_set_begin_eind_knoop.append(f"Error processing row {row}: {e}, table:{in_wegsegmenten}")
    if len(fouten_set_begin_eind_knoop) > 0:
        logger.info(
            f"er konden {len(fouten_set_begin_eind_knoop)} niet verwerkt worden: eerste 10: {fouten_set_begin_eind_knoop[:10]}")
