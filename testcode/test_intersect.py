import arcpy
def intersecttest():
    arcpy.analysis.Intersect(
        in_features=r"'C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\wegennetten verbinden\wegennettenVerbinden3.gdb\wegsegmentWallonie_tmp6copySnap' #",
        out_feature_class=r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\wegennetten verbinden\wegennettenVerbinden3.gdb\testSelfIntersect_point_arcpy2",
        join_attributes="ALL",
        cluster_tolerance=None,
        output_type="POINT"
)
