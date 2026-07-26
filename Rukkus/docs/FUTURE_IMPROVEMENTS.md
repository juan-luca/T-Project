# RUKKUS — Future Improvements (backlog)

Grouped by system. Ordered roughly by value. None of these require re-architecting — the
seams are already in place.

## Combat & weapons
- [ ] Author the full arsenal as resources: flamethrower (BEAM + FIRE), laser, railgun
      (piercing hitscan), electric arc (chain lightning strategy), minigun spin-up, boomerang
      return polish, mines (proximity), sticky grenades.
- [ ] Per-surface / per-enemy impact FX and SFX variants.
- [ ] Weapon pickups dropped by enemies; ammo economy tuning.
- [ ] Reload animations + weapon-swap wheel.

## Enemies & bosses
- [ ] Remaining archetypes: sniper (laser telegraph), shield trooper, kamikaze polish,
      mutants, turrets, drones with weapons.
- [ ] Full boss framework: `BossData` (phases, thresholds, summons), phase states,
      telegraphed patterns, multi-segment health bar, intro/defeat cinematics.
- [ ] Squad tactics: real cover nodes, flanking pathfinding (NavigationServer2D), grenades
      that arc, suppression, call-for-reinforcements.

## Movement & physics
- [ ] Proper ledge markers + two-sided ledge grab & climb animation.
- [ ] Ragdoll on death (skeleton2D or verlet), ropes (pin joints), swings, zip-lines,
      elevators with call buttons, bounce pads, conveyor belts.
- [ ] Coyote/buffer/aim assist tuning per difficulty.

## Destruction
- [ ] Destructible **terrain** via TileMap chunking (dig/blast through walls & bridges).
- [ ] Material-specific debris, dust, glass shatter shaders, dynamic 2D lights on explosions.

## Levels & progression
- [ ] All 10 biomes with unique hazards, palettes, music, secrets, dynamic events.
- [ ] Progression: XP curve, unlock tree, collectibles, achievements, side missions, NG+.
- [ ] Level-select / world map; par times; score attack.

## Presentation
- [ ] HD pixel-art sprite sets + `AnimatedSprite2D` swap-in; squash & stretch on real frames.
- [ ] 2D lighting pass, normal maps, parallax with real art, screen-space shaders (heat haze,
      CRT/scanline option), chromatic aberration on hits.
- [ ] Real adaptive-music stems with intensity-driven crossfade layers.

## Multiplayer
- [ ] Local co-op (2–4) — bind extra device slots; split power-up/score feeds.
- [ ] Online co-op via `MultiplayerSynchronizer` + RPCs; host migration; respawn tokens;
      friendly-fire toggle already present.

## Tech & tooling
- [ ] In-editor tuning dashboards; a debug overlay (hitboxes, AI state, perception cones).
- [ ] Async level streaming with loading screens; sprite atlases; texture import presets.
- [ ] Automated tests for state machines and damage math (GUT).
- [ ] Settings menu UI, controller remap, accessibility (shake scale done; add colorblind,
      hold-to-toggle, aim assist).
- [ ] Save-slot UI, cloud save, profile stats.
