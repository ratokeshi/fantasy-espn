"""Tests for fantasy_espn.client.ESPNFantasyClient."""

import unittest
from unittest.mock import MagicMock, patch

from fantasy_espn.client import ESPNFantasyClient, ESPNFantasyError


def _mock_response(status_code=200, json_data=None, text=""):
    response = MagicMock()
    response.status_code = status_code
    response.ok = 200 <= status_code < 400
    response.text = text
    if json_data is None:
        response.json.side_effect = ValueError("no json")
    else:
        response.json.return_value = json_data
    return response


class ESPNFantasyClientTestCase(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.client = ESPNFantasyClient(
            league_id=123456,
            year=2024,
            espn_s2="s2-cookie",
            swid="{SWID}",
            session=self.session,
        )

    def test_base_url_contains_league_and_year(self):
        self.assertIn("123456", self.client._base_url)
        self.assertIn("2024", self.client._base_url)

    def test_cookies_included_when_present(self):
        self.assertEqual(
            self.client._cookies,
            {"espn_s2": "s2-cookie", "SWID": "{SWID}"},
        )

    def test_cookies_empty_when_public_league(self):
        client = ESPNFantasyClient(league_id=1, year=2024, session=self.session)
        self.assertEqual(client._cookies, {})

    def test_get_teams_returns_teams_list(self):
        self.session.get.return_value = _mock_response(
            json_data={"teams": [{"id": 1, "name": "Team A"}]}
        )
        teams = self.client.get_teams()
        self.assertEqual(teams, [{"id": 1, "name": "Team A"}])
        self.session.get.assert_called_once()
        _, kwargs = self.session.get.call_args
        self.assertEqual(kwargs["params"], {"view": ["mTeam"]})
        self.assertEqual(
            kwargs["cookies"], {"espn_s2": "s2-cookie", "SWID": "{SWID}"}
        )

    def test_get_matchups_with_week(self):
        self.session.get.return_value = _mock_response(
            json_data={"schedule": [{"id": 10}]}
        )
        matchups = self.client.get_matchups(week=3)
        self.assertEqual(matchups, [{"id": 10}])
        _, kwargs = self.session.get.call_args
        self.assertEqual(kwargs["params"]["scoringPeriodId"], 3)

    def test_unauthorized_raises_error(self):
        self.session.get.return_value = _mock_response(status_code=401)
        with self.assertRaisesRegex(ESPNFantasyError, "private"):
            self.client.get_teams()

    def test_not_found_raises_error(self):
        self.session.get.return_value = _mock_response(status_code=404)
        with self.assertRaisesRegex(ESPNFantasyError, "not found"):
            self.client.get_teams()

    def test_server_error_raises_error(self):
        self.session.get.return_value = _mock_response(
            status_code=500, text="boom"
        )
        with self.assertRaisesRegex(ESPNFantasyError, "500"):
            self.client.get_teams()

    def test_invalid_json_raises_error(self):
        self.session.get.return_value = _mock_response(status_code=200)
        with self.assertRaisesRegex(ESPNFantasyError, "valid JSON"):
            self.client.get_teams()

    def test_default_session_is_requests_session(self):
        with patch("fantasy_espn.client.requests.Session") as session_cls:
            ESPNFantasyClient(league_id=1, year=2024)
            session_cls.assert_called_once()


if __name__ == "__main__":
    unittest.main()
