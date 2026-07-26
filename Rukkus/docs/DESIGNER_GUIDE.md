# RUKKUS — Designer Guide (content without code)

Everything a designer tunes lives in **Resource** files (`.tres`) or exported node fields.
You should almost never edit `.gd` to add content. Below: how to add each content type.

## Add a weapon
1. *FileSystem* → right-click `src/weapons/resources` → **New Resource** → `WeaponData`.
2. Set `id`, `display_name`, ballistics (`damage`, `fire_mode`, `fire_rate`, `pellets`,
   `spread_degrees`), feel (`recoil`, `knockback`, `screen_shake`), ammo, and a `projectile`
   (a `ProjectileData` resource — make one the same way).
3. Assign it to a character's `starting_weapon`, a power-up's `weapon_grant`, or an enemy's
   `weapon`. Done — no code.

Fire modes: `SEMI`, `AUTO`, `BURST`, `BEAM`. Exotic motion (homing, boomerang, gravity/arc,
explode-on-hit) is on `ProjectileData` — flags only.

## Add an enemy
1. **New Resource** → `EnemyData` in `src/enemies/resources`.
2. Pick an `archetype` (GRUNT/HEAVY/FLYER/SNIPER/KAMIKAZE/SHIELD/BOSS), stats, senses
   (`vision_range/angle`, `hearing_range`), behaviour flags (`can_take_cover`, `can_flank`,
   `can_retreat`, `retreat_hp_ratio`, `can_throw_grenades`), and optional `weapon`.
3. Place it via a level's spawn call or set it on an `Enemy.tscn` instance's `data` field.

`resistances` is a 6-float array indexed by damage type
`[BALLISTIC, EXPLOSIVE, FIRE, ELECTRIC, MELEE, TRUE]` — `<1` resists, `>1` is weak
(e.g. robots weak to ELECTRIC → set index 3 to `1.5`).

## Add a character
**New Resource** → `CharacterData`. Set stats, `move_tuning` (a `MovementTuning` resource —
tune the whole game feel here), `starting_weapon`, `ability_id`, `ultimate_id`, `color`, barks.

## Add a power-up
**New Resource** → `PowerUpData`. Pick an `effect` (HEAL, SHIELD, DAMAGE_MULT, INVINCIBILITY,
SPEED, EXTRA_JUMP, INFINITE_AMMO, SLOW_MOTION, WEAPON_SWAP…), `magnitude`, `duration`.
Assign to a `PowerUp.tscn` instance's `data` field.

## Add a destructible
Instance `Destructible.tscn`, set `material_type`, `max_hp`, `size`, `color`, and `explosive`
(+ `explosion_radius/damage`) for barrels. It is intentionally non-solid so you can never
delete level-critical floor by mistake.

## Add / tune a level
- Quick placeholder: duplicate `scenes/levels/jungle_01.tscn` (script `Level.gd`) and edit the
  procedural layout, or
- Author a real level with a `TileMap` for solid terrain + instanced enemy/prop scenes, and a
  `Marker2D` in group `player_spawn` for the start point. Register biome metadata in a
  `LevelData` resource (music, palette, `next_level`).

## Tune game feel
Open the character's `MovementTuning` (or `src/data/tuning_default.tres`) and adjust in the
inspector — run values, jump velocities, coyote/buffer windows, dash, wall, ledge. Changes are
live in the editor.
