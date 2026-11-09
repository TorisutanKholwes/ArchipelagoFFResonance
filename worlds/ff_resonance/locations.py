"""Location definitions."""
from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location, LocationProgressType

from .data_loader import LOCATIONS, LocationData
from .items import GAME, VICTORY, create_event

if TYPE_CHECKING:
    from .world import FFResonanceWorld

LOCATION_NAME_TO_ID: dict[str, int] = {loc.name: loc.ap_id for loc in LOCATIONS}

CATEGORY_GROUPS = {"chest": "Chests", "vision": "Visions", "request": "Requests", "chapter": "Chapters",
                   "colosseum": "Colosseum", "chamber": "Chamber of Arms", "esper": "Espers",
                   "pickup": "World Map Pickups", "shard": "Tablet Shards"}

LOCATION_NAME_GROUPS: dict[str, set[str]] = {}
for _loc in LOCATIONS:
    LOCATION_NAME_GROUPS.setdefault(_loc.region, set()).add(_loc.name)
    LOCATION_NAME_GROUPS.setdefault(CATEGORY_GROUPS[_loc.category], set()).add(_loc.name)

GOAL_LOCATION = "Story Complete"
GOAL_REGION = "Land of the Crystals"
STORY_REGION = "Story"
LAST_STORY_CHAPTER = 8


def story_event_name(chapter: int) -> str:
    """Event item of the zone_locks logic: the story of `chapter` is cleared."""
    return f"Story Chapter {chapter} Cleared"


def story_event_location(chapter: int) -> str:
    return f"Story Progress: Chapter {chapter}"


class FFResonanceLocation(Location):
    game = GAME


SHARD_MAX = max(int(loc.name.split()[2]) for loc in LOCATIONS if loc.category == "shard")


def shard_selected(name: str, step: int) -> bool:
    """'Tablet Shards: N Collected' is active for every step-th N, and always for the last one."""
    n = int(name.split()[2])
    return n % step == 0 or n == SHARD_MAX


def select_active_locations(world: FFResonanceWorld) -> list[LocationData]:
    """Locations enabled by the player's options."""
    chamber = world.options.chamber_checks.value
    enabled = {
        "chest": True,
        "vision": bool(world.options.vision_checks),
        "request": bool(world.options.request_checks),
        "chapter": bool(world.options.chapter_checks),
        "esper": bool(world.options.esper_checks),
        "pickup": bool(world.options.pickup_checks),
        "shard": world.options.tablet_shard_checks.value != 0,
        "colosseum": bool(world.options.colosseum_checks),
        "chamber": chamber != world.options.chamber_checks.option_off,
    }
    active = []
    for loc in LOCATIONS:
        if not enabled[loc.category]:
            continue
        if loc.category == "shard" and not shard_selected(loc.name, world.options.tablet_shard_checks.value):
            continue
        if (loc.category == "chamber" and chamber == world.options.chamber_checks.option_trials
                and loc.name.endswith("(Ultimate Trial)")):
            continue
        if loc.battle and not world.options.include_battle_chests:
            continue
        active.append(loc)
    return active


def filler_only_safes(world: FFResonanceWorld) -> set[str]:
    """Oblivion Palace safes beyond the player's useful-safe count (ordered by Tablet Shards needed)."""
    safes = sorted((loc for loc in world.active_locations if loc.shard_safe is not None),
                   key=lambda loc: loc.shard_safe)
    return {loc.name for loc in safes[world.options.oblivion_palace_useful_safes.value:]}


def create_all_locations(world: FFResonanceWorld) -> None:
    filler_only = filler_only_safes(world)
    for loc in world.active_locations:
        region = world.get_region(loc.region)
        location = FFResonanceLocation(world.player, loc.name, loc.ap_id, region)
        if loc.name in filler_only:
            # Fill never places progression or useful items on excluded locations.
            location.progress_type = LocationProgressType.EXCLUDED
        region.locations.append(location)

    if world.options.zone_locks:
        story = world.get_region(STORY_REGION)
        for chapter in range(1, LAST_STORY_CHAPTER + 1):
            event = FFResonanceLocation(world.player, story_event_location(chapter), None, story)
            story.locations.append(event)
            event.place_locked_item(create_event(world, story_event_name(chapter)))

    goal_region = world.get_region(GOAL_REGION)
    goal = FFResonanceLocation(world.player, GOAL_LOCATION, None, goal_region)
    goal_region.locations.append(goal)
    goal.place_locked_item(create_event(world, VICTORY))
