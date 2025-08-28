import os
import sys
from datetime import datetime

import arcpy

from wegennetwerkWallonieToWrvorm import set_begin_eind_knoop


def maak_gebied(wbn, knw, vlaanderen):
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -maak_gebied")
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} merge")
    merge = "wbn_knw_vlaanderen_tmp1merge"
    arcpy.Merge_management(
        inputs=[wbn, knw, vlaanderen],
        output=merge
    )
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} dissolve")
    gebied = "wbn_knw_vlaanderen_resultaat"
    arcpy.Dissolve_management(
        in_features=merge,
        out_feature_class=gebied
    )
    return gebied


def selectie_wegsegment_en_knopen(wegsegmenten, wegknopen, vlaanderen):
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -maak selectie van wegsegmenten waarbij de "
                     f"wegknoop buiten Vlaanderen ligt")
    vlaanderen_buffer = "vlaanderen_buffer_5m"
    arcpy.AddMessage(f"maak buffer rond vlaanderen: {vlaanderen_buffer}")
    arcpy.analysis.Buffer(
        in_features=vlaanderen,
        out_feature_class=vlaanderen_buffer,
        buffer_distance_or_field="5 Meters",
        line_side="FULL",
        line_end_type="ROUND",
        dissolve_option="ALL",
        dissolve_field=None,
        method="PLANAR"
    )
    arcpy.AddMessage(f"selecteer wegknopen buiten vlaanderen (buffer): inputfc: {wegknopen}")
    # wegknopen buiten vlaanderen
    wegknopen_lyr = "wegknopen_buitenVlaanderen_lyr"
    arcpy.MakeFeatureLayer_management(
        in_features=wegknopen,
        out_layer=wegknopen_lyr
    )
    arcpy.SelectLayerByLocation_management(
        in_layer=wegknopen_lyr,
        overlap_type="WITHIN_CLEMENTINI",
        select_features=vlaanderen_buffer,
        selection_type="NEW_SELECTION",
        invert_spatial_relationship="INVERT"
    )
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {arcpy.GetCount_management(wegknopen_lyr)[0]} "
                     f"wegknopen buiten Vlaanderen, totaal aantal knopen:{arcpy.GetCount_management(wegknopen)[0]}")
    wkoidn_uit_vlaanderen = {int(row[0]) for row in arcpy.da.SearchCursor(wegknopen_lyr, "WK_OIDN")}
    # arcpy.AddMessage(f"{len(wkoidn_uit_vlaanderen)}knopen_uit_vlaanderen: {str(wkoidn_uit_vlaanderen)[:500]}")
    arcpy.ExportFeatures_conversion(
        in_features=wegknopen_lyr,
        out_features=f"{wegknopen}_tmp1uit_vlaanderen"
    )

    # selectie wegsegmenten met beginknoop uit vlaanderen
    wsoidn_uit_vlaanderen_b = {row[0] for row in
                               arcpy.da.SearchCursor(wegsegmenten, ["WS_OIDN", "B_WK_OIDN"])
                               if row[1] in wkoidn_uit_vlaanderen}

    wsoidn_uit_vlaanderen_e = {row[0] for row in
                               arcpy.da.SearchCursor(wegsegmenten, ["WS_OIDN", "E_WK_OIDN"])
                               if row[1] in wkoidn_uit_vlaanderen}

    wegsegment_te_splitsen_fc = f"{os.path.basename(wegsegmenten)}_tmp1TeSplitsen"
    wsoidn_te_splitsen = tuple(set(wsoidn_uit_vlaanderen_b.union(wsoidn_uit_vlaanderen_e)))
    if len(wsoidn_te_splitsen) > 0:
        where_clause = f"WS_OIDN IN {wsoidn_te_splitsen}"
        # arcpy.AddMessage(f"where_clause: {where_clause}")
        arcpy.ExportFeatures_conversion(
            in_features=wegsegmenten,
            out_features=wegsegment_te_splitsen_fc,
            where_clause=where_clause
        )
        arcpy.AddMessage(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {arcpy.GetCount_management(wegsegment_te_splitsen_fc)[0]} "
            f"wegsegmenten te splitsen ({wegsegment_te_splitsen_fc})")
    else:
        arcpy.AddMessage("geen wegsegmenten te splitsen")
        sys.exit()

    return wsoidn_uit_vlaanderen_b, wsoidn_uit_vlaanderen_e, wegsegment_te_splitsen_fc, wegknopen_lyr


