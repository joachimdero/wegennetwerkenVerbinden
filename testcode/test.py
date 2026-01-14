"""
test klasse wegwallonie
"""
from wegsegment_classes import WegWallonie

row=()
bron = "?"
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
# ic_wegsegment.insertRow(row_new)
row_nationweg = weg.export_nationweg_as_list()
row_genumweg = weg.export_genummerdeweg_as_list()
row_rijstroken = weg.export_rijstroken_as_list()
row_wegbreedte = weg.export_wegbreedte_as_list()
row_wegverharding = weg.export_wegverharding_as_list()
# if row_nationweg[2] is not None:
#     ic_nationaleweg.insertRow(row_nationweg)
#     ic_genummerdeweg.insertRow(row_genumweg)
# ic_rijstroken.insertRow(row_rijstroken)
# ic_wegbreedte.insertRow(row_wegbreedte)
# ic_wegverharding.insertRow(row_wegverharding)