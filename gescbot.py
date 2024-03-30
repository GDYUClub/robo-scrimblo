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


class Gesc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.current_poll_id = None

    # no context to call from
    #@commands.Cog.listener()
    #async def on_ready(self):
        #await self.updatecurrentpoll(self,"")

    @commands.command()
    async def gesc(self, ctx):
        await ctx.send('hello from the gesc file!')

    @commands.command()
    async def geschelp(self, ctx):
        msg_content ="""todo"""
        await ctx.send(msg_content)

    async def make_poll_msg(self,ctx,poll):
        print('make poll msg')
        #print(type(ctx),self(poll))
        vote_announcement = '\nNew GESC Vote for the following Games:\n'
        emote_to_game = poll['games']
        for emote in emote_to_game:
            output = f'{emote} -> {emote_to_game[emote]}\n'
            vote_announcement += output
        msg = ctx.send(vote_announcement)

        #if it's not a new poll then update the msg id
        if poll['msg_id'] == None:
            poll['msg_id'] = msg.id
        else:
            voteCollection.update_one({'_id':ObjectId(poll['_id'])},{'$set':{'msg_id':msg.id}})
            print('updated vote msg id')
        return msg


    @commands.command(aliases=['sp'])
    async def startpoll(self, ctx):
        if self.current_poll_id != None:
            sent_message = await ctx.send("Vote already running, Use !endpoll (!ep) to end current vote")
            return
        #make sure it responds to messages from the same user in the same channel
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        #variables
        user_vote_map = {}
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



            gescPoll = {
                "msg_id":None,
                "games":emote_to_game,
                "votes":game_to_votes,
                "member_votes": {},
                "members_active":list(),
                "current_poll": True
            }

            try:
                poll_msg = await self.make_poll_msg(ctx,gescPoll)
                poll_id = voteCollection.insert_one(gescPoll).inserted_id
                print(poll_id)
                self.current_poll_id = poll_id
            except Exception as error:
                print(error)
                msg.delete()
                await ctx.send('error pushing poll to database, poll creation aborted')



        except TimeoutError:
            await ctx.send('Sorry, you took too long to respond')
            await ctx.send('consider this vote GONE')
            return


    @commands.command(aliases=['ep'])
    async def endpoll(self,ctx):
        if self.current_poll_id == None:
            await ctx.send('no vote running, use geschelp for info on how to use the bot!!')
        poll = self.get_current_poll()
        game_to_votes = poll['games']
        highest = 0
        winning_game = max(game_to_votes, key=game_to_votes.get)
        output = winning_game
        higest = game_to_votes[winning_game]

        # check for tie
        for game in game_to_votes:
            if game_to_votes[game] == game_to_votes[winning_game] and game != winning_game:
                output = "A Tie"
        sent_message = await ctx.send(f"""Vote over!\n The winner is: {output}!\n{game_to_votes}""")
        voteCollection.update_one({'_id':ObjectId(self.current_poll_id)},{'$set':{'current_poll':False}})


    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        poll = self.get_current_poll()
        print(poll)
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        reaction = (f'{payload.emoji.name}')
        print(reaction, reaction == '🍕')

        print(user.bot,message.id != poll['msg_id'],reaction not in poll['games'])
        if user.bot or message.id != poll['msg_id'] or reaction not in poll['games']:
            return

        voted_game = poll['games'][reaction]
        print(voted_game)

        vote_power = 3
        if user.id in poll['members_active']:
            vote_power = 5

        # remove previous vote if already voted
        print(f'{user} voted')
        if user.id in poll['member_votes']:
            poll['votes'][poll['member_votes'][user.id]] -= vote_power



        # add vote
        if user.id not in poll['member_votes']:
            poll['member_votes'][user.id] = ''
        poll['member_votes'][user.id] = voted_game
        poll['votes'][voted_game] += vote_power
        message.channel.send(f'{member.display_name} voted')



    # pulls the current poll from the database and
    @commands.command(aliases=['sync'])
    async def synccurrentpoll(self, ctx):
        poll = voteCollection.find_one({'current_poll':True})
        print(poll)
        if poll == None:
            param_id = ctx[0]
            poll = voteCollection.find_one({'_id':ObjectId(param_id)})
            print(poll)
            if poll != None:
                self.current_poll_id = poll['_id']
                await ctx.send(f'synced vote based on current vote id {self.current_poll_id}')
            else:
                await ctx.send(f"couldn't sync vote. Make sure there is a currently active vote in the database.")

        else:
            self.current_poll_id = poll['_id']
            await ctx.send(f'synced vote based on current vote boolean {self.current_poll_id}')
        print('called above func')
        msg = await make_poll_msg(ctx,poll)

    async def get_current_poll():
            return voteCollection.find_one({'_id':ObjectId(self.current_poll_id)})



async def setup(bot):
    await bot.add_cog(Gesc(bot))
