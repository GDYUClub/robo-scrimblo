#!/usr/bin/env python3
import discord
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

intents = discord.Intents.default()

scheduler = AsyncIOScheduler()

class BountyCog(commands.Cog):


    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bountytest(self, ctx):
        await ctx.send('hello from the bounty file!')

    @commands.command()
    async def createbounty(self,ctx):
        #it'll be interactive and stuff
        #ask them for all the info then run the bounty constructor
        #pass that into the mongo db
        pass

    @commands.command()
    async def clearedbounty(self, ctx,user,bounty):
        pass

    @commands.command()
    async def bountyleaderboard(self, ctx, n):
        # checks the current scrimbuck amounts of the top n users
        pass

    @commands.command()
    async def postinforum(self, ctx):
        FORUM_ID = "1211484206027509810"
        FORUM_CHANNEL = self.bot.get_channel(int(FORUM_ID))

        if FORUM_CHANNEL is not None:
            THREAD = await FORUM_CHANNEL.create_thread(name="robo's first thread2",content="wow look at what he can do",)
            await ctx.send(f"new thread created: {THREAD}")

        else:
            await ctx.send('Forum channel not found.')



class Bounty:
    def __init__(self, title, message, points, deadline):
        self.title = title
        self.message = message
        self.points = points
        self.deadline = deadline




async def setup(bot):
    await bot.add_cog(BountyCog(bot))
