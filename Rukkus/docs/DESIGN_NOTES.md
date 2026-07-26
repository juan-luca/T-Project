# RUKKUS — Design Notes

Short rationale for the choices that shaped the slice.

## Pillars
1. **Chaos with clarity** — lots on screen, but the player always reads threats. Enemy `!`
   alert glyphs, floating damage, muzzle flashes, telegraphs.
2. **Everything reacts** — bullets, explosions, destructibles, knockback, screen shake,
   hit-stop and slow-mo form a constant feedback loop (juice).
3. **Game feel first** — the movement had a dedicated `MovementTuning` resource before any
   level existed. Coyote time + jump buffer + variable jump + dash-cancel are non-negotiable.
4. **Fair difficulty** — enemies telegraph, have reaction delays, and lose sight of you; you
   have i-frames on dash and generous platforming grace.

## Why component + state-machine + EventBus
- **Components** (`HealthComponent`, `WeaponHolder`, `Hurtbox/Hitbox`) are reused verbatim by
  player, enemies and props → no duplicated damage/health logic.
- **State machines** keep locomotion/AI/boss-phase logic open for extension (add a state, edit
  nothing else) and readable (each mode is one small file).
- **EventBus** means the HUD, camera, audio and score all react to gameplay without gameplay
  knowing they exist. This is the backbone of the decoupling requirement.

## Why data-driven resources
Godot `Resource` subclasses appear in the editor's *New Resource* dialog, giving designers
real tools for free. "10 weapons / 11 enemies / 11 power-ups" becomes 10/11/11 `.tres` files,
not 30+ scripts. Difficulty scales all enemy stats through one `Settings.difficulty_scale()`.

## Placeholder-art strategy
Presentation is isolated (`PlayerVisuals`, `EnemyVisuals`, `_draw` shapes, procedural debris,
shockwave rings). Zero binary assets ship, so the repo is tiny and the game runs anywhere.
Swapping in HD pixel art = replacing the visuals node with an `AnimatedSprite2D`; no system
code changes.

## Multiplayer-readiness decisions made now (not later)
- Input is `PlayerIntent` per **slot**, never global `Input` reads.
- Damage/health/score flow through components + EventBus (RPC/`MultiplayerSynchronizer`-friendly).
- `friendly_fire`, `shared_lives`, `max_players` are already `GameManager` flags.
- Camera already frames the average of all players.

## Performance decisions
- `ObjectPool` for projectiles/debris/damage-numbers (the allocation hot paths).
- Physics layers keep collision pairs minimal; projectiles hit hurtboxes (one layer) filtered
  by team in code, and never snag on actor bodies.
- Debris and FX self-clean on timers; nothing accumulates.

## Known slice simplifications (addressed in later milestones)
- Ledge-grab detection is right-side only (single ray) — real levels get proper ledge markers.
- Projectile wall-bounce uses an approximate normal.
- Adaptive music is a hook (`AudioManager.set_music_intensity`) pending real stems.
- Solid *destructible terrain* (vs. destructible props) awaits a TileMap chunk system.
