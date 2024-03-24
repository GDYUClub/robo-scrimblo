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
voteCollection = db['gescvotes']

vote_running = False
poll_msg_id = ''
user_vote_map = {}
has_voted = set()
active_members = set()
emote_to_game={}
game_to_votes={}
end_time = None

class Gesc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gesc(self, ctx):
        await ctx.send('hello from the gesc file!')

    @commands.command()
    async def geschelp(self, ctx):
        msg_content ="""
The GESC Vote bot allows us to automate voting for the Game Enthusiasts sub collective.\n
It features the following commands:
``!gescvote``: starts a new vote if there is no vote currently happening. Info must be formatted as follows:
``!gescvote(game1#emoji1$game2#emoji2$game3$emoji3$...,vote_durration)``
- you can have an unlimited number of games as votes
- vote duration is the number of hours you want the vote to last for
- make sure there are no spaces in the input
- if you want to use a server emote, you'll need to get it's ID, type it out with a \ to return it's id (but don't pass the \ into the command, like <:floomba:919982797018517515>)
``!gescend``: ends the current vote before the time limit
``!gescattended``: gives you extra voting power if you attended the last meeting, if you already voted the value will be updated, call this command again to remove your extra power.
- if you attended last meeting, your vote is worth 5, otherwise it's worth 3
"""
        await ctx.send(msg_content)

    @commands.command(aliases=['gescsv'])
    @commands.has_role('Executives')
    async def startvote(self, ctx):
        if vote_running:
            sent_message = await ctx.send("Vote already running, Use !gescendvote to end current vote")
            return
        #make sure it responds to messages from the same user in the same channel
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        #reset variables
        user_vote_map = {}
        has_voted = set()
        active_members = set()
        emote_to_game={}
        game_to_votes={}

        try:
            async def waitForGame():
                await ctx.send('Paste the Game and Emoji used to vote for it. If this is the last game reply with "done". Use the !geschelp command for a format reference:')
                message = await self.bot.wait_for('message', check=check, timeout=60.0)
                if message.content != 'done':
                    #check for formatting here
                    game = message.content.split('=')[0]
                    emote = message.content.split('=')[1]
                    emote_to_game[emote] = game
                    game_to_votes[game] = 0
                    print(game,emote)
                    return await waitForGame()
            await waitForGame()
            await ctx.send(f'you entered the following games: {emote_to_game}')
            await ctx.send(f'Enter the length of time of the vote, in hours')
            message = await self.bot.wait_for('message', check=check, timeout=60.0)
            #check if it's an positive interger
            time = message.content.strip()

            # calculate end time
            end_time = datetime.now() + timedelta(hours=hours)
            scheduler.add_job(end_vote, 'date', run_date=end_time, args=[message])







        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('consider this vote GONE')
            return




async def setup(bot):
    await bot.add_cog(Gesc(bot))
