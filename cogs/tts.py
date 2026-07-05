import asyncio
import io
import os
import tempfile

import discord
from discord import app_commands
from discord.ext import commands
from gtts import gTTS


class TTS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="tts", description="Speak a message in the voice channel")
    @app_commands.describe(message="What the bot should say")
    async def tts(self, interaction: discord.Interaction, message: str):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("I'm not in a voice channel. Use `/join` first.", ephemeral=True)
            return
        if interaction.guild.voice_client.is_playing():
            await interaction.response.send_message("Already speaking, wait a moment.", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            def generate():
                tts = gTTS(text=message, lang="en")
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tts.save(f.name)
                    return f.name

            loop = asyncio.get_event_loop()
            tmp_path = await loop.run_in_executor(None, generate)

            source = discord.FFmpegPCMAudio(tmp_path)
            interaction.guild.voice_client.play(source, after=lambda e: os.unlink(tmp_path))
            await interaction.followup.send(f"🔊 Speaking: *{message}*")
        except Exception as e:
            await interaction.followup.send(f"❌ Error: `{e}`")


async def setup(bot: commands.Bot):
    await bot.add_cog(TTS(bot))
