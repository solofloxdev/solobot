import asyncio
import random
import time

import discord
from discord import app_commands
from discord.ext import commands

from version import VERSION


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! `{round(self.bot.latency * 1000)}ms`")

    @app_commands.command(name="version", description="Show the bot's current version")
    async def version(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🤖 Running version `{VERSION}` — this is the latest version.")

    @app_commands.command(name="userinfo", description="Show info about a user")
    @app_commands.describe(member="The user to look up (defaults to you)")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"User Info — {member}", color=discord.Color.blurple())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Joined Server", value=discord.utils.format_dt(member.joined_at), inline=True)
        embed.add_field(name="Account Created", value=discord.utils.format_dt(member.created_at), inline=True)
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        embed.add_field(name="Roles", value=", ".join(roles) if roles else "None", inline=False)
        fake_ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
        embed.add_field(name="IP (not real)", value=f"`IP: {fake_ip}`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Show info about this server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"{guild.name}", color=discord.Color.green())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=str(guild.owner), inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(member="The user to look up (defaults to you)")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member}'s avatar", color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poll", description="Create a quick yes/no poll")
    @app_commands.describe(question="The poll question")
    async def poll(self, interaction: discord.Interaction, question: str):
        embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.gold())
        embed.set_footer(text=f"Asked by {interaction.user}")
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    @app_commands.command(name="remind", description="Set a reminder")
    @app_commands.describe(minutes="How many minutes from now", message="What to remind you about")
    async def remind(self, interaction: discord.Interaction, minutes: float, message: str):
        await interaction.response.send_message(
            f"⏰ Got it, I'll remind you in {minutes} minute(s)."
        )

        async def send_reminder():
            await asyncio.sleep(minutes * 60)
            try:
                await interaction.user.send(f"⏰ Reminder: {message}")
            except discord.Forbidden:
                await interaction.channel.send(f"{interaction.user.mention} ⏰ Reminder: {message}")

        self.bot.loop.create_task(send_reminder())


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
