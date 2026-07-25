extends Resource
class_name MovementTuning
## Every game-feel number lives here so movement can be tuned live in the inspector and
## shared/overridden per character. This is what makes the movement feel "excellent".

@export_group("Run")
@export var max_speed: float = 320.0
@export var acceleration: float = 2600.0
@export var deceleration: float = 3200.0        ## when input opposes velocity
@export var friction: float = 2000.0            ## when no input (ground)
@export var air_acceleration: float = 1800.0    ## air control
@export var air_friction: float = 400.0

@export_group("Jump")
@export var jump_velocity: float = 620.0
@export var double_jump_velocity: float = 540.0
@export var gravity: float = 1500.0
@export var fall_gravity_mult: float = 1.35      ## heavier fall = snappier arc
@export var max_fall_speed: float = 900.0
@export var jump_cut_mult: float = 0.45          ## variable jump height on release
@export var coyote_time: float = 0.10            ## grace after leaving ledge
@export var jump_buffer: float = 0.12            ## grace before landing
@export var max_air_jumps: int = 1               ## 1 = double jump

@export_group("Dash / Slide")
@export var dash_speed: float = 720.0
@export var dash_time: float = 0.18
@export var dash_cooldown: float = 0.4
@export var dash_invuln: float = 0.12            ## i-frames during dash
@export var slide_speed: float = 480.0
@export var slide_time: float = 0.35

@export_group("Wall")
@export var wall_slide_speed: float = 120.0
@export var wall_jump_velocity: Vector2 = Vector2(360, 560)
@export var wall_stick_time: float = 0.12

@export_group("Ledge")
@export var can_ledge_grab: bool = true
@export var climb_speed: float = 160.0
