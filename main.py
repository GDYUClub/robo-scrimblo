#!/usr/bin/env python3
import discord
from gescbot.gesc import Gesc
from api_key import apikey
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

intents = discord.Intents.default()

scheduler = AsyncIOScheduler()

intents.message_content = True
intents.members = True
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in')
    try:
        bot.load_extension('gescbot')
    except Exception as e:
        print(f'failed to load extension: {e}')

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def crash(ctx):
    await ctx.send("the gesc help command output should be above me")





bot.run(apikey)
