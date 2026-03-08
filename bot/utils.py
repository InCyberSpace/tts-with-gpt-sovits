import os
import tempfile
import subprocess
from bot.logger import get_logger

logger = get_logger("Cleanup")

def save_temp_wav(data: bytes) -> str:
    """Saves bytes to a temp file and returns the path."""
    fd, path = tempfile.mkstemp(suffix=".wav")
    try:
        with os.fdopen(fd, 'wb') as tmp:
            tmp.write(data)
        logger.info(f"Saved temp audio to {path} ({len(data)} bytes)")
        return path
    except Exception as e:
        logger.error(f"Error saving temp audio: {e}")
        if os.path.exists(path):
            os.remove(path)
        raise e

def boost_volume(path: str, db: int) -> bool:
    temp_boosted = path + ".boosted.wav"
    try:
        # Run ffmpeg to boost volume
        cmd = [
            'ffmpeg', '-y', '-i', path,
            '-filter:a', f'volume={db}dB',
            temp_boosted
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Replace original with boosted
        os.replace(temp_boosted, path)
        logger.info(f"Successfully boosted volume of {path} by {db}dB")
        return True
    except Exception as e:
        logger.error(f"Failed to boost volume for {path}: {e}")
        if os.path.exists(temp_boosted):
            os.remove(temp_boosted)
        return False

def cleanup_file(path: str) -> None:
    """Safely removes a file."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Cleaned up file: {path}")
    except Exception as e:
        logger.error(f"Failed to cleanup file {path}: {e}")
