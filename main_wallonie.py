import sys

import arcpy

import selectieSegmentdelenWallonie
from wegennetwerkWallonieToWrvorm import merge_dissolve_wegsegmenten, generalize_snap_wegsegmenten, \
    snap_split_wegsegment_at_endpoint, maak_knopen, to_wr, \
    set_begin_eind_knoop, load_data

arcpy.env.workspace = "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten " \
                      "verbinden\\wegennettenVerbinden3.gdb"
arcpy.env.overwriteOutput = True

in_segmenten_test = [
    "WallonieBRABANTWALLON_input",
    "WallonieHAINAUT_input"
]
in_wegsegmenten = ["WallonieBRABANTWALLON_input",
                   "WallonieHAINAUT_input",
                   "WallonieLIEGE_input",
                   "WallonieLUXEMBOURG_input",
                   "WallonieNAMUR_input"
                   ]
# in_wegsegmenten = in_segmenten_test
in_wegsegmenten_wr = "wegsegmentVLA"
f_wegsegmenten = [
    'SHAPE@', 'NATUR_DESC', 'ICARRUEID1', 'RUE_NOM1', 'COMMU_NOM1',
    'COMMU_INS1', 'ICARRUEID2', 'RUE_NOM2', 'COMMU_NOM2',
    'COMMU_INS2', 'GESTION', 'VOIRIE_NOM', 'SENS_BK', 'AMENAG'
]

in_grenslijn = r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\wegennetten verbinden\wegennetten " \
               r"verbinden.gdb\AdmGrensType_gewestgrens"
in_wallonie_manueleSelectie_nietgebruiken = r"C:\GoogleTeamAim\Team AIM\Team AIM\Data " \
                                            r"beheer\Projecten\WRapp\wegennetten " \
                                            r"verbinden\wegennettenVerbinden2.gdb\Wallonie_manueleSelectie_nietgebruiken20240708"
in_wbn = r"C:\GoogleTeamDrive\GISdata\grb.gdb\Wbn"

template_wegsegmenten = "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten " \
                        "verbinden\\wegennettenVerbinden2.gdb\\wegsegment_template"
template_wegknopen = "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten " \
                     "verbinden\\wegennettenVerbinden2.gdb\\wegknoop_template"
templates_tables = [
    "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten verbinden\\wegennettenVerbinden2.gdb\\AttEuropweg_template",
    "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten verbinden\\wegennettenVerbinden2.gdb\\AttGenumweg_template",
    "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten verbinden\\wegennettenVerbinden2.gdb\\AttNationweg_template",
    "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten verbinden\\wegennettenVerbinden2.gdb\\AttRijstroken_template",
    "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten verbinden\\wegennettenVerbinden2.gdb\\AttWegbreedte_template",
    "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten verbinden\\wegennettenVerbinden2.gdb\\AttWegverharding_template",
    "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten "
    "verbinden\\wegennettenVerbinden2.gdb\\RltOgkruising_template"
]
bron = "WAL"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    for fc in (in_wegsegmenten_wr, in_grenslijn, in_wallonie_manueleSelectie_nietgebruiken, template_wegsegmenten,
               template_wegknopen):
        if arcpy.Exists(fc) == False:
            arcpy.AddError(f"{fc} bestaat niet")
            sys.exit()
    for fc in in_wegsegmenten:
        if arcpy.Exists(fc) == False:
            arcpy.AddError(f"{fc} bestaat niet")
            sys.exit()
    for fc in templates_tables:
        if arcpy.Exists(fc) == False:
            arcpy.AddError(f"{fc} bestaat niet")
            sys.exit()
    # wegsegmenten_tmp3 = merge_dissolve_wegsegmenten(in_wegsegmenten)
    wegsegmenten_tmp3 = load_data(in_wegsegmenten)
    wegsegmenten_tmp5 = generalize_snap_wegsegmenten(wegsegmenten_tmp3)
    wegsegmenten_tmp6 = snap_split_wegsegment_at_endpoint(wegsegmenten_tmp5)
    wegsegmenten_tmp7 = to_wr(wegsegmenten_tmp6, f_wegsegmenten, template_wegsegmenten, templates_tables, bron=bron)

    wegknopen_tmp2 = maak_knopen(wegsegmenten_tmp7, template_wegknopen, bron=bron)

    wegsegmenten_tmp7 = selectieSegmentdelenWallonie.selectie_segmenten_wallonie(
        ws=arcpy.env.workspace,
        wegsegmenten=wegsegmenten_tmp7,
        wegsegmenten_wr=in_wegsegmenten_wr,
        grenslijn=in_grenslijn,
        wallonie_manueleSelectie_nietgebruiken=in_wallonie_manueleSelectie_nietgebruiken,
        wbn=in_wbn,
        wegknopenWAL=wegknopen_tmp2
    )

    wegsegmenten_tmp8 = arcpy.ExportFeatures_conversion(
        in_features=wegsegmenten_tmp7,
        out_features="wegsegmenten_tmp8",
        where_clause="selectie NOT LIKE 'niet geselecteerd%'"
    )
    set_begin_eind_knoop(wegsegmenten_tmp8, wegknopen_tmp2)
