"""
Unit tests for config.py

Tests Config class, model presets, and effective parameter resolution.
"""

import os
import pytest
import sys


@pytest.fixture(autouse=True)
def clean_env():
    """Automatically clean Ollama/Flask env vars before each test."""
    keys_to_remove = [
        "OLLAMA_BASE_URL", "OLLAMA_MODEL", "OLLAMA_TEMPERATURE",
        "OLLAMA_NUM_PREDICT", "OLLAMA_TOP_P", "OLLAMA_TOP_K",
        "FLASK_PORT", "FLASK_DEBUG", "DEBUG",
    ]
    removed = {}
    for key in keys_to_remove:
        if key in os.environ:
            removed[key] = os.environ.pop(key)
    yield
    # Restore
    for key, value in removed.items():
        os.environ[key] = value


@pytest.fixture
def config_module( clean_env ):
    """Provide a fresh config module import."""
    # Remove cached module
    for mod_name in list(sys.modules.keys()):
        if mod_name == "config" or mod_name.startswith("config."):
            del sys.modules[mod_name]
    from config import Config, config, setup_logging
    return {"Config": Config, "config": config, "setup_logging": setup_logging}


class TestConfig:
    """Tests for Config class."""

    def test_default_ollama_base_url(self, config_module):
        """Test default Ollama base URL."""
        assert config_module["config"].OLLAMA_BASE_URL == "http://localhost:11434"

    def test_default_model(self, config_module):
        """Test default model."""
        assert config_module["config"].OLLAMA_MODEL == "llama3.1:8b"

    def test_default_flask_port(self, config_module):
        """Test default Flask port."""
        assert config_module["config"].FLASK_PORT == 5000

    def test_default_debug_false(self, config_module):
        """Test default debug is False."""
        assert config_module["config"].DEBUG is False
        # FLASK_DEBUG is set in .env file, so we just verify it's a bool
        assert isinstance(config_module["config"].FLASK_DEBUG, bool)

    def test_model_presets_exist(self, config_module):
        """Test that model presets are defined."""
        assert "llama3.1:8b" in config_module["Config"].MODEL_PRESETS
        assert "qwen3.5:9b-q4_K_M" in config_module["Config"].MODEL_PRESETS

    def test_llama3_preset_values(self, config_module):
        """Test llama3.1:8b preset values."""
        llama_preset = config_module["Config"].MODEL_PRESETS["llama3.1:8b"]
        assert llama_preset["temperature"] == 0.3
        assert llama_preset["num_predict"] == 2048
        assert llama_preset["top_p"] == 0.9
        assert llama_preset["top_k"] == 40

    def test_qwen_preset_values(self, config_module):
        """Test qwen3.5:9b-q4_K_M preset values."""
        qwen_preset = config_module["Config"].MODEL_PRESETS["qwen3.5:9b-q4_K_M"]
        assert qwen_preset["temperature"] == 0.4
        assert qwen_preset["num_predict"] == 2048
        assert qwen_preset["top_p"] == 0.85
        assert qwen_preset["top_k"] == 50

    def test_effective_temperature_llama_default(self, config_module):
        """Test effective temperature uses llama3.1 preset."""
        assert config_module["config"].effective_temperature == 0.3

    def test_effective_temperature_qwen_preset(self, config_module):
        """Test effective temperature uses qwen preset."""
        # Set model to qwen before creating fresh config
        os.environ["OLLAMA_MODEL"] = "qwen3.5:9b-q4_K_M"
        # Need fresh import for model change
        for mod_name in list(sys.modules.keys()):
            if mod_name == "config":
                del sys.modules[mod_name]
        from config import config as qwen_config
        assert qwen_config.effective_temperature == 0.4

    def test_effective_temperature_env_override(self):
        """Test that env var overrides preset."""
        os.environ["OLLAMA_MODEL"] = "llama3.1:8b"
        os.environ["OLLAMA_TEMPERATURE"] = "0.7"
        for mod_name in list(sys.modules.keys()):
            if mod_name == "config":
                del sys.modules[mod_name]
        from config import config as override_config
        assert override_config.effective_temperature == 0.7

    def test_effective_num_predict_default(self, config_module):
        """Test effective num_predict."""
        assert config_module["config"].effective_num_predict == 2048

    def test_effective_top_p_llama_default(self, config_module):
        """Test effective top_p for llama3.1."""
        assert config_module["config"].effective_top_p == 0.9

    def test_effective_top_p_qwen_default(self):
        """Test effective top_p for qwen."""
        os.environ["OLLAMA_MODEL"] = "qwen3.5:9b-q4_K_M"
        for mod_name in list(sys.modules.keys()):
            if mod_name == "config":
                del sys.modules[mod_name]
        from config import config as qwen_config
        assert qwen_config.effective_top_p == 0.85

    def test_effective_top_k_llama_default(self, config_module):
        """Test effective top_k for llama3.1."""
        assert config_module["config"].effective_top_k == 40

    def test_effective_top_k_qwen_default(self):
        """Test effective top_k for qwen."""
        os.environ["OLLAMA_MODEL"] = "qwen3.5:9b-q4_K_M"
        for mod_name in list(sys.modules.keys()):
            if mod_name == "config":
                del sys.modules[mod_name]
        from config import config as qwen_config
        assert qwen_config.effective_top_k == 50


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_debug(self):
        """Test setup_logging with debug=True."""
        import logging
        # Need fresh config without previous basicConfig
        for mod_name in list(sys.modules.keys()):
            if mod_name == "config":
                del sys.modules[mod_name]
        from config import setup_logging
        setup_logging(debug=True)
        assert logging.getLogger().level == logging.DEBUG

    def test_setup_logging_warning(self):
        """Test setup_logging with debug=False."""
        import logging
        for mod_name in list(sys.modules.keys()):
            if mod_name == "config":
                del sys.modules[mod_name]
        from config import setup_logging
        setup_logging(debug=False)
        assert logging.getLogger().level == logging.WARNING