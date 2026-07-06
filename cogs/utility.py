import asyncio
import random

import discord
from discord.ext import commands

from version import VERSION


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="ping", description="Check the bot's latency")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"Pong! `{round(self.bot.latency * 1000)}ms`")

    @discord.slash_command(name="version", description="Show the bot's current version")
    async def version(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"🤖 Running version `{VERSION}` — this is the latest version.")

    @discord.slash_command(name="userinfo", description="Show info about a user")
    async def userinfo(self, ctx: discord.ApplicationContext,
                       member: discord.Option(discord.Member, "The user to look up", required=False)):
        member = member or ctx.author
        embed = discord.Embed(title=f"User Info — {member}", color=discord.Color.blurple())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Joined Server", value=discord.utils.format_dt(member.joined_at), inline=True)
        embed.add_field(name="Account Created", value=discord.utils.format_dt(member.created_at), inline=True)
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        embed.add_field(name="Roles", value=", ".join(roles) if roles else "None", inline=False)
        fake_ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
        embed.add_field(name="FAKE IP (not real)", value=f"`FAKE IP: {fake_ip}`", inline=False)
        await ctx.respond(embed=embed)

    @discord.slash_command(name="serverinfo", description="Show info about this server")
    async def serverinfo(self, ctx: discord.ApplicationContext):
        guild = ctx.guild
        embed = discord.Embed(title=f"{guild.name}", color=discord.Color.green())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=str(guild.owner), inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
        await ctx.respond(embed=embed)

    @discord.slash_command(name="avatar", description="Get a user's avatar")
    async def avatar(self, ctx: discord.ApplicationContext,
                     member: discord.Option(discord.Member, "The user to look up", required=False)):
        member = member or ctx.author
        embed = discord.Embed(title=f"{member}'s avatar", color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar.url)
        await ctx.respond(embed=embed)

    @discord.slash_command(name="poll", description="Create a quick yes/no poll")
    async def poll(self, ctx: discord.ApplicationContext,
                   question: discord.Option(str, "The poll question")):
        embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.gold())
        embed.set_footer(text=f"Asked by {ctx.author}")
        await ctx.respond(embed=embed)
        message = await ctx.interaction.original_response()
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    @discord.slash_command(name="remind", description="Set a reminder")
    async def remind(self, ctx: discord.ApplicationContext,
                     minutes: discord.Option(float, "How many minutes from now"),
                     message: discord.Option(str, "What to remind you about")):
        await ctx.respond(f"⏰ Got it, I'll remind you in {minutes} minute(s).")

        async def send_reminder():
            await asyncio.sleep(minutes * 60)
            try:
                await ctx.author.send(f"⏰ Reminder: {message}")
            except discord.Forbidden:
                await ctx.channel.send(f"{ctx.author.mention} ⏰ Reminder: {message}")

        self.bot.loop.create_task(send_reminder())


def setup(bot: commands.Bot):
    bot.add_cog(Utility(bot))
