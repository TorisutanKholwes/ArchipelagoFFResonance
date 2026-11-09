"""Region graph.

v0.1 has no verified game-side gating, so every area region is entered freely from the origin.
Story-order gating (chapter keys) is added once the mod can enforce it (milestone M4).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

from .data_loader import REGIONS

if TYPE_CHECKING:
    from .world import FFResonanceWorld

ORIGIN = "Menu"


def create_and_connect_regions(world: FFResonanceWorld) -> None:
    origin = Region(ORIGIN, world.player, world.multiworld)
    world.multiworld.regions.append(origin)
    for name in REGIONS:
        region = Region(name, world.player, world.multiworld)
        world.multiworld.regions.append(region)
        origin.connect(region, f"{ORIGIN} -> {name}")
