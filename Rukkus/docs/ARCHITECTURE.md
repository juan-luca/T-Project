# RUKKUS — Architecture Proposal

> Original chaotic 2D **Run & Gun** platformer inspired by the *feel* of Broforce, Metal
> Slug and Contra. All characters, enemies, art, audio, names and IP are **original**.
> Engine: **Godot 4.x**.

This document is the design/architecture proposal to review **before** judging the code.
It describes the layering, the systems, how they are decoupled, and the data-driven tooling
strategy. See `DEVELOPMENT_PLAN.md` for the milestone roadmap and `FUTURE_IMPROVEMENTS.md`
for the backlog.

---

## 1. Why Godot 4.x

| Requirement | How Godot 4.x serves it |
|---|---|
| 2D pixel-art action | Native TileMaps, `GPUParticles2D`, 2D lights/normal maps, 2D shaders, `Camera2D` |
| Data-driven designer tools | `Resource` (`.tres`) subclasses appear in the editor's *New Resource* dialog — designers edit weapons/enemies/power-ups without touching code |
| SOLID / decoupling | Node composition + `signal`s + an autoload **EventBus** avoid hard references |
| Performance | Object pooling, `VisibleOnScreenNotifier2D`, physics layers, sprite atlases, async `ResourceLoader` |
| Multiplayer later | Built-in `MultiplayerAPI` + `MultiplayerSynchronizer`; input is already device/slot indexed |
| Tooling & VCS | Text-based scenes/resources, small repo, free & open source |

Unity and Unreal are heavier and 3D-centric; nothing in this brief needs what they add over
Godot for a 2D game, and Godot's Resource workflow is a decisive win for the "designer tools"
and "everything configurable from data" requirements.

---

## 2. Layered architecture

```
┌──────────────────────────────────────────────────────────────┐
│  PRESENTATION      HUD · Menus · Damage numbers · FX · Camera  │
├──────────────────────────────────────────────────────────────┤
│  GAMEPLAY          Player · Enemy · Weapon · Projectile ·      │
│                    PowerUp · Destructible · Boss               │
├──────────────────────────────────────────────────────────────┤
│  CORE SERVICES     StateMachine · ObjectPool · Components ·    │
│                    Combat(DamageInfo/Hurtbox/Hitbox)           │
├──────────────────────────────────────────────────────────────┤
│  MANAGERS (autoload, singletons)                               │
│    EventBus · GameManager · LevelManager · CheckpointManager · │
│    AudioManager · InputManager · ObjectPool · SaveSystem ·     │
│    Settings                                                     │
├──────────────────────────────────────────────────────────────┤
│  DATA (Resources, .tres)   WeaponData · ProjectileData ·       │
│    EnemyData · CharacterData · PowerUpData · LevelData          │
└──────────────────────────────────────────────────────────────┘
```

**Rule of dependencies:** upper layers may reference lower layers; lower layers *never* hard-
reference upper layers. Cross-cutting communication goes through the **EventBus** (signals) so
that, e.g., the HUD reacts to `player_health_changed` without the Player knowing the HUD exists.

---

## 3. Decoupling strategy (the anti-spaghetti rules)

1. **EventBus over direct calls.** One autoload exposes global signals. Emitters `EventBus.emit_signal(...)`;
   listeners `EventBus.connect(...)`. No system holds a reference to another system just to notify it.
2. **Composition over inheritance.** Behaviour is assembled from **Components**
   (`HealthComponent`, `AimComponent`, `WeaponHolder`, `HurtboxComponent`, `HitboxComponent`).
   A Player, an Enemy and a destructible barrel all reuse `HealthComponent`.
3. **State machines** for anything with modes (Player locomotion, Enemy AI, Boss phases). Each
   state is its own `Node` script → open/closed: add a state without editing the others.
4. **Data-driven behaviour.** Numbers and content live in `Resource` files, not in code. A new
   weapon = a new `.tres`. Code reads the resource; designers own the resource.
