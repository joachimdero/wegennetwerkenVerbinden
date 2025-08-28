import arcpy

from wegennetwerkWallonieToWrvorm import to_wr
arcpy.env.workspace = r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\wegennetten " \
                      r"verbinden\wegennettenVerbinden3.gdb"
arcpy.env.overwriteOutput = True
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
f_wegsegmenten = [
    'SHAPE@', 'NATUR_DESC', 'ICARRUEID1', 'RUE_NOM1', 'COMMU_NOM1',
    'COMMU_INS1', 'ICARRUEID2', 'RUE_NOM2', 'COMMU_NOM2',
    'COMMU_INS2', 'GESTION', 'VOIRIE_NOM', 'SENS_BK', 'AMENAG'
]

if __name__ == '__main__':
    to_wr(
        in_wegsegmenten=r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\wegennetten "
                        r"verbinden\wegennettenVerbinden3.gdb\TESTwegsegmenten_tmp7SplitAtPoint_ExportFeatures",
        f_wegsegmenten=f_wegsegmenten,
        template=template_wegsegmenten,
        templates_tables=templates_tables,
        bron="WAL"
    )
