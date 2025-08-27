"""
Tests for configuration management
"""

import pytest
from src.config import Config, get_config


def test_default_config():
    """Test that default configuration loads correctly"""
    config = Config.from_yaml('nonexistent_file.yaml')
    assert config.scraper.base_url == "https://www.flashscore.co.uk/football/italy/serie-a-"
    assert config.model.random_state == 42
    assert config.data.max_missing_percentage == 20.0


def test_get_config():
    """Test global configuration access"""
    config = get_config()
    assert isinstance(config, Config)
    assert config.scraper.headless is True
