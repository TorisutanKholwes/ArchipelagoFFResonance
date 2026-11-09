# Final Fantasy Resonance

> **Development preview (world version 0.8.0).** Checks, item delivery and notifications work in game. The goal is implemented but hasn't been confirmed on a real story clear yet. See "Current status" below.

## What does randomization do to this game?

The contents of treasure chests are shuffled into the multiworld. Opening a chest, picking up an item on the world map, obtaining a Vision or an Esper, completing a side quest, clearing a story chapter, winning a Colosseum battle or a Chamber of Arms trial sends an item to whichever player it belongs to. Items from other players arrive in your inventory, and the game's own "You obtained the following" window announces them.

## What is randomized?

- **Locations:**
  - **Treasure chests** (216): the chests in the game's treasure-box table, across Grandshelt, Lanzelt, Kolobos, Dirnado, Olderion, Zoldaad, Magi Nation Mysidia, Gronoa, Pharm and the Land of the Crystals.
  - **World-map pickups** (93, option `pickup_checks`, on by default): collecting each item lying on the world map. You still get the item itself.
  - **Tablet Shards** (up to 99, option `tablet_shard_checks`: `off` / `every_10` / `every_5` (default) / `every_3` / `every_shard`): reaching N shards collected (held plus handed in at Oblivion Palace). The 99th shard is always a check. The shards still work normally for the safes.
  - **Visions** (26, option `vision_checks`): obtaining each Vision.
  - **Requests** (33, option `request_checks`): completing each side quest.
  - **Chapters** (8, option `chapter_checks`): clearing story chapters 1 to 8.
  - **Espers** (9, option `esper_checks`, on by default): obtaining each Esper.
  - **Colosseum** (20, option `colosseum_checks`, off by default): winning each rank battle for the first time.
  - **Chamber of Arms** (12 or 24, option `chamber_checks`: `off` / `trials` / `all`, off by default): winning each Legendary Arm trial (and ultimate trial with `all`).
- **Items:** the original chest rewards (consumables, equipment and Gil), plus filler (potions, ethers, Phoenix Downs, Gil) for the other checks, which keep their normal in-game reward as well.
- **Progressive shop items** (option `progressive_shops`, on by default): Progressive Weapon Shop ×7, Progressive Armor Shop ×7, Progressive Accessory Shop ×6. See "Progressive shops" below.
- **Zone access items** (option `zone_locks`, on by default): 73 "<Zone> Access" items, one per map zone (a world-map entrance with all its inner maps: towns with their districts and castles, dungeons, shrines, caves, Sanctums of Light). See "Zone locks" below.

The 25 Tablet Shard safes of Oblivion Palace are chests named after the number of shards they need (for example "Lanzelt - Oblivion Palace Safe (12 Tablet Shards)").

**Logic:** a Chamber of Arms trial needs its Ancient piece. When that piece is found in a randomized chest (Ancient Katana, Whip, Firearm, Rod, Accessory), it becomes a progression item and the trial requires it.

## Progressive shops

With `progressive_shops` on (the default), each progressive shop item adds the next tier of gear to every shop of its kind:
- **Progressive Weapon Shop / Armor Shop:** the best weapon or armor of each type sold in the next chapter (copy 1 = chapter 2, …, copy 7 = chapter 8).
- **Progressive Accessory Shop:** the accessories the next chapter introduces (copy 1 = chapter 3, …, copy 6 = chapter 8).

Shops keep their own stock. The new gear goes into free slots, and only a full shop swaps its cheapest item of the same type. Added gear costs `progressive_shop_prices` of its normal price: `full`, `half` (default) or `quarter`. Buying isn't a check.

## Zone locks

With `zone_locks` on (the default), you can roam the world map freely, but you can only enter a zone once you have its "<Zone> Access" item:
- A locked zone's entrance on the world map has no Enter prompt.
- Fast travel to a locked zone is refused (the game shows its "place you haven't visited yet" message).
- Receiving the item opens the entrance at once, without leaving the world map.

