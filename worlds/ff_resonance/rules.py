"""Access rules and completion condition (rule_builder based).

Location requirements come from the spec ("requires": AP item ids), e.g. a Chamber of Arms trial needs
its Ancient piece when that piece is a randomized chest reward.

Zone locks (option zone_locks, TD-033): every map zone needs its "<Zone> Access" item. The story itself
becomes progression: "Story Chapter N Cleared" events need every zone the story uses in chapter N
(spec/zones.json story steps, data/zones.json). Reaching main progress P (inside chapter C) means
chapter C-1 cleared plus the access items of the chapter-C zones the story uses before P; by induction
those zones are enterable, because a zone's reach is never later than its first story step.
A location needs its zone and the progress from which it is reachable; a location whose place is
unknown needs every zone and the cleared story (always safe).

The goal event location holds the locked "Victory" item (locations.create_all_locations); with zone
locks it needs the cleared story (main progress 9000).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import And, Has, HasAll, Rule, True_

from .data_loader import STORY_STEPS, ZONES, LocationData
from .items import ITEM_BY_ID, VICTORY
from .locations import GOAL_LOCATION, LAST_STORY_CHAPTER, story_event_location, story_event_name

if TYPE_CHECKING:
    from .world import FFResonanceWorld

ZONE_BY_ID = {z.id: z for z in ZONES}
STORY_COMPLETE_PROGRESS = (LAST_STORY_CHAPTER + 1) * 1000


def combine(parts: list[Rule]) -> Rule:
    if not parts:
        return True_()
    return parts[0] if len(parts) == 1 else And(*parts)


def has_items(names: list[str]) -> Rule:
    if not names:
        return True_()
    return Has(names[0]) if len(names) == 1 else HasAll(*names)


def chapter_of(progress: int) -> int:
    return min(max(progress // 1000, 1), LAST_STORY_CHAPTER)


def progress_rule(progress: int) -> Rule:
    """The player can reach main story progress `progress`."""
    if progress >= STORY_COMPLETE_PROGRESS:
        return Has(story_event_name(LAST_STORY_CHAPTER))
    chapter = chapter_of(progress)
    parts: list[Rule] = []
    if chapter >= 2:
        parts.append(Has(story_event_name(chapter - 1)))
    zones = sorted({s.zone for s in STORY_STEPS if chapter_of(s.progress) == chapter and s.progress < progress})
    if zones:
        parts.append(has_items([ZONE_BY_ID[z].item for z in zones]))
    return combine(parts)


def chapter_cleared_rule(chapter: int) -> Rule:
    """Rule of the "Story Chapter N Cleared" event: the previous chapter plus every zone of this chapter."""
    parts: list[Rule] = []
    if chapter >= 2:
        parts.append(Has(story_event_name(chapter - 1)))
    zones = sorted({s.zone for s in STORY_STEPS if chapter_of(s.progress) == chapter})
    if zones:
        parts.append(has_items([ZONE_BY_ID[z].item for z in zones]))
    return combine(parts)


def zone_rule(zone_id: int, progress: int | None = None) -> Rule:
    """The player can enter the zone (holds its item and has reached its reach progress)."""
    zone = ZONE_BY_ID[zone_id]
    return combine([Has(zone.item), progress_rule(max(zone.reach_progress, progress or 0))])


def everything_rule() -> Rule:
    return combine([has_items([z.item for z in ZONES]), Has(story_event_name(LAST_STORY_CHAPTER))])


def zone_location_rule(loc: LocationData) -> Rule:
    if loc.logic_all:
        return everything_rule()
    if loc.logic_zone is not None:
        return zone_rule(loc.logic_zone, loc.logic_progress)
    if loc.logic_progress is not None:
        return progress_rule(loc.logic_progress)
    return True_()


def requires_rule(loc: LocationData) -> Rule | None:
    if not loc.requires:
        return None
    return has_items([ITEM_BY_ID[ap_id].name for ap_id in loc.requires])


def set_all_rules(world: FFResonanceWorld) -> None:
    zone_locks = bool(world.options.zone_locks)
    for loc in world.active_locations:
        parts = [r for r in (requires_rule(loc), zone_location_rule(loc) if zone_locks else None) if r is not None]
        if parts:
            world.set_rule(world.get_location(loc.name), combine(parts))
    if zone_locks:
        for chapter in range(1, LAST_STORY_CHAPTER + 1):
            world.set_rule(world.get_location(story_event_location(chapter)), chapter_cleared_rule(chapter))
        world.set_rule(world.get_location(GOAL_LOCATION), progress_rule(STORY_COMPLETE_PROGRESS))
    world.set_completion_rule(Has(VICTORY))
