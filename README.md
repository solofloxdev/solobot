# General-Purpose Discord Bot

A Python (discord.py) bot with general utility slash commands: `/ping`, `/userinfo`, `/serverinfo`, `/avatar`, `/poll`, `/remind`.

## 1. Create the bot application (and set a custom icon)

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**.
2. Give it a name, then on the **General Information** page upload an image under **App Icon** — this is your bot's custom icon/avatar everywhere it's used.
3. Go to the **Bot** tab → click **Reset Token** → copy the token (you'll only see it once).
4. Under **Privileged Gateway Intents**, enable **Server Members Intent** and **Message Content Intent** (required for `/userinfo` and message-based features).

## 2. Install dependencies

```bash
cd discord-bot
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## 3. Configure your token

Copy `.env.example` to `.env` and paste in your bot token:

```
DISCORD_TOKEN=your_bot_token_here
```

## 4. Invite the bot to a server

In the Developer Portal, go to **OAuth2 > URL Generator**:
- Scopes: `bot`, `applications.commands`
- Bot Permissions: `Send Messages`, `Read Message History`, `Add Reactions`, `Embed Links` (add more as needed)

Open the generated URL and add the bot to a server. Repeat for any other server you want it in — it's the same bot everywhere ("usable anywhere" you invite it).

## 5. Run the bot

```bash
python bot.py
```

Slash commands sync automatically on startup (may take up to a minute to appear in Discord).

## Adding more commands

Drop new cogs into the `cogs/` folder following the pattern in `cogs/utility.py` — each file's `setup()` function is auto-loaded on startup.
