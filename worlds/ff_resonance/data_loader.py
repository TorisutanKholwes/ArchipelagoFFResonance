"""Loads the generated game data shipped in `data/` (works from a folder or a zipped .apworld)."""
from __future__ import annotations

import json
import pkgutil
from dataclasses import dataclass
from typing import Any

from BaseClasses import ItemClassification


def _load(name: str) -> Any:
    raw = pkgutil.get_data(__name__, f"data/{name}")
    if raw is None:
        raise FileNotFoundError(f"ff_resonance data file missing: data/{name}")
    return json.loads(raw.decode("utf-8"))


CLASSIFICATIONS = {
    "progression": ItemClassification.progression,
    "useful": ItemClassification.useful,
    "filler": ItemClassification.filler,
    "trap": ItemClassification.trap,
}


@dataclass(frozen=True)
class ItemData:
    ap_id: int
    name: str
    classification: ItemClassification
    category: str
    filler_weight: int


@dataclass(frozen=True)
class LocationData:
    ap_id: int
    name: str
    region: str
    category: str
    vanilla_item: int | None  # only chests carry a randomizable vanilla reward
    battle: bool
    requires: tuple[int, ...]  # AP item ids that must be held to reach this location
    shard_safe: int | None  # Oblivion Palace safe: Tablet Shards needed to open it
    logic_zone: int | None  # zone (map zone id) the location is in, for the zone_locks logic
    logic_progress: int | None  # main story progress from which it is reachable
    logic_all: bool  # place unknown: needs every zone and the cleared story (zone_locks only)


@dataclass(frozen=True)
class ZoneData:
    id: int
    item: str  # name of its "<Zone> Access" item
    reach_progress: int  # main progress from which its entrance counts as usable


@dataclass(frozen=True)
class StoryStep:
    progress: int  # main progress {progress:0} at which the story uses the zone
    zone: int


ITEMS: tuple[ItemData, ...] = tuple(
    ItemData(i["ap_id"], i["name"], CLASSIFICATIONS[i["classification"]], i["category"], i.get("filler_weight", 0))
    for i in _load("items.json")["items"]
)

LOCATIONS: tuple[LocationData, ...] = tuple(
    LocationData(loc["ap_id"], loc["name"], loc["region"], loc["category"], loc.get("vanilla_item"),
                 bool(loc.get("battle", False)), tuple(loc.get("requires", ())), loc.get("shard_safe"),
                 loc["logic"].get("zone"), loc["logic"].get("progress"), bool(loc["logic"].get("all", False)))
    for loc in _load("locations.json")["locations"]
)

_zones = _load("zones.json")
ZONES: tuple[ZoneData, ...] = tuple(ZoneData(z["id"], z["item"], z["reach_progress"]) for z in _zones["zones"])
STORY_STEPS: tuple[StoryStep, ...] = tuple(StoryStep(s["progress"], s["zone"]) for s in _zones["story_steps"])
START_ZONES: tuple[int, ...] = tuple(_zones["start_zones"])


@dataclass(frozen=True)
class ShopChain:
    item: str  # "Progressive Weapon Shop" ...
    chain: str  # weapon | armor | accessory
    copies: int  # number of tiers


SHOP_CHAINS: tuple[ShopChain, ...] = tuple(ShopChain(c["item"], c["chain"], c["copies"])
                                           for c in _load("shops.json")["chains"])

REGIONS: tuple[str, ...] = tuple(_load("regions.json")["regions"])

# Fingerprint of the generated data; must match the game mod's generated/mappings.lua.
DATA_VERSION: str = _load("version.json")["data_version"]
