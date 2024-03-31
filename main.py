#!/usr/bin/env python3
import discord
from env import apikey
from datetime import datetime, timedelta
from discord.ext import commands

intents = discord.Intents.default()

intents.message_content = True
intents.members = True
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in')
    try:
        await bot.load_extension('bounties')
        await bot.load_extension('gescbot')
    except Exception as e:
        print(f'failed to load extension: {e}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
        await ctx.send("You do not have the role required")

bot.run(apikey)