5. **Interfaces via duck-typing / small base classes.** `Damageable` = "has `take_damage(DamageInfo)`".
   Weapons don't care whether they hit a Player, Enemy or crate.

---

## 4. Managers (autoload singletons)

| Autoload | Single responsibility |
|---|---|
| `EventBus` | Global, typed signal hub. The *only* place cross-system signals are declared. |
| `GameManager` | High-level game state (Boot→Menu→Playing→Paused→GameOver), score, run stats, slow-motion/`time_scale`. |
| `LevelManager` | Async load/unload of level scenes, spawn player(s) at spawn point, level lifecycle. |
| `CheckpointManager` | Activated checkpoints, current respawn transform, respawn flow. |
| `AudioManager` | Buses (Master/Music/SFX), pooled `AudioStreamPlayer2D`, adaptive music layers, one-shot SFX by id. |
| `InputManager` | Maps physical devices → **player slots** (1–4). Abstracts "player N intent" so co-op is a config change. |
| `ObjectPool` | Generic pooling for projectiles, particles, enemies, damage numbers, debris. |
| `SaveSystem` | Serialize/deserialize profile + per-slot progress to `user://`, autosave on checkpoint. |
| `Settings` | Volume, difficulty, controls, accessibility; persisted via `SaveSystem`. |

Autoloads are deliberately thin coordinators; heavy logic lives in the gameplay/core layers.

---

## 5. Player — component + state-machine design

```
Player (CharacterBody2D)
├── StateMachine (locomotion)
│   ├── Idle ├── Run ├── Jump ├── DoubleJump ├── Fall
│   ├── Dash ├── WallSlide ├── WallJump ├── LedgeGrab ├── Hurt └── Dead
├── HealthComponent            (hp, shield, invuln frames, i-frames)
├── AimComponent               (8-direction aim vector from input)
├── WeaponHolder               (equips WeaponData, fires, swaps, reload)
├── HurtboxComponent           (receives DamageInfo)
├── Sprite2D / AnimationPlayer  (presentation only)
└── PlayerConfig := CharacterData (stats, exclusive weapon, ability, ultimate)
```

**Game feel** is implemented in a `MovementTuning` resource + the states, and includes:
Coyote Time, Jump Buffer, Variable Jump Height, acceleration/deceleration/friction, air
control, terminal velocity, Wall Slide, Wall Jump, Dash (with i-frames + dash-cancel),
Ledge Grab / climb, and momentum preservation. All values are exported/`@export` so they are
tunable live in the inspector.

**Presentation is separated from logic:** states mutate `velocity`/flags and emit intent; a
thin `PlayerVisuals` node maps state → animation, squash & stretch, flip, muzzle flash. The
state machine never touches pixels directly.

---

## 6. Weapons & projectiles (data-driven)

```
WeaponHolder ──equips──> WeaponData (.tres)
   fire() reads: damage, fire_rate, spread, pellets, recoil, knockback,
                 reload_time, mag_size, projectile: ProjectileData, sfx, muzzle_fx
   └─ spawns Projectile(s) from ObjectPool, applies recoil to owner
Projectile (Area2D, pooled) ──on hit──> builds DamageInfo ──> target.HurtboxComponent
```

- **Open/closed:** adding Pistol, Shotgun, Rifle, Minigun, Flamethrower, Bazooka, Laser,
  Railgun, Boomerang, Electric-arc = new `WeaponData`/`ProjectileData` resources (+ optional
  `firing_pattern` enum for hitscan vs projectile vs beam vs spread). No new subclass required
  for the common cases; exotic behaviours (boomerang return, chain lightning) use a small
  strategy script referenced by the resource.
- **DamageInfo** carries amount, type (`BALLISTIC/EXPLOSIVE/FIRE/ELECTRIC/MELEE`), knockback,
  source, crit flag → enemies react differently per type (e.g. robots weak to electric).

---

## 7. Enemy AI

