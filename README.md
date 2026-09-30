# fantasy-espn
ESPN Fantasy automation

A small Python application for interacting with the (undocumented) ESPN
Fantasy Football API to retrieve league, team, roster, and matchup data.

## Installation

```bash
pip install -e .
```

## Usage

### As a library

```python
from fantasy_espn import ESPNFantasyClient

client = ESPNFantasyClient(league_id=123456, year=2024)
teams = client.get_teams()
standings = client.get_standings()
rosters = client.get_rosters()
matchups = client.get_matchups(week=1)
settings = client.get_settings()
```

For **private leagues**, pass the `espn_s2` and `swid` cookie values from a
logged-in browser session:

```python
client = ESPNFantasyClient(
    league_id=123456,
    year=2024,
    espn_s2="<espn_s2 cookie value>",
    swid="<SWID cookie value>",
)
```

### As a CLI

```bash
fantasy-espn --league-id 123456 --year 2024 teams
fantasy-espn --league-id 123456 --year 2024 standings
fantasy-espn --league-id 123456 --year 2024 rosters
fantasy-espn --league-id 123456 --year 2024 matchups --week 1
fantasy-espn --league-id 123456 --year 2024 settings
```

`--league-id` and `--year` may also be provided via the `ESPN_LEAGUE_ID` and
`ESPN_YEAR` environment variables, and `--espn-s2`/`--swid` via `ESPN_S2` and
`ESPN_SWID`, respectively.

## Running tests

```bash
pip install -e .[dev]
pytest
```
