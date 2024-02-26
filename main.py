#!/usr/bin/env python3
import discord
from api_key import apikey
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
    except Exception as e:
        print(f'failed to load extension: {e}')

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def crash(ctx):
    await ctx.send("the gesc help command output should be above me")





bot.run(apikey)
