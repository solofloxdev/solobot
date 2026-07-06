import discord
from discord.ext import commands


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
        if not ctx.guild.voice_client:
            await ctx.respond("I'm not in a voice channel. Use `/join` first.", ephemeral=True)
            return
        if ctx.guild.id in self.recording:
            await ctx.respond("Already recording. Use `/stoprecord` to stop.", ephemeral=True)
            return

        await ctx.defer()
        self.recording[ctx.guild.id] = ctx.channel
        ctx.guild.voice_client.start_recording(
            discord.sinks.WaveSink(),
            self.finished_callback,
            ctx.channel,
        )
        await ctx.followup.send("🔴 Recording started. Use `/stoprecord` to stop and get the file.")

    @discord.slash_command(name="stoprecord", description="Stop recording and get the audio file")
    async def stoprecord(self, ctx: discord.ApplicationContext):
        if ctx.guild.id not in self.recording:
            await ctx.respond("Not currently recording.", ephemeral=True)
            return

        await ctx.defer()
        ctx.guild.voice_client.stop_recording()
        self.recording.pop(ctx.guild.id, None)
        await ctx.followup.send("⏹️ Recording stopped — sending file shortly.")


def setup(bot: commands.Bot):
    bot.add_cog(Record(bot))
