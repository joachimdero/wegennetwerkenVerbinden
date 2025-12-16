import json
import os
import sys
import arcpy

# from merge_wegennet_arcgistool import workspace
from wegennetwerkWallonieToWrvorm import maak_knopen, set_begin_eind_knoop
from wegennetwerkBrusselToWrVorm import to_wr

print(f"start ")

arcpy.env.workspace = r"C:\GoogleSharedDrives\Team GIS\Projecten\WRapp\wegennetten " \
                      r"verbinden\wegennettenVerbinden.gdb"
arcpy.env.overwriteOutput = True

in_wegsegmenten = ["SegmentenBrussel_input"]


def load_json(dirname, basename):
    filepath = os.path.join(dirname, basename)
    with open(filepath, mode='r', encoding='utf-8') as file:
        dict_json = {(item["value"]): item["label_nl"] for item in json.load(file)}
    return dict_json


dirname = r"C:\GoogleSharedDrives\Team GIS\Projecten\WRapp\wegennetten verbinden\inputdata"
d_status = load_json(dirname, "brussel_status.json")
d_morphology = load_json(dirname, "brussel_morphology.json")
d_brussel_straatnaam_links = load_json(dirname, "brussel_straatnaamLinks.json")
d_brussel_straatnaam_rechts = load_json(dirname, "brussel_straatnaamRechts.json")
d_brussel_beheer = load_json(dirname, "brussel_admin.json")

in_wegsegmenten_wr = "wegsegmentVLA"
in_brussel_manueleSelectie_nietgebruiken = "brr_segments_morphology_niet_gebruiken"
# in_wbn = r"C:\GoogleTeamDrive\GISdata\grb.gdb\Wbn"

f_in_wegsegmenten = [
    'Shape@', 'from_node', 'to_node', 'pn_id_l', 'pn_id_r', 'nat_road_i', 'lvl',
    'morphology', 'admin', 'typology', 'status', 'bm_directi'
]

ws_templates = r"C:\GoogleSharedDrives\Team GIS\Projecten\WRapp\wegennetten verbinden\wegennettenVerbindenTemplates.gdb"
in_grenslijn = os.path.join(ws_templates, "AdmGrensType_gewestgrens")
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

bron = "BRU"

if __name__ == '__main__':
    for fc in (in_wegsegmenten_wr, in_grenslijn, template_wegsegmenten,
               template_wegknopen):
        if not arcpy.Exists(fc):
            arcpy.AddError(f"fc{fc} bestaat niet (in_wegsegmenten_wr, in_grenslijn, "
                           f"in_brussel_manueleSelectie_nietgebruiken, template_wegsegmenten,template_wegknopen)")
            sys.exit()
    for fc in in_wegsegmenten:
        if not arcpy.Exists(fc):
            arcpy.AddError(f"fc {fc} bestaat niet (in_wegsegmenten)")
            arcpy.AddError(f"arcpy.env.workspace{arcpy.env.workspace}")
            sys.exit()
    for table in templates_tables:
        if not arcpy.Exists(fc):
            arcpy.AddError(f"{table} bestaat niet (template tables)")
            sys.exit()

wegsegmenten = to_wr(in_wegsegmenten=in_wegsegmenten[0],
                     f_wegsegmenten=f_in_wegsegmenten,
                     template=template_wegsegmenten,
                     templates_tables=templates_tables,
                     bron=bron,
                     d_status=d_status,
                     d_morphology=d_morphology,
                     d_brussel_straatnaam_links=d_brussel_straatnaam_links,
                     d_brussel_straatnaam_rechts=d_brussel_straatnaam_rechts,
                     d_beheer=d_brussel_beheer
                     )
wegknopen = maak_knopen(wegsegmenten, template_wegknopen, bron=bron)
set_begin_eind_knoop(wegsegmenten, wegknopen)
