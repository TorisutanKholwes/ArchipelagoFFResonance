from collections import Counter

from BaseClasses import ItemClassification, LocationProgressType

from ..data_loader import ITEMS, LOCATIONS, REGIONS, SHOP_CHAINS, START_ZONES, ZONES
from ..items import FILLER_CHOICES, FILLER_ITEM_NAME, ITEM_BY_ID
from ..locations import GOAL_LOCATION
from . import FFResonanceTestBase


def own_pool(test: FFResonanceTestBase) -> list[str]:
    return [item.name for item in test.multiworld.itempool if item.player == test.player]


def own_location_names(test: FFResonanceTestBase) -> set[str]:
    return {loc.name for loc in test.multiworld.get_locations(test.player) if loc.address is not None}


DEFAULT_OFF = {"colosseum", "chamber"}
ZONE_ITEM_NAMES = {z.item for z in ZONES}
START_ZONE_NAMES = {z.item for z in ZONES if z.id in START_ZONES}
SHOP_ITEM_NAMES = {c.item for c in SHOP_CHAINS}
SHOP_COPIES = sum(c.copies for c in SHOP_CHAINS)


def randomized_chest(loc) -> bool:
    """A chest whose vanilla reward goes into the pool (kept-reward safes add filler instead)."""
    return loc.category == "chest" and loc.vanilla_item is not None


def default_active(loc) -> bool:
    if loc.category in DEFAULT_OFF:
        return False
    if loc.category == "shard":  # default every_5: 5, 10, ..., 95 and 99
        n = int(loc.name.split()[2])
        return n % 5 == 0 or n == 99
    return True


class TestDefaultGeneration(FFResonanceTestBase):
    def test_default_locations_created(self) -> None:
        self.assertEqual(own_location_names(self), {loc.name for loc in LOCATIONS if default_active(loc)})

    def test_categories_present(self) -> None:
        counts = Counter(loc.category for loc in LOCATIONS)
        self.assertEqual(counts["vision"], 26)
        self.assertEqual(counts["request"], 33)
        self.assertEqual(counts["chapter"], 8)
        self.assertEqual(counts["esper"], 9)
        self.assertEqual(counts["colosseum"], 20)
        self.assertEqual(counts["chamber"], 24)
        self.assertEqual(counts["pickup"], 93)
        self.assertEqual(counts["shard"], 99)
        self.assertGreater(counts["chest"], 200)

    def test_pool_contains_every_vanilla_chest_reward(self) -> None:
        pool = Counter(own_pool(self))
        expected = Counter(ITEM_BY_ID[loc.vanilla_item].name for loc in LOCATIONS if randomized_chest(loc))
        for name, n in expected.items():
            self.assertGreaterEqual(pool[name], n, name)

    def test_extra_locations_get_filler(self) -> None:
        pool = Counter(own_pool(self))
        chest_rewards = Counter(ITEM_BY_ID[loc.vanilla_item].name for loc in LOCATIONS if randomized_chest(loc))
        extra = pool - chest_rewards
        filler_names = {i.name for i in FILLER_CHOICES}
        # With zone locks (default), the zone access items take the place of some of that filler.
        self.assertEqual(sum(extra.values()),
                         sum(1 for loc in LOCATIONS if default_active(loc) and not randomized_chest(loc)))
        self.assertEqual(sum(n for name, n in extra.items() if name in ZONE_ITEM_NAMES),
                         len(ZONE_ITEM_NAMES) - len(START_ZONE_NAMES))
        self.assertEqual(sum(n for name, n in extra.items() if name in SHOP_ITEM_NAMES), SHOP_COPIES)
        others = {name for name in extra if name not in ZONE_ITEM_NAMES | SHOP_ITEM_NAMES}
        self.assertTrue(others <= filler_names, others - filler_names)

    def test_goal_is_locked_victory(self) -> None:
        goal = self.multiworld.get_location(GOAL_LOCATION, self.player)
        self.assertIsNotNone(goal.item)
        self.assertEqual(goal.item.name, "Victory")
        self.assertBeatable(False)  # zone locks: the story needs zone items first
        self.collect_all_but([])
        self.assertBeatable(True)

    def test_regions_exist(self) -> None:
        for name in REGIONS:
            self.assertIsNotNone(self.multiworld.get_region(name, self.player))

    def test_slot_data(self) -> None:
        slot_data = self.world.fill_slot_data()
        self.assertEqual(slot_data["goal"], 0)
        self.assertEqual(slot_data["goal_min_progress"], 9000)
        self.assertRegex(slot_data["data_version"], r"^[0-9a-f]{16}$")
        for key in ("include_battle_chests", "vision_checks", "request_checks", "chapter_checks", "esper_checks",
                    "pickup_checks"):
            self.assertEqual(slot_data[key], 1, key)
        self.assertEqual(slot_data["tablet_shard_checks"], 5)
        self.assertEqual(slot_data["colosseum_checks"], 0)
        self.assertEqual(slot_data["chamber_checks"], 0)
        self.assertEqual(slot_data["death_link"], 0)


