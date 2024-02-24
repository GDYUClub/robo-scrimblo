#!/usr/bin/env python3
import discord
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

intents = discord.Intents.default()

scheduler = AsyncIOScheduler()


class Gesc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gesc(self, ctx):
        await ctx.send('hello from the gesc file!')


def setup(bot):
  await bot.add_cog(Gesc(bot))
