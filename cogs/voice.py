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

        channel = ctx.author.voice.channel
        await ctx.respond(f"Joining **{channel.name}**... 🔊", ephemeral=True)
        try:
            if ctx.guild.voice_client:
                await ctx.guild.voice_client.move_to(channel)
            else:
                await channel.connect()
        except Exception as e:
            await ctx.send_followup(f"❌ Error: `{e}`", ephemeral=True)

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
