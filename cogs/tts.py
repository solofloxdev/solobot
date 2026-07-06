import asyncio
import os
import tempfile

import discord
from discord.ext import commands
from gtts import gTTS


class TTS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="tts", description="Speak a message in the voice channel")
    async def tts(self, ctx: discord.ApplicationContext,
                  message: discord.Option(str, "What the bot should say")):
        if not ctx.guild.voice_client:
            await ctx.respond("I'm not in a voice channel. Use `/join` first.", ephemeral=True)
            return
        if ctx.guild.voice_client.is_playing():
            await ctx.respond("Already speaking, wait a moment.", ephemeral=True)
            return

        await ctx.defer()
        try:
            def generate():
                tts = gTTS(text=message, lang="en")
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tts.save(f.name)
                    return f.name

            loop = asyncio.get_event_loop()
            tmp_path = await loop.run_in_executor(None, generate)
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(tmp_path, executable="ffmpeg"), volume=1.5
            )
            ctx.guild.voice_client.play(source, after=lambda e: os.unlink(tmp_path))
            await ctx.followup.send(f"🔊 Speaking: *{message}*")
        except Exception as e:
            import traceback
            await ctx.followup.send(f"❌ Error: `{traceback.format_exc()[:1800]}`")


def setup(bot: commands.Bot):
    bot.add_cog(TTS(bot))
