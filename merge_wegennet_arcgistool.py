import importlib
import arcpy
arcpy.AddMessage("20250425")
import os, importlib

basispath = os.path.realpath(__file__).split("GIStools")[0]
arcpy.AddMessage("basispath = %s" % basispath)
path2 = os.path.join(basispath, "GIStools")
from sys import path

path.append(path2)
import MergeWegennet

importlib.reload(MergeWegennet)
arcpy.AddMessage("reload python 3")

importlib.reload(MergeWegennet)

workspace = arcpy.GetParameterAsText(0)

MergeWegennet.merge_wegennet(workspace)
