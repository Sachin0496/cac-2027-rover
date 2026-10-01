"""Build the rover assembly. `pose` is the arm angle in degrees (used from drop 2 on)."""
from __future__ import annotations

from lib.model import Assembly
from modules import body, chassis, drive, electronics, excavator, tower


def rover(pose: float = 35.0) -> Assembly:
    asm = Assembly()
    asm.pose = pose
    chassis.build(asm)
    drive.build_all(asm)
    excavator.build(asm, pose)
    electronics.build(asm)
    tower.build(asm)
    body.build(asm)
    return asm
