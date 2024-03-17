#!/usr/bin/env python3
import discord
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from pymongo_get_db import get_database
from bson.objectid import ObjectId
import re

intents = discord.Intents.default()

scheduler = AsyncIOScheduler()

db = get_database()
bountyCollection = db['bounties']
scrimbucksCollection = db['scrimbucks']

bounty_forum_id = "1211484206027509810"

class BountyCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bountytest(self, ctx):
        await ctx.send('hello from the bounty file!')

    @commands.command(aliases=['cb'])
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

    @commands.command(aliases=['db'])
    @commands.has_role('Executives')
    async def deletebounty(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        try:
            async def waitForId():
                await ctx.send('Bounty **Id** [String]:')
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
                await ctx.send('Invalid response, bounty deletion aborted')
        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('Bounty deletion aborted')
            return

    @commands.command(aliases=['sb'])
    async def scrimbucks(self, ctx):
        try:
            scrimbuck_data = scrimbucksCollection.find_one({'discord_user_id': ctx.author.id})
            if scrimbuck_data is not None:
                await ctx.send(f"**Scrimbucks:** {scrimbuck_data['scrimbucks']}")
            else:
                await ctx.send(f'**Scrimbucks:** 0')
        except Exception as error:
            print(error)
            await ctx.send('Scrimbucks aborted')

    @commands.command(aliases=['bl'])
    async def bountyleaderboard(self, ctx):
        try:
            leaderboard = ''
            index = 1
            for scrimbuck_data in scrimbucksCollection.find().sort("scrimbucks", -1):
                user = self.bot.get_user(scrimbuck_data['discord_user_id'])
                guild = self.bot.get_guild(ctx.message.guild.id)
                member = guild.get_member(user.id)

                leaderboard += f"{index:<3}{member.display_name:<32} {scrimbuck_data['scrimbucks']}\n"
                index += 1

            await ctx.send(f"```{'   Username':<33}Scrimbucks\n-------------------------------------------\n{leaderboard}```")
        except Exception as error:
            print(error)
            await ctx.send('Bounty leaderboard aborted')

    @commands.command(aliases=['gs'])
    @commands.has_role('Executives')
    async def givescrimbucks(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            async def waitForId():
                await ctx.send('**Discord User** [@username]:')
                message = await self.bot.wait_for('message', check=check, timeout=60.0)
                try:
                    user = self.bot.get_user(int(re.sub("[^0-9]", "", message.content.strip())))
                    if user is not None:
                        return user
                    else:
                        await ctx.send('Invalid user id')
                        return await waitForId()
                except Exception as error:
                    print(error)
                    await ctx.send('Invalid user id')
                    return await waitForId()
            
            user = await waitForId()

            async def waitForAmount():
                await ctx.send('**Scrimbucks Amount** [Integer]:')
                message = await self.bot.wait_for('message', check=check, timeout=60.0)
                try:
                    return int(message.content.strip())
                except Exception as error:
                    print(error)
                    await ctx.send('Invalid value')
                    return await waitForAmount()
                
            amount = await waitForAmount()

            await ctx.send(f'**Discord Username**: {user.display_name}\n**Scrimbucks:** {amount}')
                     
            await ctx.send('Confirm? (y/n)')

            message = await self.bot.wait_for('message',check=check,timeout=60.0)

            if message.content.strip().lower() == 'y':
                try:
                    scrimbucksCollection.update_one({'discord_user_id': user.id}, {'$inc': {'scrimbucks': amount}}, upsert=True)

                    await ctx.send('Scrimbucks given')
                except Exception as error:
                    print(error)
                    await ctx.send('Give scrimbucks aborted')
            elif message.content.strip().lower() == 'n':
                await ctx.send('Give scrimbucks aborted')
            else:
                await ctx.send('Invalid response, give scrimbucks aborted')
        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('Give scrimbucks aborted')
            return

async def setup(bot):
    await bot.add_cog(BountyCog(bot))
