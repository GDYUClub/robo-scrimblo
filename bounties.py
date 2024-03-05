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
    async def createbounty(self,ctx, title, points, deadlinestr):
        deadline = datetime
        if len(title) < 1:
            await ctx.send('ERROR: Invalid title')
            await ctx.send('bounty creation aborted')
            return
        try:
            int(points)
        except:
            await ctx.send('ERROR: point not interger')
            await ctx.send('bounty creation aborted')
            return
        if int(points) < 1:
            await ctx.send('ERROR: point value lower than 0')
            await ctx.send('bounty creation aborted')
            return

        try:
            year = int(deadlinestr[:4])
            month = int(deadlinestr[5:7])
            day = int(deadlinestr[8:10])
            hour = int(deadlinestr[11:13])
            minute = int(deadlinestr[14:16])
            deadline = datetime(year,month, day, hour, minute)
        except:
            await ctx.send('ERROR: Invalid Deadline Date')
            await ctx.send('bounty creation aborted')
            return

        await ctx.send('please paste the description of the bounty')
        try:
            # Wait for a message that meets the condition
            description = await self.bot.wait_for('message',timeout=60.0)
        except Exception as error:
            # no description pasted in 60 seconds
            await ctx.send(f"error occurred {error}")
            await ctx.send('Sorry, you took too long to respond.')
            await ctx.send('bounty creation aborted')
            return
        else:
            if len(description.content) < 1:
                await ctx.send('invalid description')
                return

            await ctx.send(f'title: {title}\n scrimbuck value: {points}\n deadline: {deadline}\n description: {description.content}')

        await ctx.send('confirm? (y/n)')
        try:
            # Wait for a message that meets the condition
            message = await self.bot.wait_for('message',timeout=60.0)
        except Exception as error:
            # no description pasted in 60 seconds
            await ctx.send(f"error occurred {error}")
            await ctx.send('Sorry, you took too long to respond.')
            await ctx.send('bounty creation aborted')
            return
        else:
            if message.content == 'y':
                #make bounty
                await ctx.send('bounty created, database id is (id)')
                return
            if message.content == 'n':
                await ctx.send('bounty creation aborted')
                return
            else:
                await ctx.send('ERROR: invalid response, bounty creation aborted')
                return



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
