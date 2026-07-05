import os

import discord
from discord import app_commands
from discord.ext import commands
from anthropic import AsyncAnthropic

SYSTEM_PROMPT = "You are a friendly, helpful Discord bot. Keep replies concise (a few sentences max) since this is a chat app, not an essay."
MAX_HISTORY = 10  # messages of context per channel

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.history: dict[int, list[dict]] = {}

    async def ask_claude(self, channel_id: int, user_message: str) -> str:
        history = self.history.setdefault(channel_id, [])
        history.append({"role": "user", "content": user_message})
        history[:] = history[-MAX_HISTORY:]

        response = await client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=history,
        )
        reply = response.content[0].text
        history.append({"role": "assistant", "content": reply})
        history[:] = history[-MAX_HISTORY:]
        return reply

    @app_commands.command(name="chat", description="Talk to the bot")
    @app_commands.describe(message="What you want to say")
    async def chat(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()
        try:
            reply = await self.ask_claude(interaction.channel_id, message)
        except Exception as e:
            reply = f"Sorry, something went wrong: {e}"
        await interaction.followup.send(reply)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        if not is_dm and self.bot.user not in message.mentions:
            return

        content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
        if not content:
            return
        async with message.channel.typing():
            try:
                reply = await self.ask_claude(message.channel.id, content)
            except Exception as e:
                reply = f"Sorry, something went wrong: {e}"
        await message.reply(reply, mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))
