import aiohttp
from typing import Optional, Dict, Any
from bot.config_manager import ConfigManager
from bot.logger import get_logger

logger = get_logger("TTSClient")

class TTSClient:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    async def set_gpt_weights(self, weights_path: str) -> bool:
        url = f"{self.config_manager.get_api_url()}/set_gpt_weights"
        params = {"weights_path": weights_path}
        logger.info(f"Setting GPT weights to: {weights_path}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        logger.info("GPT weights set successfully.")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Failed to set GPT weights: {error}")
                        return False
        except Exception as e:
            logger.error(f"Error connecting to TTS API to set GPT weights: {e}")
            return False

    async def set_sovits_weights(self, weights_path: str) -> bool:
        url = f"{self.config_manager.get_api_url()}/set_sovits_weights"
        params = {"weights_path": weights_path}
        logger.info(f"Setting SoVITS weights to: {weights_path}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        logger.info("SoVITS weights set successfully.")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Failed to set SoVITS weights: {error}")
                        return False
        except Exception as e:
            logger.error(f"Error connecting to TTS API to set SoVITS weights: {e}")
            return False

    async def generate_tts(self, text: str, text_lang: str, character_name: str) -> Optional[bytes]:
        url = f"{self.config_manager.get_api_url()}/tts"
        voice_info = self.config_manager.get_voice(character_name)
        
        if not voice_info:
            logger.error(f"Voice info for {character_name} not found.")
            return None

        payload: Dict[str, Any] = self.config_manager.get_api_params()
        payload.update({
            "text": text,
            "text_lang": text_lang,
            "ref_audio_path": voice_info.get("ref_audio"),
            "prompt_text": voice_info.get("prompt_text"),
            "prompt_lang": voice_info.get("prompt_lang"),
            "media_type": "wav"  # Explicitly request wav
        })

        logger.info(f"Requesting TTS (POST) from {url} for text: {text[:50]}...")

        try:
            timeout = aiohttp.ClientTimeout(total=60) 
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.read()
                        
                        # VALIDATION: Check for RIFF/WAV header
                        if not data.startswith(b'RIFF'):
                            logger.error(f"Received invalid audio data. First 100 bytes: {data[:100]!r}")
                            return None
                            
                        return data
                    else:
                        try:
                            error_detail = await response.json()
                        except:
                            error_detail = await response.text()
                        logger.error(f"TTS API Error ({response.status}): {error_detail}")
                        return None
        except Exception as e:
            logger.error(f"Error connecting to TTS API: {e}")
            return None
