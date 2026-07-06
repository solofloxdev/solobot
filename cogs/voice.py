import asyncio

import discord
from discord.ext import commands


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="join", description="Join your voice channel and keep it alive")
    async def join(self, ctx: discord.ApplicationContext):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.respond("You need to be in a voice channel first.", ephemeral=True)
            return

        await ctx.defer()
        channel = ctx.author.voice.channel

        try:
            if ctx.guild.voice_client:
                await ctx.guild.voice_client.move_to(channel)
            else:
                await asyncio.wait_for(channel.connect(), timeout=15)
            await ctx.followup.send(f"Joined **{channel.name}** — I'll keep it alive. 🔊")
        except asyncio.TimeoutError:
            await ctx.followup.send("❌ Timed out connecting to voice channel.")
        except Exception as e:
            await ctx.followup.send(f"❌ Error: `{e}`")

    @discord.slash_command(name="leave", description="Leave the voice channel")
    async def leave(self, ctx: discord.ApplicationContext):
        if not ctx.guild.voice_client:
            await ctx.respond("I'm not in a voice channel.", ephemeral=True)
            return
        channel_name = ctx.guild.voice_client.channel.name
        await ctx.guild.voice_client.disconnect()
        await ctx.respond(f"Left **{channel_name}**.")


def setup(bot: commands.Bot):
    bot.add_cog(Voice(bot))
