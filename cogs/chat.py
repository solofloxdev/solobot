import asyncio
import io
import os
import tempfile

import discord
from discord.ext import commands
from anthropic import AsyncAnthropic
from gtts import gTTS

from cogs.users import load_notes

BASE_SYSTEM = "You are a friendly, helpful Discord bot. Keep replies concise (a few sentences max) since this is a chat app, not an essay."
MAX_HISTORY = 10

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def build_system_prompt(user_id: str = None) -> str:
    notes = load_notes()
    if not notes:
        return BASE_SYSTEM
    context = "\n\nKnown users:\n" + "\n".join(
        f"- {data.get('name', uid)} (ID: {uid}): {data['description']}"
        for uid, data in notes.items()
    )
    return BASE_SYSTEM + context


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.history: dict[int, list[dict]] = {}
        self.listening: dict[int, discord.TextChannel] = {}

    async def ask_claude(self, channel_id: int, user_message: str, user_id: str = None) -> str:
        history = self.history.setdefault(channel_id, [])
        history.append({"role": "user", "content": user_message})
        history[:] = history[-MAX_HISTORY:]

        response = await client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            system=build_system_prompt(user_id),
            messages=history,
        )
        reply = response.content[0].text
        history.append({"role": "assistant", "content": reply})
        history[:] = history[-MAX_HISTORY:]
        return reply

    async def speak_in_vc(self, guild: discord.Guild, text: str):
        vc = guild.voice_client
        if not vc or vc.is_playing():
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

    def is_vc_channel(self, channel) -> bool:
        return isinstance(channel, discord.VoiceChannel)

    @discord.slash_command(name="chat", description="Talk to the bot")
    async def chat(self, ctx: discord.ApplicationContext,
                   message: discord.Option(str, "What you want to say")):
        await ctx.defer()
        try:
            reply = await self.ask_claude(ctx.channel_id, message, str(ctx.author.id))
        except Exception as e:
            reply = f"Sorry, something went wrong: {e}"
        await ctx.followup.send(reply)
        if self.is_vc_channel(ctx.channel):
            await self.speak_in_vc(ctx.guild, reply)

    @discord.slash_command(name="listen", description="Start listening to voice and responding with TTS")
    async def listen(self, ctx: discord.ApplicationContext):
        vc = ctx.guild.voice_client
        if not vc:
            await ctx.respond("I'm not in a voice channel. Use `/join` first.", ephemeral=True)
            return
        if ctx.guild.id in self.listening:
            await ctx.respond("Already listening. Use `/stoplisten` to stop.", ephemeral=True)
            return

        await ctx.defer()
        for _ in range(26):
            if vc.is_connected():
                break
            await asyncio.sleep(0.3)
        else:
            await ctx.followup.send("❌ Voice connection not ready yet, try again in a moment.", ephemeral=True)
            return

        self.listening[ctx.guild.id] = ctx.channel
        try:
            vc.start_recording(discord.sinks.WaveSink(), self.finished_listening, ctx.channel)
        except Exception as e:
            self.listening.pop(ctx.guild.id, None)
            await ctx.followup.send(f"❌ Could not start listening: `{e}`", ephemeral=True)
            return
        await ctx.followup.send("👂 Listening... Use `/stoplisten` to stop and I'll respond to what was said.")

    @discord.slash_command(name="stoplisten", description="Stop listening and get an AI response")
    async def stoplisten(self, ctx: discord.ApplicationContext):
        if ctx.guild.id not in self.listening:
            await ctx.respond("Not currently listening.", ephemeral=True)
            return

        await ctx.defer()
        self.listening.pop(ctx.guild.id, None)
        try:
            ctx.guild.voice_client.stop_recording()
        except Exception as e:
            await ctx.followup.send(f"❌ Error: `{e}`", ephemeral=True)
            return
        await ctx.followup.send("⏹️ Processing voice...")

    async def finished_listening(self, sink: discord.sinks.WaveSink, channel: discord.TextChannel):
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        combined_text = []

        for user_id, audio in sink.audio_data.items():
            try:
                audio.file.seek(0)
                wav_data = audio.file.read()
                with sr.AudioFile(io.BytesIO(wav_data)) as source:
                    audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                if text.strip():
                    combined_text.append(text.strip())
            except Exception:
                continue

        if not combined_text:
            await channel.send("❌ Couldn't understand any speech.")
            return

        full_text = " ".join(combined_text)
        await channel.send(f"🎙️ Heard: *{full_text}*")

        reply = await self.ask_claude(channel.id, full_text)
        await channel.send(reply)

        if channel.guild.voice_client:
            await self.speak_in_vc(channel.guild, reply)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        is_vc = self.is_vc_channel(message.channel)

        if not is_dm and self.bot.user not in message.mentions:
            return

        content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
        if not content:
            return

        async with message.channel.typing():
            try:
                reply = await self.ask_claude(message.channel.id, content, str(message.author.id))
            except Exception as e:
                reply = f"Sorry, something went wrong: {e}"

        await message.reply(reply, mention_author=False)

        if is_vc and message.guild:
            await self.speak_in_vc(message.guild, reply)


def setup(bot: commands.Bot):
    bot.add_cog(Chat(bot))
