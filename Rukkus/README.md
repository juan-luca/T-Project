# RUKKUS 💥

An original, chaotic **2D run & gun** platformer — inspired by the *feel* of Broforce,
Metal Slug and Contra, built with **Godot 4.x**. Everything here (characters, enemies, art,
audio hooks, names, IP) is original.

> Fast, explosive, destructible, funny, hard-but-fair. Run in, break everything, rescue the
> civilian, reach extraction.

---

## Status: M0 vertical slice (playable)

This is the foundation milestone — a runnable slice that exercises **every core system**
end to end. See `docs/DEVELOPMENT_PLAN.md` for the full MVP → Alpha → Beta → Release roadmap
and `docs/ARCHITECTURE.md` for the design proposal.

**What works now**
- Player with full game feel: run, jump, double-jump, dash/slide (with i-frames + dash-cancel),
  wall-slide, wall-jump, ledge-grab, coyote time, jump buffer, variable jump height,
  momentum/accel/decel/friction, air control, 8-direction aim.
- Shooting (data-driven weapons + pooled projectiles), grenades, melee.
- Enemies with perception (vision cone + hearing) and a 7-state AI machine.
- Destructible props, chain-reaction barrels, explosions with AOE + knockback + shockwave.
- Camera juice (follow, look-ahead, screen shake, zoom, hit-stop, slow-mo).
- HUD, power-ups, checkpoint, rescue NPC, moving platform, a full placeholder level.

---

## Run it

1. Install **Godot 4.3+** (standard build).
2. Open Godot → *Import* → select `Rukkus/project.godot`.
3. Press **F5** (Play). The main scene is `scenes/Main.tscn`.

> Art/audio are procedural placeholders (drawn shapes; silent SFX hooks) so the project runs
> with **zero binary assets**. Systems are wired to drop in real pixel-art/audio later without
> code changes.

## Controls (Player 1, keyboard)

| Action | Key | | Action | Key |
|---|---|---|---|---|
| Move | `A` / `D` | | Fire | `J` |
| Aim | `W`/`S` + move (8-dir) | | Grenade | `K` |
| Jump / Double / Wall | `Space` | | Melee | `L` |
| Dash / Slide | `Shift` (hold `S` = slide) | | Special / Ultimate | `Ctrl` |
| Pause | `Esc` | | | |

Gamepad is mapped too (left stick, `A` jump, `RT`/`X` fire, etc.). More slots (co-op) are a
config change — see `docs/ARCHITECTURE.md §11`.

---

## Project layout

```
Rukkus/
├── project.godot         autoloads, input map, physics layers
├── docs/                 ARCHITECTURE · DEVELOPMENT_PLAN · DESIGN_NOTES · DESIGNER_GUIDE · FUTURE_IMPROVEMENTS
├── src/
│   ├── autoload/         9 manager singletons (decoupled via EventBus)
│   ├── core/             StateMachine, State, PlayerIntent, ObjectPool
│   ├── data/             Resource classes = designer tools (.tres)
│   ├── combat/           DamageInfo, Health/Hurtbox/Hitbox components
│   ├── player/           Player + 11 locomotion states + components + visuals
│   ├── weapons/          WeaponHolder + weapon/projectile resources
│   ├── projectiles/      pooled Projectile
│   ├── enemies/          Enemy + perception + 7 AI states + resources
│   ├── powerups/ destruction/ camera/ ui/ characters/ world/ fx/
├── scenes/               Main, Player, Enemy, Projectile, Destructible, PowerUp, HUD, levels/
└── assets/placeholder/   (generated at runtime — nothing to ship yet)
```

## Adding content without code

New weapons, enemies, characters, power-ups and levels are **`.tres` resource files** — create
them in Godot's *New Resource* dialog. See `docs/DESIGNER_GUIDE.md`.

## License / originality

All content is original and intended to be freely licensable. No third-party sprites, audio,
names, maps or code were copied from any existing game.