class TestDeathLink(FFResonanceTestBase):
    options = {"death_link": True}

    def test_slot_data_enables_death_link(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["death_link"], 1)

    def test_locations_unchanged(self) -> None:
        expected = [loc for loc in LOCATIONS if default_active(loc)]
        self.assertEqual(len(own_pool(self)), len(expected))


class TestWithoutBattleChests(FFResonanceTestBase):
    options = {"include_battle_chests": False}

    def test_battle_chests_removed(self) -> None:
        names = own_location_names(self)
        battle = [loc.name for loc in LOCATIONS if loc.battle]
        self.assertTrue(battle, "data should contain at least one battle chest")
        for name in battle:
            self.assertNotIn(name, names)
        expected = [loc for loc in LOCATIONS if default_active(loc) and not loc.battle]
        self.assertEqual(len(own_pool(self)), len(expected))


class TestChestsOnly(FFResonanceTestBase):
    options = {"vision_checks": False, "request_checks": False, "chapter_checks": False, "esper_checks": False,
               "pickup_checks": False, "tablet_shard_checks": "off"}

    def test_only_chests(self) -> None:
        names = own_location_names(self)
        self.assertEqual(names, {loc.name for loc in LOCATIONS if loc.category == "chest"})
        pool = Counter(own_pool(self))
        self.assertEqual(sum(pool.values()), len(names))
        # Zone items replace filler-class chest rewards; every other chest reward stays in the pool.
        expected = Counter(ITEM_BY_ID[loc.vanilla_item].name for loc in LOCATIONS if randomized_chest(loc)
                           and ITEM_BY_ID[loc.vanilla_item].classification != ItemClassification.filler)
        for name, n in expected.items():
            self.assertGreaterEqual(pool[name], n, name)
        self.assertEqual(sum(pool[name] for name in ZONE_ITEM_NAMES), len(ZONE_ITEM_NAMES) - len(START_ZONE_NAMES))


class TestData(FFResonanceTestBase):
    run_default_tests = False

    def test_ids_follow_scheme(self) -> None:
        for item in ITEMS:
            if item.category == "zone":
                self.assertIn(item.ap_id - 79_000_000, {z.id for z in ZONES}, item.name)
            elif item.category == "shop":
                self.assertIn(item.ap_id, {79_900_001, 79_900_002, 79_900_003}, item.name)
            else:
                self.assertTrue(77_000_000 <= item.ap_id < 79_000_000, item.name)
        for loc in LOCATIONS:
            if loc.category == "chest":
                self.assertTrue(80_000_000 <= loc.ap_id < 82_000_000, loc.name)
            else:
                self.assertTrue(82_000_000 <= loc.ap_id < 83_000_000, loc.name)
        bases = {"vision": 82_000_000, "request": 82_100_000, "chapter": 82_200_000, "colosseum": 82_300_000,
                 "chamber": 82_400_000, "esper": 82_500_000, "pickup": 82_600_000, "shard": 82_700_000}
        for loc in LOCATIONS:
            if loc.category in bases:
                self.assertTrue(bases[loc.category] <= loc.ap_id < bases[loc.category] + 100_000, loc.name)

    def test_only_chests_have_vanilla_items(self) -> None:
        for loc in LOCATIONS:
            if loc.vanilla_item is not None:
                self.assertEqual(loc.category, "chest", loc.name)
            elif loc.category == "chest":
                self.assertIsNotNone(loc.shard_safe, f"{loc.name}: only Oblivion Palace safes keep their reward")

    def test_oblivion_palace_safes(self) -> None:
        safes = sorted((loc for loc in LOCATIONS if loc.shard_safe is not None), key=lambda loc: loc.shard_safe)
        self.assertEqual(len(safes), 25)
        self.assertEqual([loc.shard_safe for loc in safes][:4], [3, 6, 9, 12])
        self.assertEqual(safes[-1].shard_safe, 99)
        kept = {loc.shard_safe for loc in safes if loc.vanilla_item is None}
        self.assertEqual(kept, {9, 24, 40, 64, 80, 89})
        for loc in safes:
            self.assertEqual(loc.ap_id, 80_203_100 + int(loc.ap_id % 100), loc.name)

    def test_filler_is_filler(self) -> None:
        self.assertEqual(self.world.create_item(FILLER_ITEM_NAME).classification, ItemClassification.filler)
        for item in FILLER_CHOICES:
            self.assertEqual(item.classification, ItemClassification.filler, item.name)

    def test_progression_items_are_exactly_the_required_pieces(self) -> None:
        required = {ap for loc in LOCATIONS for ap in loc.requires}
        progression = {i.ap_id for i in ITEMS
                       if i.classification & ItemClassification.progression and i.category != "zone"}
        self.assertEqual(progression, required)
        self.assertEqual({ITEM_BY_ID[ap].name for ap in required},
                         {"Ancient Katana", "Ancient Whip", "Ancient Firearm", "Ancient Rod", "Ancient Accessory"})


