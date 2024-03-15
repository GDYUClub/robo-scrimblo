#!/usr/bin/env python3
import discord
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from pymongo_get_db import get_database
from bson.objectid import ObjectId

intents = discord.Intents.default()

scheduler = AsyncIOScheduler()

db = get_database()
bountyCollection = db['bounties']

bounty_forum_id = "1211484206027509810"

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
        
        try:
            async def waitForTitle():
                await ctx.send('Paste bounty **Title** [String]:')
                message = await self.bot.wait_for('message', check=check, timeout=60.0)

                if len(message.content.strip()) < 1:
                    await ctx.send('Invalid title')
                    return await waitForTitle()
                else:
                    return message.content.strip()

            title = await waitForTitle()

            async def waitForDesc():
                await ctx.send('Paste bounty **Description** [String]:')
                message = await self.bot.wait_for('message', check=check, timeout=60.0)

                if len(message.content.strip()) < 1:
                    await ctx.send('Invalid description')
                    return await waitForDesc()
                else:
                    return message.content.strip()

            description = await waitForDesc()
            
            async def waitForReward():
                await ctx.send('Paste bounty **Scrimbucks Reward** [Integer]:')
                message = await self.bot.wait_for('message', check=check, timeout=60.0)
                try:
                    return int(message.content.strip())
                except Exception as error:
                    print(error)
                    await ctx.send('Invalid reward value')
                    return await waitForReward()

            reward = await waitForReward()
            
            async def waitForDeadline():
                await ctx.send('Paste bounty **Deadline** [yyyy-mm-dd hh:mm pp]:')
                message = await self.bot.wait_for('message', check=check, timeout=60.0)
                try:
                    return datetime.strptime(message.content.strip(), '%Y-%m-%d %I:%M %p')
                except Exception as error:
                    print(error)
                    await ctx.send('Invalid deadline value')
                    return await waitForDeadline()

            deadline = await waitForDeadline()

            await ctx.send(f'**Title**: {title}\n**Description**: {description}\n**Scrimbucks Reward**: {reward}\n**Deadline**: <t:{int(deadline.timestamp())}:F>')
            
            async def forumPost():
                forum_channel = self.bot.get_channel(int(bounty_forum_id))

                if forum_channel is not None:
                    thread = await forum_channel.create_thread(
                        name=title,
                        content=f'**Description**: {description}\n**Scrimbucks Reward**: {reward}\n**Deadline**: <t:{int(deadline.timestamp())}:F>',
                    )
                    await ctx.send(f"Bounty thread: https://discord.com/channels/{thread.message.guild.id}/{thread.thread.id}")
                    return thread.thread.id
                else:
                    await ctx.send('Forum channel not found.')
                    await ctx.send('Bounty creation partially aborted')

            await ctx.send('Confirm? (y/n)')
            
            message = await self.bot.wait_for('message',check=check,timeout=60.0)
            
            if message.content.strip().lower() == 'y':
                thread_id = await forumPost()
                bounty = {
                    "title": title,
                    "description": description,
                    "reward": reward,
                    "deadline": deadline,
                    "thread_id": thread_id
                }
                try:
                    new_id = bountyCollection.insert_one(bounty).inserted_id
                    await ctx.send(f'Id: {new_id}')
                except Exception as error:
                    print(error)
                    await ctx.send('Bounty creation partially aborted')
            elif message.content.strip().lower() == 'n':
                await ctx.send('Bounty creation aborted')
            else:
                await ctx.send('Invalid response, bounty creation aborted')
        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('Bounty creation aborted')
            return

    @commands.command()
    async def deletebounty(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        try:
            async def waitForId():
                await ctx.send('Paste bounty **Id** [String]:')
                message = await self.bot.wait_for('message', check=check, timeout=60.0)
                if len(message.content.strip()) < 1:
                    await ctx.send('Invalid id')
                    return await waitForId()
                else:
                    return message.content.strip()
            
            bounty_id = await waitForId()

            async def forumDelete(thread_id):
                thread = self.bot.get_channel(int(bounty_forum_id)).get_thread(int(thread_id))

                if thread is not None:
                    await thread.delete()
                else:
                    await ctx.send('Forum channel or thread not found.')
                    await ctx.send('Bounty deletion partially aborted')
            
            await ctx.send('Confirm? (y/n)')

            message = await self.bot.wait_for('message',check=check,timeout=60.0)

            if message.content.strip().lower() == 'y':
                try:
                    deleted_bounty = bountyCollection.find_one_and_delete({'_id': ObjectId(bounty_id)})

                    if deleted_bounty is not None:
                        await forumDelete(deleted_bounty['thread_id'])
                        await ctx.send('Bounty deleted')
                    else:
                        await ctx.send('Invalid id, bounty deletion aborted')
                except Exception as error:
                    print(error)
                    await ctx.send('Bounty deletion aborted')
            elif message.content.strip().lower() == 'n':
                await ctx.send('Bounty deletion aborted')
            else:
                await ctx.send('Invalid response, bounty creation aborted')
        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('Bounty creation aborted')
            return

    @commands.command()
    async def bountyleaderboard(self, ctx, n):
        # checks the current scrimbuck amounts of the top n users
        pass

async def setup(bot):
    await bot.add_cog(BountyCog(bot))
