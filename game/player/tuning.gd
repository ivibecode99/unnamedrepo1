class_name Tuning
extends RefCounted
## Movement constants. Tweak here; tests assert on derived jump heights.
const RUN_SPEED := 9.0
const ACCEL := 45.0
const DECEL := 55.0
const AIR_ACCEL := 28.0
const GRAVITY := 34.0
const MAX_FALL := 38.0
const JUMP_V := [11.5, 13.5, 17.5]      # single / double / triple
const JUMP_CHAIN_TIME := 0.28
const COYOTE := 0.12
const JUMP_BUFFER := 0.12
const JUMP_CUT := 0.5
const LONG_JUMP_SPEED := 15.0
const LONG_JUMP_V := 9.0
const WALL_JUMP_V := 14.0
const WALL_JUMP_PUSH := 9.0
const WALL_SLIDE := 4.0
const DIVE_SPEED := 14.0
const DIVE_V := 5.5
const POUND_V := -42.0
const POUND_HANG := 0.22
const ROLL_SPEED := 14.5
const ROLL_TIME := 0.55
const SPIN_TIME := 0.5
const SWIM_SPEED := 6.5
const HAT_RANGE := 11.0
const HAT_SPEED := 22.0
const HAT_BOUNCE_V := 15.0
const INVULN := 1.4
const CROUCH_SPEED := 3.0
const ICE_ACCEL := 5.0
const ICE_DECEL := 2.0

static func jump_height(v: float) -> float:
	return v * v / (2.0 * GRAVITY)
