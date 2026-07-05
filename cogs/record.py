import discord
from discord import app_commands
from discord.ext import commands
from discord.sinks import WaveSink


class Record(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.recording = {}

    async def finished_callback(self, sink, channel: discord.TextChannel):
        files = []
        for user_id, audio in sink.audio_data.items():
            audio.file.seek(0)
            files.append(discord.File(audio.file, filename=f"recording_{user_id}.wav"))

        if files:
            await channel.send("🎙️ Here's the recording:", files=files[:10])
        else:
            await channel.send("No audio was recorded.")

    @app_commands.command(name="record", description="Start recording the voice channel")
    async def record(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("I'm not in a voice channel. Use `/join` first.", ephemeral=True)
            return
        if interaction.guild.id in self.recording:
            await interaction.response.send_message("Already recording. Use `/stoprecord` to stop.", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            sink = WaveSink()
            self.recording[interaction.guild.id] = interaction.channel
            interaction.guild.voice_client.start_recording(sink, self.finished_callback, interaction.channel)
            await interaction.followup.send("🔴 Recording started. Use `/stoprecord` to stop and get the file.")
        except Exception as e:
            await interaction.followup.send(f"❌ Recording not supported: `{e}`")

    @app_commands.command(name="stoprecord", description="Stop recording and get the audio file")
    async def stoprecord(self, interaction: discord.Interaction):
        if interaction.guild.id not in self.recording:
            await interaction.response.send_message("Not currently recording.", ephemeral=True)
            return

        await interaction.response.defer()
        try:
            interaction.guild.voice_client.stop_recording()
        except Exception as e:
            await interaction.followup.send(f"❌ Error stopping: `{e}`")
            return
        self.recording.pop(interaction.guild.id, None)
        await interaction.followup.send("⏹️ Recording stopped — sending files shortly.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Record(bot))
