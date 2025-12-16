"""
wegennetwerkBrusselToWrvorm.py
------------------------------
Converteert inputdata uit Brussel naar Wegenregister-formaat,
met arcpy cursors en de nieuwe WegBrussel class.
"""

import os
from datetime import datetime

import arcpy

import GeometryLineCalculateM
from wegsegment_classes import WegBrussel


def to_wr(in_wegsegmenten,
          f_wegsegmenten,
          template,
          templates_tables,
          bron,
          d_status,
          d_morphology,
          d_beheer,
          d_brussel_straatnaam_links,
          d_brussel_straatnaam_rechts):
    """
    Zet Brussel netwerkdata om naar WR featureclass + tabellen.
    """
    print(f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}-toWr")

    # Doel featureclass en tabellen
    wegsegmenten_tmp7 = f"wegsegment{bron}"
    nationaleweg = f"AttNationweg{bron}"
    rijstroken = f"AttRijstroken{bron}"
    wegbreedte = f"AttWegbreedte{bron}"
    wegverharding = f"AttWegverharding{bron}"

    # Maak nieuwe featureclass
    arcpy.CreateFeatureclass_management(
        out_path=arcpy.env.workspace,
        out_name=wegsegmenten_tmp7,
        geometry_type="POLYLINE",
        template=template,
        has_m="ENABLED",
        has_z="ENABLED",
        spatial_reference=template
    )

    # Maak nieuwe tabellen
    for table in templates_tables:
        arcpy.CreateTable_management(
            out_path=arcpy.env.workspace,
            out_name=f"{os.path.basename(table.split('_')[0])}{bron}",
            template=table
        )

    # Velddefinities
    f_ic_wegsegment = [
        'Shape@', 'WS_OIDN', 'WS_UIDN', 'WS_GIDN', 'STATUS', 'LBLSTATUS', 'MORF', 'LBLMORF',
        'WEGCAT', 'LBLWEGCAT', 'LSTRNMID', 'LSTRNM', 'RSTRNMID', 'RSTRNM', 'BEHEER', 'LBLBEHEER',
        'METHODE', 'LBLMETHOD', 'OPNDATUM', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG', 'TGBEP',
        'LBLTGBEP', 'legende', 'bron'
    ]
    f_ic_nationaleweg = ['NW_OIDN', 'WS_OIDN', 'IDENT2', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG']
    f_ic_rijstroken = [
        'RS_OIDN', 'WS_OIDN', 'WS_GIDN', 'AANTAL', 'RICHTING', 'LBLRICHT',
        'VANPOS', 'TOTPOS', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG'
    ]
    f_ic_wegbreedte = ['WB_OIDN', 'WS_OIDN', 'WS_GIDN', 'BREEDTE',
                       'VANPOS', 'TOTPOS', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG']
    f_ic_wegverharding = ['WV_OIDN', 'WS_OIDN', 'WS_GIDN', 'TYPE', 'LBLTYPE',
                          'VANPOS', 'TOTPOS', 'BEGINTIJD', 'BEGINORG', 'LBLBGNORG']

    # Start edit session
    with arcpy.da.Editor(arcpy.env.workspace):
        ic_wegsegment = arcpy.da.InsertCursor(wegsegmenten_tmp7, f_ic_wegsegment)
        ic_nationaleweg = arcpy.da.InsertCursor(nationaleweg, f_ic_nationaleweg)
        ic_rijstroken = arcpy.da.InsertCursor(rijstroken, f_ic_rijstroken)
        ic_wegbreedte = arcpy.da.InsertCursor(wegbreedte, f_ic_wegbreedte)
        ic_wegverharding = arcpy.da.InsertCursor(wegverharding, f_ic_wegverharding)

        # Logging
        print(arcpy.env.workspace)
        print(arcpy.ListFeatureClasses())
        print(in_wegsegmenten)
        print(f"velden in {in_wegsegmenten}: {[f.name for f in arcpy.ListFields(in_wegsegmenten)]}")
        print(f"aantal features in {in_wegsegmenten}: {arcpy.GetCount_management(in_wegsegmenten).getOutput(0)}")

        # Selecteer enkel bruikbare segmenten
        where_clause = "(TeGebruiken <> 'nee' AND TeGebruiken <> 'Nee') OR TeGebruiken IS NULL"

        fouten = []
        with arcpy.da.SearchCursor(in_wegsegmenten, f_wegsegmenten, where_clause) as sc:
            for i, row in enumerate(sc):
                (geometrie, from_node, to_node, pn_id_l, pn_id_r, nat_road_i,
                 lvl, morphology, admin, typology, status, richting) = row

                fout = []
                if i % 10000 == 0:
                    print(f"{i} wegsegmenten omgezet, {len(fouten)} konden niet verwerkt worden")

                # Validatie geometrie
                if geometrie is None:
                    fout.append(f"ongeldige geometrie (None): {row}")
                elif geometrie.getLength() == 0:
                    fout.append(f"ongeldige geometrie (lengte 0): {row}")
                elif geometrie.firstPoint.equals(row[0].lastPoint):
                    fout.append(f"ongeldige geometrie (beginpunt = eindpunt): {row}")

                if fout:
                    fouten.append(fout)
                    continue

                # Zet om naar polyline met M-waarden
                geometry_wr = GeometryLineCalculateM.PolylineWithMValues(row[0]).out_geometry
                row_tmp = [geometry_wr] + list(row[1:])

                # Maak WegBrussel object
                weg = WegBrussel(*row_tmp,
                                 bron=bron,
                                 d_status=d_status,
                                 d_morphology=d_morphology,
                                 d_beheer=d_beheer,
                                 d_straatnaam_links=d_brussel_straatnaam_links,
                                 d_straatnaam_rechts=d_brussel_straatnaam_rechts)

                # Exporteer en schrijf wegsegment
                ic_wegsegment.insertRow(weg.export_wegsegment_as_list())
                row_nationweg = weg.export_nationweg_as_list()
                if row_nationweg[2] is not None:  # ident2 aanwezig
                    ic_nationaleweg.insertRow(row_nationweg)
                ic_rijstroken.insertRow(weg.export_rijstroken_as_list())
                ic_wegbreedte.insertRow(weg.export_wegbreedte_as_list())
                ic_wegverharding.insertRow(weg.export_wegverharding_as_list())

            print(f"{i} wegsegmenten omgezet, {len(fouten)} konden niet verwerkt worden")

        if fouten:
            print(f"Er konden {len(fouten)} niet verwerkt worden: eerste 10: {fouten[:10]}")

    return wegsegmenten_tmp7
