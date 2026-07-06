import asyncio

import discord
from discord import app_commands
from discord.ext import commands


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="join", description="Join your voice channel and keep it alive")
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("You need to be in a voice channel first.", ephemeral=True)
            return

        await interaction.response.defer()
        channel = interaction.user.voice.channel

        try:
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.move_to(channel)
            else:
                await asyncio.wait_for(channel.connect(self_deaf=False, self_mute=False), timeout=15)
            await interaction.followup.send(f"Joined **{channel.name}** — I'll keep it alive. 🔊")
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Timed out connecting to voice — check the bot has Connect permission in that channel.")
        except Exception as e:
            await interaction.followup.send(f"❌ Error: `{e}`")

    @app_commands.command(name="leave", description="Leave the voice channel")
    async def leave(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)
            return

        await interaction.response.defer()
        channel_name = interaction.guild.voice_client.channel.name
        await interaction.guild.voice_client.disconnect()
        await interaction.followup.send(f"Left **{channel_name}**.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Voice(bot))
