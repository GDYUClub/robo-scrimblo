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


async def setup(bot):
    await bot.add_cog(Gesc(bot))
