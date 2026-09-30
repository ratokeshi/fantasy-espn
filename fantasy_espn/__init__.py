"""fantasy_espn: a small Python client for the ESPN Fantasy Football API."""

from .client import ESPNFantasyClient, ESPNFantasyError

__all__ = ["ESPNFantasyClient", "ESPNFantasyError"]

__version__ = "0.1.0"
