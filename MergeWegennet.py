import os

import arcpy
from datetime import datetime


def tijd():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def merge_wegennet(workspace):
    arcpy.env.workspace = workspace
    bronnen = ["VlA", "WAL", "GRENS", "BRU"]
    table_fc_in_wr = [
        "wegsegment",
        "AttNationweg",
        "AttRijstroken",
        "AttWegbreedte",
        "AttWegverharding",
        "AttGenumweg",
        "AttEuropweg",
        "wegknoop",
    ]

    for table_fc in table_fc_in_wr:
        table_fc_bronnen = [f"{table_fc}{bron}" for bron in bronnen]
        if "wegknoopGRENS" in table_fc_bronnen:
            table_fc_bronnen.remove("wegknoopGRENS")
        arcpy.AddMessage(f"{tijd()} table_fc_bronnen: {table_fc_bronnen} => {table_fc}")
        arcpy.env.outputZFlag = "Disabled"
        arcpy.Merge_management(
            inputs=table_fc_bronnen,
            output=os.path.join(workspace, table_fc)
        )


# ----------------------------------
# if __name__ == '__main__':
#     merge_wegennet()
# arcpy.env.workspace = "C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\Wegenregister naar WRAPP\Wegenregister_SHAPE_20240919\Bewerkt\Bewerkt20240919.gdb"
# arcpy.env.overwriteOutput = True

