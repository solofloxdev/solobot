import asyncio
import os
import tempfile

import discord
from discord.ext import commands
from gtts import gTTS



async def speak(guild: discord.Guild, text: str):
    vc = guild.voice_client
    if not vc:
        return
    try:
        def generate():
            tts = gTTS(text=text, lang="en")
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tts.save(f.name)
                return f.name
        loop = asyncio.get_event_loop()
        tmp_path = await loop.run_in_executor(None, generate)
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(tmp_path, executable="ffmpeg"), volume=1.5
        )
        vc.play(source, after=lambda e: os.unlink(tmp_path))
    except Exception:
        pass


class Record(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.recording = {}

    async def finished_callback(self, sink: discord.sinks.WaveSink, channel: discord.TextChannel):
        files = []
        for user_id, audio in sink.audio_data.items():
            audio.file.seek(0)
            files.append(discord.File(audio.file, filename=f"recording_{user_id}.wav"))
        if files:
            await channel.send("🎙️ Here's the recording:", files=files[:10])
        else:
            await channel.send("No audio was recorded.")

    @discord.slash_command(name="record", description="Start recording the voice channel")
    async def record(self, ctx: discord.ApplicationContext):
        vc = ctx.guild.voice_client
        if not vc:
            await ctx.respond("I'm not in a voice channel. Use `/join` first.", ephemeral=True)
            return
        if ctx.guild.id in self.recording:
            await ctx.respond("Already recording.", ephemeral=True)
            return

        await ctx.defer()
        self.recording[ctx.guild.id] = ctx.channel
        for attempt in range(5):
            try:
                vc.start_recording(discord.sinks.WaveSink(), self.finished_callback, ctx.channel)
                break
            except discord.sinks.errors.RecordingException as e:
                if "Not connected" in str(e) and attempt < 4:
                    await asyncio.sleep(1)
                else:
                    self.recording.pop(ctx.guild.id, None)
                    await ctx.followup.send(f"❌ Could not start recording: `{e}`", ephemeral=True)
                    return
        await ctx.followup.send("🔴", ephemeral=True)
        await speak(ctx.guild, "soloflox activated R mode")

    @discord.slash_command(name="stoprecord", description="Stop recording and get the audio file")
    async def stoprecord(self, ctx: discord.ApplicationContext):
        if ctx.guild.id not in self.recording:
            await ctx.respond("Not currently recording.", ephemeral=True)
            return

        await ctx.defer()
        self.recording.pop(ctx.guild.id, None)
        try:
            ctx.guild.voice_client.stop_recording()
        except Exception as e:
            await ctx.followup.send(f"❌ Error stopping: `{e}`", ephemeral=True)
            return
        await ctx.followup.send("⏹️", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Record(bot))