def splits_segmenten(wegsegmenten, vlaanderen, wsoidn_uit_vlaanderen_b, wsoidn_uit_vlaanderen_e,
                     wegsegment_te_splitsen_fc, knopen_uit_vlaanderen):
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -split segmenten die deels buiten vlaanderen "
                     f"liggen")
    arcpy.AddMessage(f"maak knopen")
    knopen = ("beginknoop_nieuw_tmp1", "eindknoop_nieuw_tmp2")
    f_knopen = {"beginknoop_nieuw_tmp1": "!B_WK_OIDN!", "eindknoop_nieuw_tmp2": "!E_WK_OIDN!"}

    for s, k in zip((wsoidn_uit_vlaanderen_b, wsoidn_uit_vlaanderen_e), knopen):
        if len(s) == 0:
            arcpy.AddMessage(f"geen segmenten in {k}")
            arcpy.CreateFeatureclass_management(
                out_path=arcpy.env.workspace,
                out_name=k,
                geometry_type="MULTIPOINT"
            )
            break
        elif len(s) == 1:
            print(s)
            print(type(s))
            s = f"({tuple(s)[0]})"
        else:
            s = tuple(s)

        wegsegment_selectie_lyr = "wegsegment_lyr"
        # arcpy.AddMessage(f'where_clause=f"WS_OIDN  IN {s}"')
        arcpy.MakeFeatureLayer_management(
            in_features=wegsegment_te_splitsen_fc,
            out_layer=wegsegment_selectie_lyr,
            where_clause=f"WS_OIDN  IN {s}"
        )
        # maak nieuwe knopen
        arcpy.AddMessage(f"intersect: in{wegsegment_selectie_lyr},{vlaanderen}, out:{k}")
        arcpy.analysis.Intersect(
            in_features=[wegsegment_selectie_lyr, vlaanderen],
            out_feature_class=k,
            join_attributes="ALL",
            cluster_tolerance=None,
            output_type="POINT"
        )

        arcpy.CalculateField_management(
            in_table=k,
            field="WK_OIDN",
            field_type="LONG",
            expression=f_knopen[k],
        )
    wegknopen_merge = "wegknoop_tmp3verplaatstMerge"
    arcpy.Merge_management(
        inputs=list(knopen),
        output=wegknopen_merge
    )
    wegknopen_verplaatst = "wegknoop_tmp4singlepart"
    arcpy.MultipartToSinglepart_management(
        in_features=wegknopen_merge,
        out_feature_class=wegknopen_verplaatst
    )

    # split
    wegsegmenten_split = f"{wegsegmenten}_tmp2split"
    arcpy.management.SplitLineAtPoint(
        in_features=wegsegment_te_splitsen_fc,
        point_features=wegknopen_verplaatst,
        out_feature_class=wegsegmenten_split,
        search_radius="0.01 Meters"
    )
    wegsegmenten_split_lyr = "wegsegmenten_split_lyr"
    arcpy.MakeFeatureLayer_management(
        in_features=wegsegmenten_split,
        out_layer=wegsegmenten_split_lyr
    )

    arcpy.SelectLayerByLocation_management(
        in_layer=wegsegmenten_split_lyr,
        overlap_type="INTERSECT",
        select_features=knopen_uit_vlaanderen,
        selection_type="NEW_SELECTION"
    )
    wegsegmenten_split_verwijderen = f"{wegsegmenten}_tmp3teverwijderensegmentdelen"
    arcpy.ExportFeatures_conversion(
        in_features=wegsegmenten_split_lyr,
        out_features=wegsegmenten_split_verwijderen
    )
    return wegsegmenten_split_verwijderen, wegknopen_verplaatst