class TestShardSteps(FFResonanceTestBase):
    run_default_tests = False

    def test_steps(self) -> None:
        from ..locations import shard_selected
        names = [f"Tablet Shards: {n} Collected" for n in range(1, 100)]
        self.assertEqual(sum(shard_selected(n, 1) for n in names), 99)
        self.assertEqual(sum(shard_selected(n, 3) for n in names), 33)   # 3..99, 99 is a multiple of 3
        self.assertEqual(sum(shard_selected(n, 5) for n in names), 20)   # 5..95 + 99
        self.assertEqual(sum(shard_selected(n, 10) for n in names), 10)  # 10..90 + 99


class TestAllChecks(FFResonanceTestBase):
    options = {"colosseum_checks": True, "chamber_checks": "all", "tablet_shard_checks": "every_shard"}

    def test_every_location_created(self) -> None:
        self.assertEqual(own_location_names(self), {loc.name for loc in LOCATIONS})

    def test_chamber_trials_need_their_piece(self) -> None:
        for loc in LOCATIONS:
            if loc.requires:
                names = [ITEM_BY_ID[ap].name for ap in loc.requires]
                self.assertAccessDependency([loc.name], [names], only_check_listed=True)


class TestChamberTrialsOnly(FFResonanceTestBase):
    options = {"chamber_checks": "trials"}

    def test_no_ultimate_trials(self) -> None:
        names = own_location_names(self)
        self.assertEqual(sum(1 for n in names if n.startswith("Chamber of Arms") and n.endswith("(Trial)")), 12)
        self.assertFalse([n for n in names if n.endswith("(Ultimate Trial)")])


def safe_progress_types(test: FFResonanceTestBase) -> dict[int, LocationProgressType]:
    return {loc.shard_safe: test.multiworld.get_location(loc.name, test.player).progress_type
            for loc in LOCATIONS if loc.shard_safe is not None}


class TestUsefulSafesDefault(FFResonanceTestBase):
    def test_every_safe_is_normal(self) -> None:
        self.assertTrue(all(pt == LocationProgressType.DEFAULT for pt in safe_progress_types(self).values()))


class TestUsefulSafesTen(FFResonanceTestBase):
    options = {"oblivion_palace_useful_safes": 10}

    def test_safes_after_the_tenth_are_filler_only(self) -> None:
        types = safe_progress_types(self)
        thresholds = sorted(types)
        for n in thresholds[:10]:
            self.assertEqual(types[n], LocationProgressType.DEFAULT, n)
        for n in thresholds[10:]:
            self.assertEqual(types[n], LocationProgressType.EXCLUDED, n)

    def test_slot_data(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["oblivion_palace_useful_safes"], 10)


class TestUsefulSafesNoneChestsOnly(FFResonanceTestBase):
    """Smallest pool (chests only) with every safe filler-only: fill must still succeed."""
    options = {"oblivion_palace_useful_safes": 0, "vision_checks": False, "request_checks": False,
               "chapter_checks": False, "esper_checks": False, "pickup_checks": False, "tablet_shard_checks": "off"}

    def test_all_safes_excluded(self) -> None:
        self.assertTrue(all(pt == LocationProgressType.EXCLUDED for pt in safe_progress_types(self).values()))


