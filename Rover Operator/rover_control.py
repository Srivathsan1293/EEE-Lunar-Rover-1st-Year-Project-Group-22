

import pygame
import sys
import json
import os
import argparse
import time

DEADZONE    = 0.08
TURN_SCALE  = 0.7
UPDATE_HZ   = 50
CONFIG_FILE = "joystick_map.json"


def apply_deadzone(value, threshold):
    return value if abs(value) > threshold else 0.0


def joystick_to_motors(forward, turn):
    left  = max(-1.0, min(1.0, forward + turn * TURN_SCALE))
    right = max(-1.0, min(1.0, forward - turn * TURN_SCALE))
    return left, right


def to_pwm(signed):
    return {
        "direction": 0 if signed >= 0 else 1,
        "speed": int(abs(signed) * 255),
    }



def wait_for_axis(js, prompt, threshold=0.5):
    print(f"\n  {prompt}")
    print("  Move that stick now...")
    # drain any existing movement first
    for _ in range(20):
        pygame.event.pump()
        time.sleep(0.05)
    baseline = [js.get_axis(i) for i in range(js.get_numaxes())]
    while True:
        pygame.event.pump()
        deltas = [(i, js.get_axis(i) - baseline[i]) for i in range(js.get_numaxes())]
        # pick the axis that moved the most
        i, delta = max(deltas, key=lambda x: abs(x[1]))
        if abs(delta) > threshold:
            invert = delta < 0
            print(f"  → Axis {i}  (invert={invert})")
            # wait for stick to return to centre
            while abs(js.get_axis(i) - baseline[i]) > 0.1:
                pygame.event.pump()
                time.sleep(0.02)
            return i, invert
        time.sleep(0.02)


def run_mapping_wizard(js):
    print("\n=== Axis Mapping Wizard ===\n")

    fwd_axis, fwd_invert = wait_for_axis(
        js, "FORWARD/BACK: Push the left stick all the way FORWARD (away from you)"
    )
    turn_axis, turn_invert = wait_for_axis(
        js, "STEERING: Push the left stick all the way to the RIGHT"
    )

    mapping = {
        "forward_axis":   fwd_axis,
        "forward_invert": fwd_invert,
        "turn_axis":      turn_axis,
        "turn_invert":    turn_invert,
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(mapping, f, indent=2)

    print(f"\nSaved to {CONFIG_FILE}: {mapping}")
    return mapping


def load_or_create_mapping(js):
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            mapping = json.load(f)
        print(f"Loaded mapping: {mapping}")
        return mapping
    print(f"No {CONFIG_FILE} found — running wizard...")
    return run_mapping_wizard(js)


def run(js, mapping):
    fwd_axis    = mapping["forward_axis"]
    fwd_invert  = mapping["forward_invert"]
    turn_axis   = mapping["turn_axis"]
    turn_invert = mapping["turn_invert"]

    clock = pygame.time.Clock()
    print("\nRunning — Ctrl+C to quit.\n")

    try:
        while True:
            pygame.event.pump()

            raw_fwd  = js.get_axis(fwd_axis)  * (-1 if fwd_invert  else 1)
            raw_turn = js.get_axis(turn_axis) * (-1 if turn_invert else 1)

            fwd  = apply_deadzone(raw_fwd,  DEADZONE)
            turn = apply_deadzone(raw_turn, DEADZONE)

            left_s, right_s = joystick_to_motors(fwd, turn)
            L = to_pwm(left_s)
            R = to_pwm(right_s)

            print(
                f"FWD={fwd:+.2f}  TURN={turn:+.2f}  │  "
                f"L dir={L['direction']} spd={L['speed']:3d}  │  "
                f"R dir={R['direction']} spd={R['speed']:3d}   ",
                end="\r",
            )

            clock.tick(UPDATE_HZ)

    except KeyboardInterrupt:
        print("\nStopped.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", action="store_true", help="Re-run the axis mapping wizard")
    args = parser.parse_args()

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller detected. Plug it in and try again.")
        sys.exit(1)

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"Controller: {js.get_name()}  ({js.get_numaxes()} axes)")

    if args.map:
        mapping = run_mapping_wizard(js)
    else:
        mapping = load_or_create_mapping(js)

    run(js, mapping)
    pygame.quit()


if __name__ == "__main__":
    main()