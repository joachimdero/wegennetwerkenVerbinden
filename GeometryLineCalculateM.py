import arcpy


class PolylineWithMValues:
    def __init__(self, in_geometry):
        self.in_geometry = in_geometry
        self.out_geometry = None
        self.add_m_values()

    def add_m_values(self):
        if self.in_geometry.type != 'polyline':
            raise ValueError("Input geometrie moet een lijn zijn")

        # Maak een array om de punten van de nieuwe geometrie op te slaan
        geometry_new = arcpy.Array()

        # Itereer door de onderdelen van de lijn
        for part in self.in_geometry:
            part_new = arcpy.Array()
            for pnt in part:
                pnt.M = self.in_geometry.measureOnLine(pnt)

                # if part_new and [round(pnt.X, 3), round(pnt.Y, 3)] == [round(part_new[-1].X, 3), round(part_new[-1].Y, 3)]:
                if part_new and [pnt.X, pnt.Y] == [part_new[-1].X, 3, part_new[-1].Y]:
                    # print("identiek vertex")
                    part_new.remove(len(part_new)-1)
                part_new.add(pnt)
            geometry_new.add(part_new)
        self.out_geometry = arcpy.Polyline(geometry_new, has_z=True, has_m=True)
        # print ("out_geometry: ", self.out_geometry.WKT)

        return self.out_geometry.WKT


# if __name__ == "__main__":
#     in_wegsegmenten = "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten " \
#                       "verbinden\\wegennettenVerbinden2.gdb\\Wallonie_tmp3dissolve"
#     with arcpy.da.SearchCursor(in_wegsegmenten, "SHAPE@") as sc:
#         i = 0
#         for row in sc:
#             i += 1
#             if i > 2:
#                 break
#             row_new = PolylineWithMValues(row[0])
            # print (row_new.out_geometry.WKT)
