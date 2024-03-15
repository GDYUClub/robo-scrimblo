#!/usr/bin/env python3
import discord
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from pymongo_get_db import get_database

intents = discord.Intents.default()

scheduler = AsyncIOScheduler()

db = get_database()
bountyCollection = db['bounties']

class BountyCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bountytest(self, ctx):
        await ctx.send('hello from the bounty file!')

    @commands.command()
    @commands.has_role('Executives')
    async def createbounty(self, ctx):
        #make sure it responds to messages from the same user in the same channel
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        async def waitForTitle():
            await ctx.send('Paste bounty **Title** [String]:')
            message = await self.bot.wait_for('message', check=check, timeout=60.0)

            if len(message.content.strip()) < 1:
                await ctx.send('Invalid title')
                return await waitForTitle()
            else:
                return message.content.strip()

        try:
            title = await waitForTitle()
        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('Bounty creation aborted')
            return
        
        async def waitForDesc():
            await ctx.send('Paste bounty **Description** [String]:')
            message = await self.bot.wait_for('message', check=check, timeout=60.0)

            if len(message.content.strip()) < 1:
                await ctx.send('Invalid description')
                return await waitForDesc()
            else:
                return message.content.strip()

        try:
            description = await waitForDesc()
        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('Bounty creation aborted')
            return
        
        async def waitForPoints():
            await ctx.send('Paste bounty reward **Scrimbucks** [Integer]:')
            message = await self.bot.wait_for('message', check=check, timeout=60.0)
            try:
                return int(message.content.strip())
            except Exception as error:
                print(error)
                await ctx.send('Invalid points value')
                return await waitForPoints()                

        try:
            points = await waitForPoints()
        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('Bounty creation aborted')
            return
        
        async def waitForDeadline():
            await ctx.send('Paste bounty **Deadline** [yyyy-mm-dd hh:mm pp]:')
            message = await self.bot.wait_for('message', check=check, timeout=60.0)
            try:
                return datetime.strptime(message.content.strip(), '%Y-%m-%d %I:%M %p')
            except Exception as error:
                print(error)
                await ctx.send('Invalid deadline value')
                return await waitForDeadline()

        try:
            deadline = await waitForDeadline()
        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('Bounty creation aborted')
            return
        
        await ctx.send(f'**Title**: {title}\n**Description**: {description}\n**Scrimbucks**: {points}\n**Deadline**: {deadline.strftime("%Y-%m-%d %I:%M %p")}')
        
        await ctx.send('Confirm? (y/n)')
        try:
            message = await self.bot.wait_for('message',check=check,timeout=60.0)
        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('Bounty creation aborted')
            return
        else:
            if message.content.strip().lower() == 'y':
                bounty = {
                    "title": title,
                    "description": description,
                    "reward": points,
                    "deadline": deadline
                }
                try:
                    new_id = bountyCollection.insert_one(bounty).inserted_id
                    await ctx.send('Bounty created')
                    await ctx.send(f'Id: {new_id}')
                except Exception as error:
                    print(error)
                    await ctx.send('Bounty creation aborted')
            elif message.content.strip().lower() == 'n':
                await ctx.send('Bounty creation aborted')
                return
            else:
                await ctx.send('Invalid response, bounty creation aborted')
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

async def setup(bot):
    await bot.add_cog(BountyCog(bot))
