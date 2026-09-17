#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import re
import sys

from shaders import handle_find_shaders
from particles import handle_convert_particle_systems

COMMANDS = {
    "find-shaders": {
        "desc": "Find shaders referenced in a scene. This is non-exhaustive and does not cover shaders created at runtime. Apply -r to recurse through all .unity files and materials.",
        "aliases": ["find_shaders"],
        "args": [
            {
                "type": "flag",
                "name": "-r",
                "long_name": "--recurse",
                "help": "Recurse through all files in the base directory."
            },
        ]
    },
    "convert-particle-systems": {
        "desc": "Convert (most) info related to legacy particle systems to their modern equivalents. One object at a time. sorey",
        "aliases": ["convert_particle_systems", "convert_ps"],
        "args": [
            {
                "type": "positional",
                "name": "class_name",
                "input_type": str,
                "help": "The object name to search for."
            }
        ]
    }
}

def main():
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='''
            Script to analyze Unity files.
        ''',
    )
    parser.add_argument("target", type=Path)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-i", "--ignore_warnings", action="store_true")

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    for name, info in COMMANDS.items():
        ps = subparsers.add_parser(
            name,
            aliases=info["aliases"],
            help=info["desc"],
            description=info["desc"],
        )
        if "args" in info:
            for a in info["args"]:
                if a["type"] == "flag":
                    ps.add_argument(a["name"], a["long_name"], action="store_true")
                elif a["type"] == "positional":
                    ps.add_argument(a["name"], type=a["input_type"])

    args = parser.parse_args()

    if not args.target.exists:
        print("Target file or directory doesn't exist; exiting...")
        sys.exit(1)        

    for name, info in COMMANDS.items():
        # set up aliases to canonical names
        if args.command in [name, *info["aliases"]]:
            args.command = name
            break

    match args.command:
        case "find-shaders":
            handle_find_shaders(args)

        case "convert-particle-systems":
            handle_convert_particle_systems(args)

if __name__ == "__main__":
    main()