def maak_nieuwe_fc_segmenten(wegsegmenten, wegsegmenten_split_verwijderen,wegknopen_verplaatst):
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -maak_nieuwe_fc_segmenten")
    # verwijder wegsegment(delen)
    segmenten_resultaat = f"wegsegmentVLA"
    arcpy.Erase_analysis(
        in_features=wegsegmenten,
        erase_features=wegsegmenten_split_verwijderen,
        out_feature_class=segmenten_resultaat
    )

    arcpy.AddMessage(f"segmenten_resultaat = {segmenten_resultaat}")
    wegsegmenten_ingeschetst_lyr = "wegsegmenten_ingeschetst_lyr"
    arcpy.MakeFeatureLayer_management(
        in_features=segmenten_resultaat,
        out_layer=wegsegmenten_ingeschetst_lyr,
        where_clause="LBLMETHOD = 'ingeschetst'"
    )
    arcpy.DeleteFeatures_management(
        in_features=wegsegmenten_ingeschetst_lyr
    )
    # verwijder 0m-segmenten
    segmenten_0mselectie = arcpy.MakeFeatureLayer_management(
        in_features=segmenten_resultaat,
        out_layer="segmenten_0mselectie",
        where_clause="Shape_Length = 0"
    )

    print(f"segmenten_0mselectie: aantal: {arcpy.GetCount_management(in_rows=segmenten_0mselectie).getOutput(0)}")
    arcpy.DeleteFeatures_management(
        in_features=segmenten_0mselectie
    )

    arcpy.CalculateField_management(
        in_table=wegsegmenten,
        field="bron",
        expression="'VLA'",
        expression_type="PYTHON3",
        field_type="TEXT"
    )
    arcpy.management.CalculateField(
        in_table=wegsegmenten,
        field="legende",
        expression="Legende(!LBLMORF!,!WEGCAT!,!BEHEER!,!LBLSTATUS!)",
        expression_type="PYTHON3",
        code_block="""def Legende(morf, wegcat, beheer, status):
        legende = 8
        if morf == 'dienstweg' :
            legende = 8
        elif status == 'in aanbouw' :
            legende = 14
        elif morf == 'in- of uitrit van een dienst':
            legende = 8        
        elif morf == 'tramweg, niet toegankelijk voor andere voertuigen':
            legende = 12
        elif morf == 'veer':
            legende = 12        
        elif morf == 'aardeweg':
            legende = 10
        elif morf == 'wandel- of fietsweg, niet toegankelijk voor andere voertuigen':
            legende = 9
        elif wegcat == 'L3' :
            legende = 8
        elif wegcat == 'L2':
            legende = 7
        elif wegcat == 'L1' and not 'AWV' in beheer:
            legende = 6        
        elif wegcat == 'L1' and 'AWV' in beheer:
            legende = 5
        elif 'S' in wegcat :
            legende = 4
        elif 'P' in wegcat :
            legende = 3
        elif wegcat == 'H' :
            legende = 1
        return legende""",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )

    return segmenten_resultaat


def verplaats_knopen(wegknopen_resultaat, f_c, knopen_nieuw_geo):
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -verplaats_knopen")
    with arcpy.da.UpdateCursor(wegknopen_resultaat, f_c) as uc:
        for row in uc:
            if row[0] in knopen_nieuw_geo:
                geometry_multipoint_new = knopen_nieuw_geo[row[0]]
                if geometry_multipoint_new.partCount != 1:
                    arcpy.AddError(f"FOUT MULTIPOINT: {geometry_multipoint_new[:]}, row: {row}")
                geometry_firstpoint_new = geometry_multipoint_new[0]
                geometry_firstpoint_new = arcpy.Point(geometry_firstpoint_new.X, geometry_firstpoint_new.Y)
                row_new = [row[0], geometry_firstpoint_new]
                uc.updateRow(row_new)

    arcpy.AddMessage(f"wegknopen_resultaat: {wegknopen_resultaat}")


