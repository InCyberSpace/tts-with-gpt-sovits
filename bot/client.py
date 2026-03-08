import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from typing import Optional, List
from bot.config_manager import ConfigManager
from bot.tts_client import TTSClient
from bot.logger import get_logger
from bot.utils import save_temp_wav, cleanup_file, boost_volume

logger = get_logger("DiscordBot")

class TTSCommands(commands.Cog):
    volume_boost_db = 1

    def __init__(self, bot: 'TTSBot'):
        self.bot = bot

    async def _generate_and_get_temp_path(self, text: str, lang: Optional[str]) -> Optional[str]:
        """Helper to generate TTS, boost volume, and return the temp file path."""
        text_lang = lang or self.bot.config_manager.config.get("default_lang", "ko")
        audio_data = await self.bot.tts_client.generate_tts(text, text_lang, self.bot.current_character)
        
        if audio_data:
            try:
                temp_path = save_temp_wav(audio_data)
                boost_volume(temp_path, TTSCommands.volume_boost_db)
                return temp_path
            except Exception as e:
                logger.error(f"Error saving auto-TTS temp file: {e}")
        return None

    async def _play_audio(self, interaction: discord.Interaction, audio_data: bytes, text: str):
        """Helper to handle the audio playback process."""
        temp_path = None
        try:
            temp_path = save_temp_wav(audio_data)
            boost_volume(temp_path, TTSCommands.volume_boost_db)
            
            # Verify file exists and has size
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) < 100:
                logger.error(f"Generated file {temp_path} is invalid or too small.")
                await interaction.followup.send("Generated audio is invalid.")
                if temp_path: cleanup_file(temp_path)
                return

            source = discord.FFmpegPCMAudio(temp_path)
            
            def after_playing(error):
                if error: logger.error(f"Playback error: {error}")
                if temp_path: cleanup_file(temp_path)
                self.bot.is_playing = False

            if not interaction.guild.voice_client.is_playing():
                interaction.guild.voice_client.play(source, after=after_playing)
                self.bot.is_playing = True
                await interaction.followup.send(f"Playing: {text[:100]}", file=discord.File(temp_path, filename="audio.wav"))
            else:
                cleanup_file(temp_path)
                await interaction.followup.send("Already playing audio, please wait.")
        
        except Exception as e:
            logger.error(f"Error in _play_audio: {e}")
            if temp_path: cleanup_file(temp_path)
            await interaction.followup.send(f"Playback error: {e}")

    @app_commands.command(name="join", description="Joins your current voice channel.")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await interaction.response.defer()
            try:
                if interaction.guild.voice_client:
                    await interaction.guild.voice_client.move_to(channel)
                else:
                    await asyncio.wait_for(channel.connect(timeout=15.0), timeout=20.0)
                await interaction.followup.send(f"Joined {channel}")
            except Exception as e:
                logger.error(f"Error in join: {e}")
                await interaction.followup.send(f"Failed to join: {e}")
        else:
            await interaction.response.send_message("You are not in a voice channel!", ephemeral=True)

    @app_commands.command(name="say", description="Synthesizes text and sends it as an audio file.")
    @app_commands.describe(text="The text to synthesize.", lang="The language of the text.")
    @app_commands.choices(lang=[
        app_commands.Choice(name="Chinese (zh)", value="zh"),
        app_commands.Choice(name="English (en)", value="en"),
        app_commands.Choice(name="Japanese (ja)", value="ja"),
        app_commands.Choice(name="Korean (ko)", value="ko")
    ])
    async def say(self, interaction: discord.Interaction, text: str, lang: Optional[str] = None):
        """Synthesizes text and sends it as a wav file. NO voice channel required."""
        await interaction.response.defer()
        temp_path = await self._generate_and_get_temp_path(text, lang)
        
        if temp_path:
            await interaction.followup.send(file=discord.File(temp_path, filename="tts.wav"))
            try: os.remove(temp_path)
            except: pass
        else:
            await interaction.followup.send("Failed to generate TTS.")

    @app_commands.command(name="voice", description="Changes the current voice character.")
    @app_commands.describe(character_name="The name of the character to use.")
    async def voice(self, interaction: discord.Interaction, character_name: Optional[str] = None):
        available_voices = list(self.bot.config_manager.valid_voices.keys())
        if character_name is None:
            return await interaction.response.send_message(f"Current voice: **{self.bot.current_character}**\nAvailable: {', '.join(available_voices)}")
        if character_name in self.bot.config_manager.valid_voices:
            self.bot.current_character = character_name
            await self.bot.set_character_weights(character_name)
            await interaction.response.send_message(f"Character changed to: **{character_name}**")
        else:
            await interaction.response.send_message(f"Voice '{character_name}' not found. Available: {', '.join(available_voices)}", ephemeral=True)

    @voice.autocomplete('character_name')
    async def voice_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        voices = list(self.bot.config_manager.valid_voices.keys())
        return [app_commands.Choice(name=v, value=v) for v in voices if current.lower() in v.lower()][:25]

    @app_commands.command(name="lang", description="Changes the default language for TTS.")
    @app_commands.describe(lang="The language code (zh, en, ja, ko).")
    @app_commands.choices(lang=[
        app_commands.Choice(name="Chinese (zh)", value="zh"),
        app_commands.Choice(name="English (en)", value="en"),
        app_commands.Choice(name="Japanese (ja)", value="ja"),
        app_commands.Choice(name="Korean (ko)", value="ko")
    ])
    async def lang(self, interaction: discord.Interaction, lang: str):
        self.bot.config_manager.config["default_lang"] = lang
        await interaction.response.send_message(f"Default language changed to: **{lang}**")
        logger.info(f"Default language changed to: {lang}")

    @app_commands.command(name="reload", description="Reloads configuration.")
    async def reload(self, interaction: discord.Interaction):
        self.bot.config_manager.load_all()
        await interaction.response.send_message("Configuration reloaded.")