The eight zones the story needs in chapter 1 start unlocked: Town of Mitra, Grandshelt (the Royal Capital), Earth Shrine, Village of Kol, Grandport Harbor, Town of Felicitas, Kolobos Ruins and Siren's Tower.

The logic follows the story. Each chapter needs every zone its story uses (taken from the game's own story data), so the story can always be finished. A zone's contents count as reachable once its item is found and the story has reached the point where the zone opens.

Checks whose place isn't known yet (Visions, requests, Espers other than Siren, Tablet Shard counts, the Oblivion Palace safes, a few chests) need every zone and the cleared story. World-map pickups need the cleared story, because their island isn't known. This is safe but strict; these checks still count normally when you do them earlier.

The story can still teleport you into a zone you haven't unlocked (this is allowed by design).

Chests whose original reward is a valuable (key) item or an artifact are **not** randomized yet, because their role in quests hasn't been verified. They keep their vanilla contents.

## What is the goal?

**Story Complete:** finish the main story. Detected when the game's main progress reaches its post-story value, the same condition the game uses to unlock post-story content.

## Which items can be in another player's world?

Any randomized chest reward: consumables, equipment and Gil.

## What does another world's item look like in Final Fantasy Resonance?

The chest gives nothing in game (the game shows "0 Gil"), and the item is sent to its owner.

## Current status

| Feature | Status |
|---|---|
| Seed generation | Works |
| Detecting opened chests in game | Works (including chests opened while offline) |
| Giving items in game | Works (items, equipment, Gil) |
| Archipelago connection | Works (in-game "Archipelago Options" on the title screen + ffr_bridge: ws/wss, password, reconnect) |
| Replacing vanilla chest contents | Works (randomized chests give nothing in game) |
| Vision / request checks | Works |
| Chapter checks | Implemented, not yet observed in play |
| Esper checks | Works |
| World-map pickup checks | Works |
| Tablet Shard checks | Works |
| Colosseum / Chamber of Arms checks | Implemented, not yet observed in play |
| Received-item notification | Works (game's own window for items) |
| In-game Archipelago messages | Works (mod 0.13.0): top-right popups for received items with the sender, Gil, zones, shop tiers, DeathLink, hints and chat; a "recent" list in the system menu (Esc), saved per seed. Checks you send aren't announced |
| Story-completion goal detection | Implemented, not yet observed on a real clear |
| Progressive shops | Works (tier gear added at the chosen price, purchases, update while playing; checked in game with weapon and accessory tiers) |
| Zone locks (entrances + fast travel) | Works (locking, live unlock and fast-travel refusal checked in game on chapter 1); story logic for later chapters comes from game data, not yet played through |
| DeathLink | Works |

## Oblivion Palace safes

All 25 safes in the Oblivion Palace (Lanzelt) are checks. They open as you hand in Tablet Shards (3, 6, 9 ... 94, 99).
- **19 safes** have a randomized reward.
- **6 safes** (9, 24, 40, 64, 80 and 89 shards) keep their vanilla reward: Magicite and Adamantite, whose role in the game isn't verified yet. Opening one still sends a check.

`oblivion_palace_useful_safes` (0-25, default 25) sets how many safes, in order of shards needed, may hold progression or useful items. The later safes only ever contain filler, so you don't have to collect all 99 shards for an important item.

## DeathLink

With `death_link: true`, a game over in Final Fantasy Resonance (your whole party defeated in battle) sends a death to every DeathLink player in the room. When another player dies, your party is wiped out:
- during a battle: immediately, by an enemy's instant-death attack. The normal game-over screen (continue, retry or load) appears after the next action, so if it's your turn, pick any action;
- outside battle: the death is queued and applied as soon as your next battle starts. Returning to the title screen discards a queued death.

The game over caused by someone else's death isn't sent back. Deaths that happen while the game or the bridge is closed are not replayed. The bridge's `--death-link on/off` overrides the YAML setting.

## Known limitations

- Item and location names come from the game's English text. Two maps without a display name in the game data use their internal map codes (`Town_01Gra_02`, `Dng_02Lan_41`). Maps that share a display name are told apart by their map code.
- There is no logic: every chest is considered reachable from the start. In practice, the in-game story still controls where you can go.