class TestZoneLocks(FFResonanceTestBase):
    """Zone locks (default on, TD-033)."""

    def swept_state(self, item_names: list[str]):
        state = self.multiworld.state.copy()
        for name in item_names:
            state.collect(self.world.create_item(name), True)
        state.sweep_for_advancements()
        return state

    def test_start_zones_precollected_not_in_pool(self) -> None:
        pre = {i.name for i in self.multiworld.precollected_items[self.player]}
        self.assertEqual(pre, START_ZONE_NAMES)
        self.assertEqual(len(START_ZONE_NAMES), 8)
        pool = Counter(own_pool(self))
        for name in ZONE_ITEM_NAMES - START_ZONE_NAMES:
            self.assertEqual(pool[name], 1, name)
        for name in START_ZONE_NAMES:
            self.assertEqual(pool[name], 0, name)

    def test_zone_items_are_progression(self) -> None:
        for name in ZONE_ITEM_NAMES:
            self.assertTrue(self.world.create_item(name).classification & ItemClassification.progression, name)

    def chest_in(self, map_name: str) -> str:
        return next(loc.name for loc in LOCATIONS if loc.category == "chest" and map_name in loc.name
                    and loc.vanilla_item is not None and not loc.battle)

    def test_chapter_one_zone_open_at_start(self) -> None:
        state = self.swept_state([])
        self.assertTrue(self.multiworld.get_location(self.chest_in("Town of Mitra"), self.player).can_reach(state))

    def test_chapter_two_zone_needs_its_item(self) -> None:
        loc = self.multiworld.get_location(self.chest_in("Dilmagia"), self.player)
        self.assertFalse(loc.can_reach(self.swept_state([])))
        self.assertTrue(loc.can_reach(self.swept_state(["Dilmagia, the Machinopolis Access"])))

    def test_later_chapter_needs_earlier_story_zones(self) -> None:
        loc = self.multiworld.get_location(self.chest_in("Olderion, the Aquapolis"), self.player)
        self.assertFalse(loc.can_reach(self.swept_state(["Olderion, the Aquapolis Access"])))
        chapter2 = ["Dilmagia, the Machinopolis Access", "Mt. Thunderclap Access", "Mobliz Shipyard Access",
                    "Wind Shrine Access", "Dwarven Forge Access"]
        self.assertTrue(loc.can_reach(self.swept_state(chapter2 + ["Olderion, the Aquapolis Access"])))

    def test_unknown_place_needs_everything(self) -> None:
        vision = next(loc.name for loc in LOCATIONS if loc.category == "vision")
        loc = self.multiworld.get_location(vision, self.player)
        everything = sorted(ZONE_ITEM_NAMES - START_ZONE_NAMES)
        self.assertFalse(loc.can_reach(self.swept_state(everything[:-1])))
        self.assertTrue(loc.can_reach(self.swept_state(everything)))

    def test_slot_data(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["zone_locks"], 1)


class TestZoneLocksOff(FFResonanceTestBase):
    options = {"zone_locks": False}

    def test_no_zone_items(self) -> None:
        self.assertFalse(self.multiworld.precollected_items[self.player])
        self.assertFalse(set(own_pool(self)) & ZONE_ITEM_NAMES)
        self.assertEqual(self.world.fill_slot_data()["zone_locks"], 0)

    def test_everything_open(self) -> None:
        state = self.multiworld.state.copy()
        name = next(loc.name for loc in LOCATIONS if loc.category == "chest" and "Dilmagia" in loc.name)
        self.assertTrue(self.multiworld.get_location(name, self.player).can_reach(state))


class TestProgressiveShops(FFResonanceTestBase):
    """Progressive shop items (default on, TD-034)."""

    def test_copies_in_pool(self) -> None:
        pool = Counter(own_pool(self))
        self.assertEqual({c.chain: c.copies for c in SHOP_CHAINS}, {"weapon": 7, "armor": 7, "accessory": 6})
        for chain in SHOP_CHAINS:
            self.assertEqual(pool[chain.item], chain.copies, chain.item)

    def test_useful_not_progression(self) -> None:
        for name in SHOP_ITEM_NAMES:
            item = self.world.create_item(name)
            self.assertTrue(item.classification & ItemClassification.useful, name)
            self.assertFalse(item.classification & ItemClassification.progression, name)

    def test_slot_data(self) -> None:
        data = self.world.fill_slot_data()
        self.assertEqual(data["progressive_shops"], 1)
        self.assertEqual(data["progressive_shop_prices"], 1)  # half


class TestProgressiveShopsOff(FFResonanceTestBase):
    options = {"progressive_shops": False, "progressive_shop_prices": "quarter"}

    def test_no_shop_items(self) -> None:
        self.assertFalse(set(own_pool(self)) & SHOP_ITEM_NAMES)
        data = self.world.fill_slot_data()
        self.assertEqual(data["progressive_shops"], 0)
        self.assertEqual(data["progressive_shop_prices"], 2)
