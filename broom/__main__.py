import argparse
import sys
from pathlib import Path

import broom


def main_root(ns: argparse.Namespace) -> int:
    rem = (lambda *_: None) if ns.dry_run else broom.remove

    types = broom.Clean.NONE
    for t in ns.types:
        types |= broom.Clean[t.upper()]

    for flags, path in broom.clean(ns.folders, types):
        print(f"{"|".join(flag.name.lower() for flag in flags)}: {path}")
        rem(path)

    return 0


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    def as_path(arg: str) -> Path:
        return Path(arg).resolve()

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands that would be executed, but do not execute them.",
    )

    parser.add_argument(
        "-t",
        "--type",
        dest="types",
        action="append",
        default=[],
        choices=[flag.name.lower() for flag in broom.Clean],
    )

    parser.add_argument(
        "folders",
        nargs="*",
        type=as_path,
        default=[Path.cwd()],
        help="Top levels roots to start the cleaning from.",
    )

    parser.set_defaults(entrypoint=main_root)

    return parser.parse_args()


def main() -> int:
    ns = cli()
    return ns.entrypoint(ns)


if __name__ == "__main__":
    sys.exit(main())