def voeg_knopen_toe(wegknopen_resultaat: object, knopen_duplicate: dict) -> object:
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -voeg_knopen_toe")
    # f_c = ["WK_OIDN", "SHAPE@", "TYPE", "LBLTYPE"]
    f_c = ["WK_OIDN", "SHAPE@", "TYPE", "LBLTYPE", 'WK_UIDN', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG']
    i = 0
    with arcpy.da.InsertCursor(wegknopen_resultaat, f_c) as ic:
        for knopen in knopen_duplicate:
            for knoop in knopen_duplicate[knopen]:
                # if i <10:
                #     print(f"knoop:{knoop}")
                i += 1
                # wkoidn = knopen_duplicate[knoop][0]
                wkoidn = knoop[0]
                wkuidn = str(wkoidn)+"_1"
                begintijd = "19500101T000000"
                beginorg = "AWV"
                lblbgnorg = "AWV"
                geometry = knoop[1]
                row_new = [wkoidn, geometry, 1, "echte knoop",wkuidn,begintijd,beginorg,lblbgnorg]
                # arcpy.AddMessage(f"row_new:{row_new}")
                ic.insertRow(row_new)
    arcpy.AddMessage(f"{i} knopen toegevoegd")


def maak_nieuwe_fc_knopen(wegknopen, knopen_nieuw, wegsegmenten_split_verwijderen):
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -maak_nieuwe_fc_knopen")
    wegknopen_resultaat = f"wegknoopVLA"
    arcpy.ExportFeatures_conversion(
        in_features=wegknopen,
        out_features=wegknopen_resultaat
    )
    # maak layer met nieuwe wegknopen die grenzen aan een verwijderd wegsegmentdeel
    knopen_nieuw_selectie = "wegknoop_verplaatst_tmp4singlepart_lyr"
    arcpy.MakeFeatureLayer_management(
        in_features=knopen_nieuw,
        out_layer=knopen_nieuw_selectie
    )
    arcpy.SelectLayerByLocation_management(
        in_layer=knopen_nieuw_selectie,
        overlap_type="BOUNDARY_TOUCHES",
        select_features=wegsegmenten_split_verwijderen,
        selection_type="NEW_SELECTION"
    )
    arcpy.ExportFeatures_conversion(
        in_features=knopen_nieuw_selectie,
        out_features="wegknoop_verplaatst_tmp5boundarytouches"
    )

    # maak WK_OIDN uniek (oorspronkelijk punt kan gesnapt zijn naar meerdere afgeknipte segmenten)
    f_c = ["WK_OIDN", "SHAPE@"]
    knopen_nieuw_geo = {}  # ["WK_OIDN", "SHAPE@"]
    knopen_duplicate = {}  # oospronkelijk WK_OIDN, nieuw WK_OIDN
    wk_oidn_nieuw = 100000000
    with arcpy.da.SearchCursor(knopen_nieuw_selectie, f_c) as sc:
        for row in sc:
            if row[0] in knopen_nieuw_geo:
                if row[0] in knopen_duplicate:
                    knopen_duplicate[row[0]].append([wk_oidn_nieuw, row[1]])
                else:
                    knopen_duplicate[row[0]] = [[wk_oidn_nieuw, row[1]]]
                # knopen_nieuw_geo[wk_oidn_nieuw] = row[1]
                wk_oidn_nieuw += 1
            else:
                knopen_nieuw_geo[row[0]] = row[1]
    arcpy.AddMessage(f"knopen_duplicate:{knopen_duplicate}")

    # knopen_nieuw_geo = {row[0]: row[1] for row in arcpy.da.SearchCursor(knopen_nieuw_selectie, f_c)}
    verplaats_knopen(wegknopen_resultaat, f_c, knopen_nieuw_geo)
    voeg_knopen_toe(wegknopen_resultaat, knopen_duplicate)

    return wegknopen_resultaat, knopen_duplicate


def test_wegknopen(wegknopen, wegsegmenten):
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -test_wegknopen")
    # controle worden alle knopen gebruikt, bestaan alle knopen
    wegknopen_wkoidn = [row[0] for row in arcpy.da.SearchCursor(wegknopen, "WK_OIDN")]
    wegsegment_wkoidn = {value for row in arcpy.da.SearchCursor(wegsegmenten, ["B_WK_OIDN", "E_WK_OIDN"]) for value in
                         row}
    enkele_knopen, dubbele_knopen, niet_gebruikte_knopen = set(), set(), set()
    for v in wegknopen_wkoidn:
        if v not in enkele_knopen:
            enkele_knopen.add(v)
        else:
            dubbele_knopen.add(v)
        if v not in wegsegment_wkoidn:
            niet_gebruikte_knopen.add(v)
    arcpy.AddMessage(f"{len(dubbele_knopen)} dubbele knopen,: eerste 100: {list(dubbele_knopen)[:100]}")
    arcpy.AddMessage(
        f"{len(niet_gebruikte_knopen)} niet gebruikte knopen,: eerste 100: {list(niet_gebruikte_knopen)[:100]}")

    niet_bestaande_knopen = wegsegment_wkoidn - set(wegknopen_wkoidn)
    arcpy.AddMessage(
        f"{len(niet_bestaande_knopen)} niet bestaande knopen,: eerste 100: {list(niet_bestaande_knopen)[:100]}")

    if len(niet_gebruikte_knopen) > 0:
        arcpy.AddMessage("verwijder niet gebruikte knopen")
        wegknopen_selectie = "wegknopen_selectie"
        if len(niet_gebruikte_knopen) == 1:
            niet_gebruikte_knopen_str = f"({tuple(niet_gebruikte_knopen)[0]})"
        else:
            niet_gebruikte_knopen_str = tuple(niet_gebruikte_knopen)
        arcpy.MakeFeatureLayer_management(
            in_features=wegknopen,
            out_layer=wegknopen_selectie,
            where_clause=f"WK_OIDN in {niet_gebruikte_knopen_str}"
        )
        arcpy.ExportFeatures_conversion(
            in_features=wegknopen_selectie,
            out_features="wegknoop_tmp5nietgebruikteknopen"
        )
        arcpy.DeleteFeatures_management(
            in_features=wegknopen_selectie
        )


def edit_begin_eindknoop(segmenten_resultaat, wegknopen_duplicate, wegknopen):
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -edit_begin_eindknoop")
    wegknopen_selectie = "wegknopen_selectie"
    arcpy.MakeFeatureLayer_management(
        in_features=wegknopen,
        out_layer=wegknopen_selectie,
        where_clause=f"WK_OIDN >= 100000000 AND WK_OIDN < 200000000"
    )

    wegsegmenten_selectie = "wegsegmenten_selectie_lyr"
    wegknopen_duplicate_wkoidn = tuple(wegknopen_duplicate.keys())
    if len(wegknopen_duplicate_wkoidn) == 1:
        wegknopen_duplicate_wkoidn_str = f"({tuple(wegknopen_duplicate_wkoidn)[0]})"
    else:
        wegknopen_duplicate_wkoidn_str = tuple(wegknopen_duplicate_wkoidn)
    # arcpy.AddMessage(f"whereclause: B_WK_OIDN IN {wegknopen_duplicate_wkoidn_str} OR E_WK_OIDN IN {wegknopen_duplicate_wkoidn_str}")
    arcpy.MakeFeatureLayer_management(
        in_features=segmenten_resultaat,
        out_layer=wegsegmenten_selectie,
        where_clause=f"B_WK_OIDN IN {wegknopen_duplicate_wkoidn_str} OR E_WK_OIDN IN {wegknopen_duplicate_wkoidn_str}"
    )
    arcpy.SelectLayerByLocation_management(
        in_layer=wegsegmenten_selectie,
        overlap_type="BOUNDARY_TOUCHES",
        select_features=wegknopen_selectie,
        search_distance="1 Centimeters"
    )

    set_begin_eind_knoop(wegsegmenten_selectie, wegknopen)


def maak_nieuwe_atttables(wegsegment, atttables=[]):
    arcpy.AddMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -maak_nieuwe_atttables")
    max_event = {row[0]: [row[1].firstPoint.M, row[1].lastPoint.M] for row in
                 arcpy.da.SearchCursor(wegsegment, ["WS_OIDN", "SHAPE@"])}

    for atttable in atttables:
        arcpy.AddMessage(f"atttable = {atttable}")
        i_delete = 0
        i_update = 0
        atttable_new = f"{atttable.split('_')[0]}VLA"
        arcpy.ExportTable_conversion(
            in_table=atttable,
            out_table=atttable_new,
        )
        if atttable in (
                "AttEuropweg_input",
                "AttGenumweg_input",
                "AttNationweg_input"
        ):
            f_uc = ["WS_OIDN"]
            with arcpy.da.UpdateCursor(atttable_new, f_uc) as uc:
                for row in uc:
                    ws_oidn = row[f_uc.index("WS_OIDN")]

                    if ws_oidn not in max_event:
                        uc.deleteRow()
                        i_delete += 1
        else:
            f_uc = ["WS_OIDN", "VANPOS", "TOTPOS"]
            with arcpy.da.UpdateCursor(atttable_new, f_uc) as uc:
                for row in uc:
                    ws_oidn = row[f_uc.index("WS_OIDN")]
                    van = row[f_uc.index("VANPOS")]
                    tot = row[f_uc.index("TOTPOS")]

                    if ws_oidn not in max_event or van >= max_event[ws_oidn][1] or tot <= max_event[ws_oidn][0]:
                        uc.deleteRow()
                        i_delete += 1
                    else:
                        update = False
                        if van < max_event[ws_oidn][0] and abs(van - max_event[ws_oidn][0]) > 0.001:
                            van = round(max_event[ws_oidn][0], 3)
                            update = True
                        if tot > max_event[ws_oidn][1] and abs(tot - max_event[ws_oidn][1]) > 0.001:
                            tot = round(max_event[ws_oidn][1], 3)
                            update = True
                        if update == True:
                            row_new = [ws_oidn, van, tot]
                            uc.updateRow(row_new)
                            i_update += 1
        arcpy.AddMessage(f"{i_update} updates voor {atttable}")
        arcpy.AddMessage(f"{i_delete} deletes voor {atttable}")
