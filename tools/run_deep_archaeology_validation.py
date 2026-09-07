"""Directly assemble all three gigantic Deepworks archaeology families in a fresh world."""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_server  # noqa: E402


SITES = (
    ("deep_quarry", 2048, 2048),
    ("elder_kings_tomb", 2560, 2048),
    ("faultwork", 3072, 2048),
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="deep-archaeology-grand")
    ap.add_argument("--level-name", default="deep-archaeology-grand-validation")
    ap.add_argument("--heap", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--only", choices=[sid for sid, _x, _z in SITES])
    args = ap.parse_args()
    commands = [(75, "say Deep archaeology direct-assembly validation started")]
    for sid, x, z in SITES:
        if args.only and sid != args.only:
            continue
        commands.extend([
            (2, f"execute in mythicbotany:alfheim run forceload add {x - 112} {z - 112} {x + 112} {z + 112}"),
            (18, f"execute in mythicbotany:alfheim run place structure alfheim:{sid} {x} -40 {z}"),
            (18, f"say placed {sid}"),
        ])
    commands.extend([(5, "save-all flush"), (8, "stop")])
    return run_server.run(args.seed, args.level_name, args.heap, commands, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
