import json
import os

import discord
from discord.ext import commands

NOTES_FILE = "user_notes.json"


def load_notes() -> dict:
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_notes(notes: dict):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)


class Users(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="adduser", description="Add a note/description for a user")
    async def adduser(self, ctx: discord.ApplicationContext,
                      user_id: discord.Option(str, "The user's Discord ID"),
                      description: discord.Option(str, "Your understanding/description of this user")):
        notes = load_notes()
        notes[user_id] = {"description": description}

        try:
            user = await self.bot.fetch_user(int(user_id))
            notes[user_id]["name"] = str(user)
        except Exception:
            notes[user_id]["name"] = f"User {user_id}"

        save_notes(notes)
        await ctx.respond(f"✅ Saved note for **{notes[user_id]['name']}**: {description}")

    @discord.slash_command(name="getuser", description="Get the note for a user")
    async def getuser(self, ctx: discord.ApplicationContext,
                      user_id: discord.Option(str, "The user's Discord ID")):
        notes = load_notes()
        if user_id not in notes:
            await ctx.respond("No note found for that user ID.", ephemeral=True)
            return
        note = notes[user_id]
        embed = discord.Embed(title=f"Note — {note.get('name', user_id)}", color=discord.Color.blurple())
        embed.add_field(name="Description", value=note["description"])
        await ctx.respond(embed=embed)

    @discord.slash_command(name="removeuser", description="Remove a user note")
    async def removeuser(self, ctx: discord.ApplicationContext,
                         user_id: discord.Option(str, "The user's Discord ID")):
        notes = load_notes()
        if user_id not in notes:
            await ctx.respond("No note found for that user ID.", ephemeral=True)
            return
        name = notes[user_id].get("name", user_id)
        del notes[user_id]
        save_notes(notes)
        await ctx.respond(f"🗑️ Removed note for **{name}**.")

    @discord.slash_command(name="listusers", description="List all saved user notes")
    async def listusers(self, ctx: discord.ApplicationContext):
        notes = load_notes()
        if not notes:
            await ctx.respond("No user notes saved yet.", ephemeral=True)
            return
        embed = discord.Embed(title="Saved User Notes", color=discord.Color.green())
        for uid, data in notes.items():
            embed.add_field(
                name=data.get("name", uid),
                value=f"ID: `{uid}`\n{data['description']}",
                inline=False
            )
        await ctx.respond(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Users(bot))