class TTSBot(commands.Bot):
    def __init__(self, config_manager: ConfigManager, tts_client: TTSClient):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.config_manager = config_manager
        self.tts_client = tts_client
        self.current_character: str = config_manager.get_default_character_name()

    async def set_character_weights(self, character_name: str):
        """Sets the GPT and SoVITS weights for the character, falling back to defaults."""
        voice_info = self.config_manager.get_voice(character_name)
        weights = voice_info.get("weights")
        if not weights:
            weights = self.config_manager.config.get("default_weights")
        
        if weights:
            gpt_w = weights.get("gpt_weight")
            sovits_w = weights.get("sovits_weight")
            if gpt_w:
                await self.tts_client.set_gpt_weights(gpt_w)
            if sovits_w:
                await self.tts_client.set_sovits_weights(sovits_w)

    async def setup_hook(self):
        await self.add_cog(TTSCommands(self))
        
        # Apply weights for the initial character
        await self.set_character_weights(self.current_character)

        # Sync globally
        synced = await self.tree.sync()
        logger.info(f"Slash commands synced globally: {len(synced)} commands.")

    async def on_ready(self):
        logger.info(f"Bot logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        
        # Check if bot is in a voice channel in this guild
        vc = message.guild.voice_client
        if vc and vc.is_connected():
            # Only play if the user is in the same voice channel
            if message.author.voice and message.author.voice.channel == vc.channel:
                # Basic cleaning: ignore messages starting with command prefix
                if message.content.startswith(self.command_prefix): return
                
                logger.info(f"Auto-TTS for {message.author}: {message.content}")
                
                # We need to find the cog to use the helper
                cog = self.get_cog("TTSCommands")
                if cog:
                    temp_path = await cog._generate_and_get_temp_path(message.content, None)
                    if temp_path:
                        source = discord.FFmpegPCMAudio(temp_path)
                        def after_playing(error):
                            try: os.remove(temp_path)
                            except: pass
                        
                        # Use a small lock or check if already playing to avoid overlapping
                        # Note: This simple version won't queue, it will skip if busy
                        if not vc.is_playing():
                            vc.play(source, after=after_playing)
                        else:
                            try: os.remove(temp_path)
                            except: pass

        await self.process_commands(message)