```
Enemy (CharacterBody2D)
├── StateMachine: Patrol → Investigate → Alert → Chase → Attack → TakeCover → Retreat → Search → Dead
├── HealthComponent · HurtboxComponent · HitboxComponent · WeaponHolder (optional)
├── PerceptionComponent  (visual cone via raycast + LOS; auditory via EventBus "noise" events)
└── EnemyData (.tres): stats, weapon, senses ranges, aggression, behaviour flags
```

- Vision = LOS raycast within a cone; hearing = subscribes to `EventBus.noise_emitted(pos, radius)`
  (gunfire/explosions create noise). Enemies **investigate last known position**, take cover,
  flank, retreat when low, and can throw grenades / swap weapons — all gated by `EnemyData` flags,
  so difficulty and behaviour are configurable per resource and per global difficulty setting.
- **Bosses** reuse the same state machine with **phase** states and telegraphed attack patterns,
  a `BossData` resource (phases, thresholds, summons), and a multi-segment health bar in the HUD.

---

## 8. Destruction, physics & FX

- `Destructible` component: hp + material type; on death spawns pooled **debris**, dust,
  a shockwave, and emits `EventBus.destructible_destroyed`. Level-critical geometry is tagged
  `indestructible` so the floor never disappears.
- Explosions = radial query (`PhysicsShapeQuery`) applying `DamageInfo` + knockback impulse
  falloff to every `Damageable`/`RigidBody2D` in range → chain-reaction barrels.
- Divertive/"fun" physics: `RigidBody2D` debris, ragdoll-lite death impulses, moving platforms,
  elevators, ropes (pin joints), swinging objects, bounce pads.

---

## 9. Camera & game juice

`GameCamera` (Camera2D): smooth follow with look-ahead, dynamic zoom (speed/threat based),
trauma-based **screen shake**, hit-stop / **slow-motion** (`Engine.time_scale`), and a cinematic
mode for boss intros. Driven by `EventBus` events (`explosion`, `boss_intro`, `player_hit`).

---

## 10. UI / Audio / Save (summary)

- **UI:** HUD (health, shield, ammo, grenades, special meter, minimap, objectives, floating
  damage, debug FPS) — all reacting to EventBus, no gameplay logic inside.
- **Audio:** bus layout + pooled players; adaptive music via crossfaded layers keyed to combat
  intensity; per-weapon / per-surface / per-explosion SFX ids.
- **Save:** JSON under `user://`, multiple profile slots, autosave on checkpoint, settings
  persistence.

---

## 11. Multiplayer-readiness (built in from day one, single-player first)

- Input is addressed by **player slot** (`InputManager.get_intent(slot)`), never by hard-coded
  `Input.is_action_pressed`. Adding players 2–4 = spawning more `Player` nodes bound to slots.
- Gameplay state changes flow through components/EventBus, which are straightforward to wrap
  with `MultiplayerSynchronizer` / RPCs later.
- `Friendly fire`, `respawn`, and `shared lives` are already config flags in `GameManager`.

---

## 12. Performance budget

Object pooling (projectiles, particles, debris, damage numbers, common enemies), off-screen
culling via `VisibleOnScreenNotifier2D`, physics-layer masks to minimise collision pairs,
sprite atlases, async level streaming, and "spawn budget" caps. No per-frame allocations in hot
paths.

---

## 13. Directory map

```
Rukkus/
├── project.godot            # autoloads, input map, layers, window
├── docs/                    # this proposal + plan + design notes + backlog
├── src/
│   ├── autoload/            # the 9 managers
│   ├── core/                # StateMachine, State, pooling, utils
│   ├── data/                # Resource classes (designer tools)
│   ├── combat/              # DamageInfo, Hurtbox/Hitbox components
│   ├── player/              # Player + states + components
│   ├── weapons/            (+ resources/*.tres)
│   ├── projectiles/
│   ├── enemies/            (+ states + resources/*.tres)
│   ├── powerups/           (+ resources/*.tres)
│   ├── destruction/ · camera/ · ui/ · characters/ · fx/
├── scenes/                  # Main + levels/*
└── assets/placeholder/      # generated placeholder art
```
