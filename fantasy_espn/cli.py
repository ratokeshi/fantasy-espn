"""Command line interface for fetching ESPN Fantasy Football data."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, List, Optional

from .client import ESPNFantasyClient, ESPNFantasyError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fantasy-espn",
        description="Fetch ESPN Fantasy Football data from the command line.",
    )
    parser.add_argument(
        "--league-id",
        type=int,
        default=_env_int("ESPN_LEAGUE_ID"),
        help="ESPN fantasy football league id (or set ESPN_LEAGUE_ID).",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=_env_int("ESPN_YEAR"),
        help="Season year, e.g. 2024 (or set ESPN_YEAR).",
    )
    parser.add_argument(
        "--espn-s2",
        default=os.environ.get("ESPN_S2"),
        help="espn_s2 cookie value for private leagues (or set ESPN_S2).",
    )
    parser.add_argument(
        "--swid",
        default=os.environ.get("ESPN_SWID"),
        help="SWID cookie value for private leagues (or set ESPN_SWID).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("teams", help="List teams in the league.")
    subparsers.add_parser("standings", help="Show league standings.")
    subparsers.add_parser("rosters", help="Show team rosters.")
    subparsers.add_parser("settings", help="Show league settings.")

    matchups_parser = subparsers.add_parser(
        "matchups", help="Show matchups/box scores."
    )
    matchups_parser.add_argument(
        "--week", type=int, default=None, help="Scoring period/week to fetch."
    )

    return parser


def _env_int(name: str) -> Optional[int]:
    value = os.environ.get(name)
    return int(value) if value else None


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.league_id or not args.year:
        parser.error(
            "--league-id and --year are required "
            "(or set ESPN_LEAGUE_ID/ESPN_YEAR)."
        )

    client = ESPNFantasyClient(
        league_id=args.league_id,
        year=args.year,
        espn_s2=args.espn_s2,
        swid=args.swid,
    )

    try:
        result: Any
        if args.command == "teams":
            result = client.get_teams()
        elif args.command == "standings":
            result = client.get_standings()
        elif args.command == "rosters":
            result = client.get_rosters()
        elif args.command == "settings":
            result = client.get_settings()
        elif args.command == "matchups":
            result = client.get_matchups(week=args.week)
        else:  # pragma: no cover - argparse enforces valid choices
            parser.error(f"Unknown command: {args.command}")
    except ESPNFantasyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
