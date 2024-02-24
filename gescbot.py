#!/usr/bin/env python3
import discord
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

intents = discord.Intents.default()

scheduler = AsyncIOScheduler()

vote_running = False
poll_msg_id = ''
user_vote_map = {}
has_voted = set()
active_members = set()

class Gesc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gesc(self, ctx):
        await ctx.send('hello from the gesc file!')

    @commands.command()
    async def gesc(self, ctx):
        await ctx.send('hello from the gesc file!')


async def setup(bot):
    await bot.add_cog(Gesc(bot))
