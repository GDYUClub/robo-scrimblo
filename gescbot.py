#!/usr/bin/env python3
import discord
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from pymongo_get_db import get_database
from bson.objectid import ObjectId
import re

intents = discord.Intents.default()

intents.message_content = True
intents.members = True
intents.messages = True
intents.reactions = True

scheduler = AsyncIOScheduler()
db = get_database()
voteCollection = db['gescvotes']

#vote_running = False
#poll_msg_id = ''
#user_vote_map = {}
#has_voted = set()
#active_members = set()
#emote_to_game={}
#game_to_votes={}
#end_time = None
#current_poll_id = None

class Gesc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.vote_running = False
        self.poll_msg_id = ''
        self.user_vote_map = {}
        self.has_voted = set()
        self.active_members = set()
        self.emote_to_game={}
        self.game_to_votes={}
        self.end_time = None
        self.current_poll_id = None

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

            vote_announcement = '\nNew GESC Vote for the following Games:\n'
            for emote in emote_to_game:
                output = f'{emote} -> {emote_to_game[emote]}\n'
                vote_announcement += output

            poll_msg = await ctx.send(vote_announcement)
            poll_msg_id = poll_msg.id

            gescVote = {
                "msg_id":poll_msg_id,
                "games":emote_to_game,
                "votes":game_to_votes,
                "member_votes": {},
                "members_voted":list(),
                "members_active":list(),
                "current_vote": True
            }

            try:
                poll_id = voteCollection.insert_one(gescVote).inserted_id
                print(poll_id)
                self.current_poll_id = poll_id
            except Exception as error:
                print(error)
                await ctx.send('error pushing poll to database, the poll above is not real 😳')



        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('consider this vote GONE')
            return


    @commands.command(aliases=['gescev'])
    async def end_vote(self,ctx):
        if not vote_running:
            await ctx.send('no vote running, use geschelp for info on how to use the bot!!')
        highest = 0
        winning_game = max(client.vote_dict, key=client.vote_dict.get)
        output = winning_game
        higest = client.vote_dict[winning_game]

        # check for tie
        for game in client.vote_dict:
            if client.vote_dict[game] == client.vote_dict[winning_game] and game != winning_game:
                output = "A Tie"
        sent_message = await ctx.send(f"""Vote over!\n The winner is: {output}!\n{client.vote_dict}""")

    #@commands.Cog.listener()
    #async def on_raw_reaction_add(self,payload):
        #print(self.current_poll_id)
        #poll = voteCollection.find_one({'_id': ObjectId(self.current_poll_id)})
        #print(poll)
        #print(payload.message.id, poll["msg_id"])
        #if user.bot or reaction.message.id != poll_msg_id:
            #return
        #print('this is where the fun begins')


    @commands.Cog.listener()
    async def on_reaction_add(self,payload):
        print(self.current_poll_id)
        poll = voteCollection.find_one({'_id': ObjectId(self.current_poll_id)})
        print(poll)
        print(payload.message.id, poll["msg_id"])
        if user.bot or reaction.message.id != poll_msg_id:
            return
        print('this is where the fun begins')

    # pulls the current poll from the database and
    @commands.command(aliases=['gescsync'])
    async def updatecurrentpoll(self, ctx):
        poll = voteCollection.find_one({'current_vote':True})
        print(poll)
        if poll == None:
            param_id = ctx[0]
            poll = voteCollection.find_one({'_id':ObjectId(param_id)})
            print(poll)
            if poll != None:
                self.current_poll_id = poll['_id']
                await ctx.send(f'synced vote based on current vote id {self.current_poll_id}')
        else:
            self.current_poll_id = poll['_id']
            await ctx.send(f'synced vote based on current vote boolean {self.current_poll_id}')





async def setup(bot):
    await bot.add_cog(Gesc(bot))
