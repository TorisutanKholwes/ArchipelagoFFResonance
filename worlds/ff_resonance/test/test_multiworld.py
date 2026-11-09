"""Generation sweeps: several seeds, all option combinations, multiple FFR players, mixed multiworlds."""
import itertools
import unittest

from Fill import distribute_items_restrictive
from test.general import setup_multiworld
from worlds import AutoWorldRegister

from ..world import FFResonanceWorld

TOGGLES = ("zone_locks", "progressive_shops", "include_battle_chests", "vision_checks", "request_checks", "chapter_checks",
           "esper_checks", "colosseum_checks", "pickup_checks")
SEEDS = (1, 2, 3)


def fill(multiworld) -> None:
    distribute_items_restrictive(multiworld)
    for step in ("post_fill",):
        for world in multiworld.worlds.values():
            getattr(world, step)()


class TestMultiworldGeneration(unittest.TestCase):
    def assert_complete(self, multiworld) -> None:
        unfilled = [loc.name for loc in multiworld.get_locations() if loc.item is None]
        self.assertEqual(unfilled, [], "unfilled locations")
        self.assertTrue(multiworld.can_beat_game(multiworld.state), "multiworld not beatable")

    def test_every_option_combination(self) -> None:
        for values, chamber in itertools.product(itertools.product((False, True), repeat=len(TOGGLES)),
                                                 ("off", "trials", "all")):
            options = dict(zip(TOGGLES, values), chamber_checks=chamber)
            with self.subTest(**options):
                mw = setup_multiworld(FFResonanceWorld, seed=1, options=options)
                fill(mw)
                self.assert_complete(mw)
                own = [loc for loc in mw.get_locations(1) if loc.address is not None]
                pool = [i for i in mw.itempool if i.player == 1]
                self.assertEqual(len(own), len(pool))

    def test_every_useful_safe_count(self) -> None:
        """Every slider value, on the smallest pool (chests only) with the most progression (all trials)."""
        chests_only = {"vision_checks": False, "request_checks": False, "chapter_checks": False,
                       "esper_checks": False, "pickup_checks": False, "tablet_shard_checks": "off",
                       "chamber_checks": "all"}
        for count, seed in itertools.product(range(26), SEEDS):
            with self.subTest(useful_safes=count, seed=seed):
                mw = setup_multiworld(FFResonanceWorld, seed=seed,
                                      options={**chests_only, "oblivion_palace_useful_safes": count})
                fill(mw)
                self.assert_complete(mw)
                excluded = [loc for loc in mw.get_locations(1) if loc.progress_type == loc.progress_type.EXCLUDED]
                self.assertEqual(len(excluded), 25 - count)
                for loc in excluded:
                    self.assertFalse(loc.item.advancement or loc.item.useful, f"{loc.name}: {loc.item.name}")

    def test_zone_locks_many_seeds(self) -> None:
        """Zone locks on the smallest pool (chests only, all Chamber trials) over many seeds."""
        chests_only = {"vision_checks": False, "request_checks": False, "chapter_checks": False,
                       "esper_checks": False, "pickup_checks": False, "tablet_shard_checks": "off",
                       "chamber_checks": "all", "zone_locks": True}
        for seed in range(1, 21):
            with self.subTest(seed=seed):
                mw = setup_multiworld(FFResonanceWorld, seed=seed, options=chests_only)
                fill(mw)
                self.assert_complete(mw)

    def test_several_ffr_players(self) -> None:
        for players, seed in itertools.product((2, 3, 4), SEEDS):
            with self.subTest(players=players, seed=seed):
                mw = setup_multiworld([FFResonanceWorld] * players, seed=seed,
                                      options={"chamber_checks": "all", "colosseum_checks": True,
                                               "tablet_shard_checks": "every_shard"})
                fill(mw)
                self.assert_complete(mw)
                # items really cross between worlds
                crossing = [loc for loc in mw.get_locations() if loc.item and loc.item.player != loc.player]
                self.assertTrue(crossing)

    def test_mixed_with_apquest(self) -> None:
        apquest = AutoWorldRegister.world_types["APQuest"]
        for seed in SEEDS:
            with self.subTest(seed=seed):
                mw = setup_multiworld([FFResonanceWorld, apquest, FFResonanceWorld], seed=seed,
                                      options=[{"vision_checks": False}, {}, {"request_checks": False}])
                fill(mw)
                self.assert_complete(mw)

    def test_same_seed_same_placement(self) -> None:
        def placement(seed: int) -> list[tuple[str, str, int]]:
            mw = setup_multiworld([FFResonanceWorld] * 2, seed=seed)
            fill(mw)
            return sorted((loc.name, loc.item.name, loc.item.player) for loc in mw.get_locations() if loc.item)
        self.assertEqual(placement(7), placement(7))
        self.assertNotEqual(placement(7), placement(8))
