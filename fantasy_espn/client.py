"""Client for interacting with the (undocumented) ESPN Fantasy Football API.

This module provides a thin wrapper around the ESPN Fantasy Football
read API that is used by the ESPN Fantasy website itself. It supports
both public leagues (no authentication required) and private leagues
(which require the ``espn_s2`` and ``SWID`` cookies from a logged-in
browser session).

Example
-------
>>> from fantasy_espn import ESPNFantasyClient
>>> client = ESPNFantasyClient(league_id=123456, year=2024)
>>> league = client.get_league()
>>> teams = client.get_teams()
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}"


class ESPNFantasyError(Exception):
    """Raised when the ESPN Fantasy Football API returns an error."""


class ESPNFantasyClient:
    """A client for reading data from the ESPN Fantasy Football API.

    Parameters
    ----------
    league_id:
        The numeric ESPN fantasy football league id.
    year:
        The season year, e.g. ``2024``.
    espn_s2:
        The ``espn_s2`` cookie value, required for private leagues.
    swid:
        The ``SWID`` cookie value, required for private leagues.
    session:
        An optional :class:`requests.Session` to use for HTTP requests.
        Mostly useful for testing.
    """

    def __init__(
        self,
        league_id: int,
        year: int,
        espn_s2: Optional[str] = None,
        swid: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.league_id = league_id
        self.year = year
        self.espn_s2 = espn_s2
        self.swid = swid
        self.session = session or requests.Session()

    @property
    def _cookies(self) -> Dict[str, str]:
        cookies = {}
        if self.espn_s2:
            cookies["espn_s2"] = self.espn_s2
        if self.swid:
            cookies["SWID"] = self.swid
        return cookies

    @property
    def _base_url(self) -> str:
        return BASE_URL.format(year=self.year, league_id=self.league_id)

    def _get(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        response = self.session.get(
            self._base_url, params=params, cookies=self._cookies, timeout=10
        )
        if response.status_code == 401:
            raise ESPNFantasyError(
                "Unauthorized: this league is private. Provide valid "
                "'espn_s2' and 'swid' cookies."
            )
        if response.status_code == 404:
            raise ESPNFantasyError(
                f"League {self.league_id} not found for year {self.year}."
            )
        if not response.ok:
            raise ESPNFantasyError(
                f"ESPN API request failed with status {response.status_code}: "
                f"{response.text}"
            )
        try:
            return response.json()
        except ValueError as exc:
            raise ESPNFantasyError(
                "ESPN API returned a response that was not valid JSON."
            ) from exc

    def get_league(self, views: Optional[List[str]] = None) -> Dict[str, Any]:
        """Return raw league data for the requested ``views``.

        Common views include ``mTeam``, ``mRoster``, ``mMatchup``,
        ``mMatchupScore``, ``mSettings`` and ``mStandings``.
        """
        params = {"view": views} if views else None
        return self._get(params=params)

    def get_teams(self) -> List[Dict[str, Any]]:
        """Return the list of teams in the league."""
        data = self.get_league(views=["mTeam"])
        return data.get("teams", [])

    def get_standings(self) -> List[Dict[str, Any]]:
        """Return team standings (records, points for/against, etc.)."""
        data = self.get_league(views=["mTeam", "mStandings"])
        return data.get("teams", [])

    def get_rosters(self) -> List[Dict[str, Any]]:
        """Return the list of teams including their current rosters."""
        data = self.get_league(views=["mTeam", "mRoster"])
        return data.get("teams", [])

    def get_matchups(self, week: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return matchup/box score data, optionally filtered by ``week``."""
        params: Dict[str, Any] = {"view": ["mMatchup", "mMatchupScore"]}
        if week is not None:
            params["scoringPeriodId"] = week
        data = self._get(params=params)
        return data.get("schedule", [])

    def get_settings(self) -> Dict[str, Any]:
        """Return the league settings."""
        data = self.get_league(views=["mSettings"])
        return data.get("settings", {})
