"""Player options."""
from __future__ import annotations

from dataclasses import dataclass

from Options import Choice, DeathLink, DefaultOnToggle, OptionGroup, PerGameCommonOptions, Range, Toggle


class Goal(Choice):
    """Victory condition.

    Story Complete: finish the main story (the game's main progress reaches the post-story value).
    """
    display_name = "Goal"
    option_story_complete = 0
    default = option_story_complete


class ZoneLocks(DefaultOnToggle):
    """Lock every map zone (town, dungeon, shrine, cave) behind an "<Zone> Access" item.

    Without its item, a zone's world-map entrance shows no Enter prompt and fast travel to it is refused.
    The world map itself stays free. The zones the story needs in chapter 1 start unlocked; the logic
    knows which zones each later chapter needs, so the story can always be finished.
    Off: every zone is open, as in the normal game."""
    display_name = "Zone Locks"


class ProgressiveShops(DefaultOnToggle):
    """Add Progressive Weapon Shop / Armor Shop / Accessory Shop items (7, 7 and 6 copies).

    Each copy adds the next tier of gear to every shop of that kind: weapons and armor of the next
    chapter (one per weapon/armor type), or the accessories the next chapter introduces. Shops keep their
    normal stock, so you're never weaker than in the normal game. The items replace filler."""
    display_name = "Progressive Shops"


class ProgressiveShopPrices(Choice):
    """Price of the gear added by the progressive shop items, compared with its normal price."""
    display_name = "Progressive Shop Prices"
    option_full = 0
    option_half = 1
    option_quarter = 2
    default = option_half


class IncludeBattleChests(DefaultOnToggle):
    """Include treasure chests that start a battle when opened (monster-in-a-box) as checks."""
    display_name = "Include Battle Chests"


class VisionChecks(DefaultOnToggle):
    """Obtaining each Vision (26) is a check. The Vision itself is still obtained normally."""
    display_name = "Vision Checks"


class RequestChecks(DefaultOnToggle):
    """Completing each side quest (request, 33) is a check. Its normal reward is still given."""
    display_name = "Request Checks"


class ChapterChecks(DefaultOnToggle):
    """Clearing each story chapter (1-8) is a check."""
    display_name = "Chapter Checks"


class PickupChecks(DefaultOnToggle):
    """Collecting each item lying on the world map (93) is a check. The item itself is still obtained."""
    display_name = "World Map Pickup Checks"


class TabletShardChecks(Choice):
    """Checks for the number of Tablet Shards collected (held plus handed in at Oblivion Palace).

    Off: none.
    Every 10 / Every 5 / Every 3 / Every Shard: a check at every 10th, 5th, 3rd or every shard
    collected. The 99th shard is always a check unless Off. The shards themselves work normally.
    """
    display_name = "Tablet Shard Checks"
    option_off = 0
    option_every_10 = 10
    option_every_5 = 5
    option_every_3 = 3
    option_every_shard = 1
    default = option_every_5


class OblivionPalaceUsefulSafes(Range):
    """How many of the 25 Oblivion Palace safes (Lanzelt) may hold progression or useful items.

    The safes open as you hand in Tablet Shards (3, 6, 9 ... 94, 99 shards). The first N safes, in that
    order, are normal locations; the later ones only ever contain filler, so you never need to collect
    all 99 shards for something important. 25 = every safe is a normal location; 0 = filler only.
    """
    display_name = "Oblivion Palace Useful Safes"
    range_start = 0
    range_end = 25
    default = 25


class EsperChecks(DefaultOnToggle):
    """Obtaining each of the 9 Espers is a check. The Esper itself is still obtained normally."""
    display_name = "Esper Checks"


class ColosseumChecks(Toggle):
    """Winning each of the 20 Colosseum rank battles for the first time is a check.
    The higher leagues expect levels 55-99, so this is off by default."""
    display_name = "Colosseum Checks"


class ChamberChecks(Choice):
    """Chamber of Arms trials as checks.

    Off: none.
    Trials: the 12 first awakenings (level 50 trials).
    All: also the 12 ultimate awakenings (level 75 trials, character level 70 required).
    A trial needs its Ancient piece; pieces found in randomized chests are progression items.
    """
    display_name = "Chamber of Arms Checks"
    option_off = 0
    option_trials = 1
    option_all = 2
    default = option_off


@dataclass
class FFResonanceOptions(PerGameCommonOptions):
    goal: Goal
    zone_locks: ZoneLocks
    progressive_shops: ProgressiveShops
    progressive_shop_prices: ProgressiveShopPrices
    include_battle_chests: IncludeBattleChests
    vision_checks: VisionChecks
    request_checks: RequestChecks
    chapter_checks: ChapterChecks
    esper_checks: EsperChecks
    pickup_checks: PickupChecks
    tablet_shard_checks: TabletShardChecks
    oblivion_palace_useful_safes: OblivionPalaceUsefulSafes
    colosseum_checks: ColosseumChecks
    chamber_checks: ChamberChecks
    death_link: DeathLink


option_groups = [
    OptionGroup("Logic", [ZoneLocks]),
    OptionGroup("Shops", [ProgressiveShops, ProgressiveShopPrices]),
    OptionGroup("Locations", [IncludeBattleChests, PickupChecks, TabletShardChecks, OblivionPalaceUsefulSafes,
                              VisionChecks, RequestChecks, ChapterChecks, EsperChecks, ColosseumChecks,
                              ChamberChecks]),
    OptionGroup("Multiworld", [DeathLink]),
]
