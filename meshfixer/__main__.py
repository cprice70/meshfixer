import argparse
import dataclasses
import json
import sys
from pathlib import Path

from meshfixer.diagnostics import analyze_mesh
from meshfixer.formats import UnsupportedFormatError, load_mesh, save_mesh
from meshfixer.repair import RepairConfig, repair_mesh


def cmd_diagnose(args: argparse.Namespace) -> int:
    path = Path(args.file)
    try:
        ms = load_mesh(path)
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 3
    except UnsupportedFormatError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    stats = analyze_mesh(ms)

    if args.json:
        print(json.dumps(dataclasses.asdict(stats)))
        return 0

    print(f"File:               {path}")
    print(f"Triangles:          {stats.triangle_count:,}")
    print(f"Vertices:           {stats.vertex_count:,}")
    print(f"Watertight:         {'Yes' if stats.is_watertight else 'No'}")
    print(f"Holes:              {stats.hole_count}")
    print(f"Non-manifold edges: {stats.non_manifold_edge_count}")
    print(f"Non-manifold verts: {stats.non_manifold_vertex_count}")
    print(f"Degenerate faces:   {stats.degenerate_face_count}")
    bb = stats.bounding_box
    print(f"Bounding box:       {bb[0]:.3f} x {bb[1]:.3f} x {bb[2]:.3f}")
    return 0


def cmd_repair(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_stem(input_path.stem + "_fixed")

    try:
        ms = load_mesh(input_path)
    except FileNotFoundError:
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        return 3
    except UnsupportedFormatError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    config = RepairConfig(
        close_holes=not args.skip_hole_fill,
        max_hole_size=args.max_hole_size,
    )
    result = repair_mesh(ms, config)

    if not result.success:
        for w in result.warnings:
            print(f"Warning: {w}", file=sys.stderr)
        print("Repair failed.", file=sys.stderr)
        return 2

    try:
        save_mesh(ms, output_path)
    except UnsupportedFormatError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Repaired: {output_path}")
    for w in result.warnings:
        print(f"Warning: {w}")
    return 0


def cmd_gui(_args: argparse.Namespace) -> int:
    from meshfixer.gui.app import run_app
    return run_app()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="meshfixer",
        description="Repair broken STL and 3MF mesh files.",
    )
    sub = parser.add_subparsers(dest="command")

    p_diag = sub.add_parser("diagnose", help="Analyze mesh without repairing")
    p_diag.add_argument("file")
    p_diag.add_argument("--json", action="store_true", help="Output as JSON")

    p_rep = sub.add_parser("repair", help="Repair mesh file")
    p_rep.add_argument("input")
    p_rep.add_argument("output", nargs="?")
    p_rep.add_argument("--skip-hole-fill", action="store_true")
    p_rep.add_argument("--max-hole-size", type=int, default=30)

    sub.add_parser("gui", help="Launch graphical interface")

    args = parser.parse_args()

    if args.command == "diagnose":
        sys.exit(cmd_diagnose(args))
    elif args.command == "repair":
        sys.exit(cmd_repair(args))
    else:
        sys.exit(cmd_gui(args))


if __name__ == "__main__":
    main()
