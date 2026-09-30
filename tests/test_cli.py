"""Tests for fantasy_espn.cli."""

import json
import unittest
from unittest.mock import patch

from fantasy_espn.cli import main
from fantasy_espn.client import ESPNFantasyError


class CLITestCase(unittest.TestCase):
    def test_main_requires_league_id_and_year(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["teams"])
        self.assertEqual(ctx.exception.code, 2)

    @patch("fantasy_espn.cli.ESPNFantasyClient")
    def test_teams_command_prints_json(self, client_cls):
        client_cls.return_value.get_teams.return_value = [{"id": 1}]
        with patch("sys.stdout") as mock_stdout:
            exit_code = main(
                ["--league-id", "1", "--year", "2024", "teams"]
            )
        self.assertEqual(exit_code, 0)
        client_cls.return_value.get_teams.assert_called_once()

    @patch("fantasy_espn.cli.ESPNFantasyClient")
    def test_matchups_command_passes_week(self, client_cls):
        client_cls.return_value.get_matchups.return_value = []
        exit_code = main(
            ["--league-id", "1", "--year", "2024", "matchups", "--week", "5"]
        )
        self.assertEqual(exit_code, 0)
        client_cls.return_value.get_matchups.assert_called_once_with(week=5)

    @patch("fantasy_espn.cli.ESPNFantasyClient")
    def test_error_from_client_returns_nonzero(self, client_cls):
        client_cls.return_value.get_teams.side_effect = ESPNFantasyError("nope")
        exit_code = main(["--league-id", "1", "--year", "2024", "teams"])
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
