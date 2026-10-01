"""Assembly model: every physical object is an Item carrying its metadata."""
from __future__ import annotations

from dataclasses import dataclass, field

from build123d import Color, Compound, Location, Pos, Shape


def to_bed(shape: Shape) -> Shape:
    """Centre on the bed in XY and drop onto z = 0."""
    bb = shape.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * shape


@dataclass
class Item:
    id: str                       # unique instance id, e.g. "wheel_lf"
    part: str                     # part type, e.g. "wheel" (instances of one type share an STL)
    kind: str                     # "printed" | "purchased" | "stock"
    module: str                   # "chassis" | "drive" | "excavator" | ...
    shape: Shape                  # world-frame solid
    color: str                    # hex
    mass_g: float | None = None   # purchased/stock: given; printed: computed from volume
    moving: str | None = None     # None | "arm" | "carriage" | "spin" (interference sweep)
    local: Shape | None = None    # printed: part in its own frame
    orient: Location | None = None  # printed: print orientation applied to `local`
    meta: dict = field(default_factory=dict)

    def oriented(self) -> Shape:
        """Printed part sitting on the bed in its print orientation."""
        base = self.local if self.local is not None else self.shape
        return to_bed((self.orient * base) if self.orient is not None else base)

    def mass(self) -> float:
        if self.mass_g is not None:
            return self.mass_g
        from checks.printfit import printed_mass_g
        return printed_mass_g(self.local if self.local is not None else self.shape)


class Assembly:
    def __init__(self) -> None:
        self.items: list[Item] = []
        self._ids: set[str] = set()

    def add(self, item: Item) -> Item:
        if item.id in self._ids:
            raise ValueError(f"duplicate item id {item.id!r}")
        self._ids.add(item.id)
        self.items.append(item)
        return item

    def by_module(self, module: str) -> list[Item]:
        return [i for i in self.items if i.module == module]

    def get(self, item_id: str) -> Item:
        return next(i for i in self.items if i.id == item_id)

    def compound(self) -> Compound:
        kids = []
        for it in self.items:
            s = it.shape.moved(Location())
            s.label = it.id
            s.color = Color(it.color)
            kids.append(s)
        return Compound(label="rover_v2", children=kids)


def printed_item(id: str, part: str, module: str, local: Shape, place: Location, color: str,
                 orient: Location | None = None, moving: str | None = None, **meta) -> Item:
    return Item(id, part, "printed", module, place * local, color, None, moving, local, orient, meta)


def bought_item(id: str, part: str, module: str, shape: Shape, place: Location, color: str,
                mass_g: float, kind: str = "purchased", moving: str | None = None, **meta) -> Item:
    return Item(id, part, kind, module, place * shape, color, mass_g, moving, None, None, meta)


def at(point, z_dir, x_dir=None) -> Location:
    """Location whose local +Z points along z_dir and local +X along x_dir, at `point`."""
    from build123d import Plane, Vector
    z = Vector(*z_dir).normalized()
    if x_dir is None:
        x = Vector(1, 0, 0) if abs(z.X) < 0.9 else Vector(0, 1, 0)
        x = (x - z * x.dot(z)).normalized()
    else:
        x = Vector(*x_dir).normalized()
    return Location(Plane(origin=tuple(point), x_dir=(x.X, x.Y, x.Z), z_dir=(z.X, z.Y, z.Z)))
