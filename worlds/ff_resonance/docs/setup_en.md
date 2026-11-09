# Final Fantasy Resonance Setup Guide

> **Development preview.** Checks, item delivery and notifications work. The goal is implemented but not yet confirmed on a real story clear.

## Required software

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases)
- FINAL FANTASY RESONANCE (Steam, Windows build; tested on Linux with Proton)
- The FFResonanceAP game mod (UE4SS Lua mod), from the project's `FFResonanceMod` folder. Install instructions are in `FFResonanceMod/README.md`.

## Generating a game

1. Create a player YAML. You can export a template from the Archipelago Launcher ("Generate Template Options"). The available options are:
   - `goal`: `story_complete`
   - `include_battle_chests`: `true` / `false` (the monster-in-a-box chest)
   - `pickup_checks`: `true` / `false` (world-map pickups, on by default)
   - `tablet_shard_checks`: `off` / `every_10` / `every_5` / `every_3` / `every_shard` (default `every_5`)
   - `oblivion_palace_useful_safes`: `0`-`25` (default `25`): how many Oblivion Palace safes, in order of Tablet Shards needed, may hold progression or useful items; the later ones hold filler only
   - `vision_checks`, `request_checks`, `chapter_checks`, `esper_checks`: `true` / `false` (on by default)
   - `colosseum_checks`: `true` / `false` (off by default)
   - `chamber_checks`: `off` / `trials` / `all` (off by default)
   - `death_link`: `true` / `false` (off by default; see the game page for what counts as a death)
2. Put the YAML in Archipelago's `Players` folder and run `Generate`.

Example:

```yaml
name: Player1
game: Final Fantasy Resonance
Final Fantasy Resonance:
  goal: story_complete
  zone_locks: true
  progressive_shops: true
  progressive_shop_prices: half
  include_battle_chests: true
  pickup_checks: true
  tablet_shard_checks: every_5
  oblivion_palace_useful_safes: 25
  vision_checks: true
  request_checks: true
  chapter_checks: true
  esper_checks: true
  colosseum_checks: false
  chamber_checks: off
  death_link: false
```

## Connecting to a server

1. Install the mod (`FFResonanceMod/README.md`) and the bridge (`FFResonanceMod/bridge/README.md`).
2. Start the bridge: `python -m ffr_bridge` (no arguments).
3. Start the game. On the title screen, click **Archipelago Options**, enter the server (e.g. `archipelago.gg`), port, slot name and room password, press **Connect**, then **Back**. The text under the button turns green: **Connected as <slot>**.
4. Load a new game, or a save not used with another seed.

The password is not saved: enter it again each time you start the game. The mod does nothing to a save until you press Connect during the current game launch. You can restart the bridge at any time; nothing is lost while it's offline (press Connect again afterwards).
