from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .options import option_groups


class FFResonanceWebWorld(WebWorld):
    game = "Final Fantasy Resonance"
    theme = "ocean"
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Final Fantasy Resonance for Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["TorisutanKholwes"],
    )
    tutorials = [setup_en]
    option_groups = option_groups
