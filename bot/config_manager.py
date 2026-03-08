import json
import os
import sys
from typing import Any, Dict, Optional
from bot.logger import get_logger

logger = get_logger("ConfigManager")

class ConfigManager:
    def __init__(self, config_path: str = "data/config.json", voices_path: str = "data/voices.json"):
        # Get project root (parent directory of 'bot')
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.root_dir, config_path)
        self.voices_path = os.path.join(self.root_dir, voices_path)
        self.ref_audio_dir = os.path.join(self.root_dir, "data", "ref_audios")
        
        self.config: Dict[str, Any] = {}
        self.voices: Dict[str, Any] = {}
        self.valid_voices: Dict[str, Any] = {}
        self.default_character: Optional[str] = None
        
        self.load_all()

    def load_all(self) -> None:
        self.load_config()
        self.load_voices()
        
        # Verify we have at least one valid voice
        if not self.valid_voices:
            logger.critical("No valid voice profiles found in voices.json or audio files are missing. Terminating.")
            sys.exit(1)
        
        # Set default to the first valid voice
        self.default_character = list(self.valid_voices.keys())[0]
        logger.info(f"Default character set to: {self.default_character}")

    def load_config(self) -> None:
        try:
            if not os.path.exists(self.config_path):
                logger.critical(f"Config file not found at {self.config_path}. Terminating.")
                sys.exit(1)
                
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            
            if "api_url" not in self.config:
                logger.critical("API URL not found in config.json. Terminating.")
                sys.exit(1)
                
            logger.info(f"Config loaded from {self.config_path}")
        except Exception as e:
            logger.critical(f"Error loading config: {e}")
            sys.exit(1)

    def load_voices(self) -> None:
        try:
            if not os.path.exists(self.voices_path):
                logger.critical(f"Voices file not found at {self.voices_path}. Terminating.")
                sys.exit(1)

            with open(self.voices_path, "r", encoding="utf-8") as f:
                self.voices = json.load(f)
            
            if not self.voices:
                logger.critical("Voices file is empty. Terminating.")
                sys.exit(1)

            logger.info(f"Voices loaded from {self.voices_path}")
            self.validate_voices()
        except Exception as e:
            logger.critical(f"Error loading voices: {e}")
            sys.exit(1)

    def validate_voices(self) -> None:
        self.valid_voices = {}
        invalid_voices = []

        for name, info in self.voices.items():
            ref_filename = info.get("ref_audio")
            if not ref_filename:
                invalid_voices.append(name)
                continue

            ref_path = os.path.join(self.ref_audio_dir, ref_filename)
            if os.path.exists(ref_path):
                self.valid_voices[name] = info
            else:
                logger.warning(f"Voice '{name}' reference file not found: {ref_path}")
                invalid_voices.append(name)
        
        if invalid_voices:
            logger.warning(f"Found {len(invalid_voices)} invalid voice profiles: {', '.join(invalid_voices)}")

    def get_voice(self, character_name: Optional[str] = None) -> Dict[str, Any]:
        # Use first valid character if none provided or character is invalid
        target = character_name if character_name in self.valid_voices else self.default_character
        
        voice_info = self.valid_voices.get(target)
        if voice_info:
            full_info = voice_info.copy()
            full_info["ref_audio"] = os.path.join(self.ref_audio_dir, voice_info["ref_audio"])
            return full_info
        return {}

    def get_api_params(self) -> Dict[str, Any]:
        # Do not include keys used by the bot itself
        exclude_keys = {"api_url", "default_character", "default_lang", "default_weights"}
        return {k: v for k, v in self.config.items() if k not in exclude_keys}

    def get_api_url(self) -> str:
        return self.config["api_url"]

    def get_default_character_name(self) -> str:
        """Returns the configured default character name, or the first valid one available."""
        config_default = self.config.get("default_character")
        if config_default in self.valid_voices:
            return config_default
        
        # Fallback to the first valid voice found
        if self.valid_voices:
            first_valid = list(self.valid_voices.keys())[0]
            if config_default:
                logger.info(f"Configured default '{config_default}' is invalid. Falling back to '{first_valid}'")
            return first_valid
            
        return ""
