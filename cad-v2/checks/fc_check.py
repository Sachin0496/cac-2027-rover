"""Run inside FreeCAD (freecadcmd): import a STEP and report solids and invalid shapes."""
import sys

import FreeCAD
import Import

path = sys.argv[-1]
doc = FreeCAD.newDocument("chk")
Import.insert(path, doc.Name)
bad = n = 0
for o in doc.Objects:
    if hasattr(o, "Shape") and not o.Shape.isNull() and o.Shape.Solids:
        n += 1
        if not o.Shape.isValid():
            bad += 1
            print("INVALID", o.Label)
print("FC_RESULT solids=%d invalid=%d" % (n, bad))
