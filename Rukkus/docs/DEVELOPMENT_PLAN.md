# RUKKUS — Development Plan (MVP → Alpha → Beta → Release)

Each milestone is shippable/testable on its own. Modules are built small and verified before
the next one starts, exactly as requested.

## M0 — Foundation (this commit series) ✅ target of the initial slice
- Project config, autoloads, EventBus, folder structure.
- Core: `StateMachine`, `State`, `ObjectPool`, component base classes, `DamageInfo`.
- Data resources: `WeaponData`, `ProjectileData`, `EnemyData`, `CharacterData`, `PowerUpData`.
- Player vertical slice: run/jump/double-jump/dash/wall-slide/wall-jump/ledge-grab + coyote
  time, jump buffer, variable jump, momentum; 8-dir aim; shoot; grenade; melee.
- One weapon firing pooled projectiles; one enemy with a working AI state machine.
- Destructible crate + explosion; `GameCamera` with follow + shake; minimal HUD.
- One playable placeholder level. **Deliverable: a chaotic runnable vertical slice.**

## MVP
- 3 weapons (pistol, shotgun, rifle) + grenades + melee, all data-driven.
- 3 enemy archetypes (grunt, drone, bruiser) with full perception + cover.
- 1 biome (Jungle Base), 1 mini-boss, checkpoints + autosave, power-up pickups.
- Full HUD, screen shake, hit-stop, basic adaptive audio, pause/settings menu.

## Alpha
- 6–8 weapons incl. flamethrower/bazooka/laser/railgun; 3 characters w/ ability+ultimate.
- 8+ enemy types + 2 full bosses w/ phases & cinematics; ragdoll-lite deaths.
- 3 biomes, moving platforms/elevators/ropes, richer destruction, minimap.
- Progression (XP, unlocks, collectibles, achievements), power-up system complete.
- **Local co-op (2P)** enabled on top of the slot-based input.

## Beta
- All 10 biomes, all weapons/enemies/bosses, full audio (adaptive layers, surface SFX).
- Online co-op (up to 4) via `MultiplayerSynchronizer`; friendly-fire toggle; respawn.
- Full save/profiles, options, accessibility, controller remap, localization scaffold.
- Performance pass (pooling everywhere, atlases, streaming), balancing, content-tuning tools.

## Release
- Polish, juice, marketing build, achievements/leaderboards, secret characters, NG+.

---

## Verification checklist per module
- Compiles with no parse errors in the Godot editor.
- Runs in isolation (test scene) before integration.
- No hard cross-system references (only EventBus / injected deps).
- Numbers exposed as `@export` / Resource fields (designer-editable).
