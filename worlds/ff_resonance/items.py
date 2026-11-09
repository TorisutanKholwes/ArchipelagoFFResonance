"""Item definitions and item pool creation."""
from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification
from Options import OptionError

from .data_loader import ITEMS, SHOP_CHAINS, START_ZONES, ZONES, ItemData

if TYPE_CHECKING:
    from .world import FFResonanceWorld

GAME = "Final Fantasy Resonance"
VICTORY = "Victory"

ITEM_BY_NAME: dict[str, ItemData] = {item.name: item for item in ITEMS}
ITEM_BY_ID: dict[int, ItemData] = {item.ap_id: item for item in ITEMS}
ITEM_NAME_TO_ID: dict[str, int] = {item.name: item.ap_id for item in ITEMS}

# Filler used when the pool needs padding: Potion (game item 1). Its AP id is fixed by the ID
# scheme in spec/tools/generate.py: 77_000_000 + 1 * 10 + 1.
FILLER_ITEM_ID = 77_000_011
FILLER_ITEM_NAME = ITEM_BY_ID[FILLER_ITEM_ID].name

ITEM_NAME_GROUPS: dict[str, set[str]] = {}
for _item in ITEMS:
    ITEM_NAME_GROUPS.setdefault(_item.category.capitalize(), set()).add(_item.name)


class FFResonanceItem(Item):
    game = GAME


def create_item(world: FFResonanceWorld, name: str) -> FFResonanceItem:
    data = ITEM_BY_NAME[name]
    return FFResonanceItem(name, data.classification, data.ap_id, world.player)


def create_event(world: FFResonanceWorld, name: str) -> FFResonanceItem:
    return FFResonanceItem(name, ItemClassification.progression, None, world.player)


FILLER_CHOICES: list[ItemData] = [item for item in ITEMS if item.filler_weight > 0]


def random_filler_name(world: FFResonanceWorld) -> str:
    choice = world.random.choices(FILLER_CHOICES, weights=[i.filler_weight for i in FILLER_CHOICES])[0]
    return choice.name


def create_all_items(world: FFResonanceWorld) -> None:
    """One item per active location, so the pool size always equals the location count.

    Chests contribute their vanilla reward (shuffled by AP fill). Visions, requests and chapters keep
    their in-game reward, so they contribute weighted filler (spec FILLER_TABLE).
    With zone_locks, the chapter-1 zones are given at the start and the other zone access items replace
    filler; with progressive_shops, the progressive shop items do too. Filler is taken first from the
    filler added for non-chest locations, then from filler-class chest rewards.
    """
    extra = [create_item(world, random_filler_name(world)) for loc in world.active_locations
             if loc.vanilla_item is None]
    chest = [create_item(world, ITEM_BY_ID[loc.vanilla_item].name) for loc in world.active_locations
             if loc.vanilla_item is not None]
    world.random.shuffle(extra)
    added: list[FFResonanceItem] = []
    if world.options.zone_locks:
        start = set(START_ZONES)
        for zone in ZONES:
            if zone.id in start:
                world.multiworld.push_precollected(create_item(world, zone.item))
        added += [create_item(world, zone.item) for zone in ZONES if zone.id not in start]
    if world.options.progressive_shops:
        added += [create_item(world, chain.item) for chain in SHOP_CHAINS for _ in range(chain.copies)]
    extra, chest = remove_filler(world, extra, chest, len(added))
    world.multiworld.itempool += added + chest + extra


def remove_filler(world: FFResonanceWorld, extra: list[FFResonanceItem], chest: list[FFResonanceItem],
                  count: int) -> tuple[list[FFResonanceItem], list[FFResonanceItem]]:
    """Make room for `count` added items: drop non-chest filler first, then filler-class chest rewards."""
    take = min(count, len(extra))
    extra = extra[take:]
    need = count - take
    if need:
        filler_chests = [i for i, item in enumerate(chest) if item.classification == ItemClassification.filler]
        if len(filler_chests) < need:
            raise OptionError(f"{world.player_name}: not enough filler for {count} zone/shop items; "
                              "enable more checks, or turn zone_locks or progressive_shops off")
        drop = set(world.random.sample(filler_chests, need))
        chest = [item for i, item in enumerate(chest) if i not in drop]
    return extra, chest
