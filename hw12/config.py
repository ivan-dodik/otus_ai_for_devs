import logging
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Ollama configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))
    OLLAMA_NUM_PREDICT: int = int(os.getenv("OLLAMA_NUM_PREDICT", "4096"))
    OLLAMA_TOP_P: float = float(os.getenv("OLLAMA_TOP_P", "0.9"))
    OLLAMA_TOP_K: int = int(os.getenv("OLLAMA_TOP_K", "40"))
    OLLAMA_REQUEST_TIMEOUT: int = int(os.getenv("OLLAMA_REQUEST_TIMEOUT", "300"))

    # Flask configuration
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Debug logging
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Model-specific presets (applied automatically when model name matches)
    MODEL_PRESETS: dict = {
        "llama3.1:8b": {
            "temperature": 0.3,
            "num_predict": 2048,
            "top_p": 0.9,
            "top_k": 40,
        },
        "qwen3.5:9b-q4_K_M": {
            "temperature": 0.4,
            "num_predict": 2048,
            "top_p": 0.85,
            "top_k": 50,
        },
    }

    @property
    def effective_temperature(self) -> float:
        """Return temperature, overridden by model preset if configured."""
        env_val = os.getenv("OLLAMA_TEMPERATURE")
        if env_val is not None:
            return float(env_val)
        # Check model preset
        for preset_name, preset in self.MODEL_PRESETS.items():
            if preset_name in self.OLLAMA_MODEL:
                return preset["temperature"]
        return self.OLLAMA_TEMPERATURE

    @property
    def effective_num_predict(self) -> int:
        """Return num_predict, overridden by model preset if configured."""
        env_val = os.getenv("OLLAMA_NUM_PREDICT")
        if env_val is not None:
            return int(env_val)
        for preset_name, preset in self.MODEL_PRESETS.items():
            if preset_name in self.OLLAMA_MODEL:
                return preset["num_predict"]
        return self.OLLAMA_NUM_PREDICT

    @property
    def effective_top_p(self) -> float:
        """Return top_p, overridden by model preset if configured."""
        env_val = os.getenv("OLLAMA_TOP_P")
        if env_val is not None:
            return float(env_val)
        for preset_name, preset in self.MODEL_PRESETS.items():
            if preset_name in self.OLLAMA_MODEL:
                return preset["top_p"]
        return self.OLLAMA_TOP_P

    @property
    def effective_top_k(self) -> int:
        """Return top_k, overridden by model preset if configured."""
        env_val = os.getenv("OLLAMA_TOP_K")
        if env_val is not None:
            return int(env_val)
        for preset_name, preset in self.MODEL_PRESETS.items():
            if preset_name in self.OLLAMA_MODEL:
                return preset["top_k"]
        return self.OLLAMA_TOP_K


config = Config()


def setup_logging(debug: bool | None = None) -> None:
    """
    Настройка логирования.

    Args:
        debug: Если True — уровень DEBUG, если False — WARNING,
               если None — используется config.DEBUG.
    """
    if debug is None:
        debug = config.DEBUG

    level = logging.DEBUG if debug else logging.WARNING

    # force=True перезаписывает любую предыдущую конфигурацию корневого логгера
    # (Python 3.8+). Это гарантирует, что --debug флаг из CLI сработает,
    # даже если logging.basicConfig() уже был вызван ранее при импортах.
    logging.basicConfig(
        format="%(message)s",
        level=level,
        force=True,
    )