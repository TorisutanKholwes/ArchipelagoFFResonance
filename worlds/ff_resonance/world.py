"""World class for FINAL FANTASY RESONANCE."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world
from . import options as ffr_options
from .data_loader import DATA_VERSION, LocationData


class FFResonanceWorld(World):
    """
    FINAL FANTASY RESONANCE is an HD-2D turn-based RPG. Treasure chests, world-map pickups, Visions,
    side quests, story chapters, Espers, the Colosseum and the Chamber of Arms send items to the multiworld.
    """

    game = "Final Fantasy Resonance"
    web = web_world.FFResonanceWebWorld()
    options_dataclass = ffr_options.FFResonanceOptions
    options: ffr_options.FFResonanceOptions

    item_name_to_id: ClassVar[dict[str, int]] = items.ITEM_NAME_TO_ID
    location_name_to_id: ClassVar[dict[str, int]] = locations.LOCATION_NAME_TO_ID
    item_name_groups = items.ITEM_NAME_GROUPS
    location_name_groups = locations.LOCATION_NAME_GROUPS

    origin_region_name = regions.ORIGIN

    active_locations: list[LocationData]

    def generate_early(self) -> None:
        self.active_locations = locations.select_active_locations(self)

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_item(self, name: str) -> items.FFResonanceItem:
        return items.create_item(self, name)

    def get_filler_item_name(self) -> str:
        return items.FILLER_ITEM_NAME

    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            "world_version": "0.8.0",
            "data_version": DATA_VERSION,
            "goal_min_progress": 9000,
            **self.options.as_dict("goal", "zone_locks", "progressive_shops", "progressive_shop_prices",
                                   "include_battle_chests", "vision_checks", "request_checks",
                                   "chapter_checks", "esper_checks", "colosseum_checks", "chamber_checks",
                                   "pickup_checks", "tablet_shard_checks", "oblivion_palace_useful_safes",
                                   "death_link"),
        }
