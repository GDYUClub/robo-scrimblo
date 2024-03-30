#!/usr/bin/env python3
import discord
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from pymongo_get_db import get_database
from bson.objectid import ObjectId
import re
import emoji

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
        msg = await ctx.send(vote_announcement)
        for emote in emote_to_game:
            await msg.add_reaction(emote)

            pass



        #if it's not a new poll then update the msg id
        if poll['msg_id'] == None:
            poll['msg_id'] = msg.id
        else:
            old_msg = await ctx.fetch_message(poll['msg_id'])
            await old_msg.delete()
            voteCollection.update_one({'_id':ObjectId(poll['_id'])},{'$set':{'msg_id':msg.id}})
            print('updated vote msg id')
        return msg


    @commands.has_role('Executives')
    @commands.command(aliases=['gescc'])
    async def startpoll(self, ctx):
        if self.current_poll_id != None:
            sent_message = await ctx.send("Vote already running, Use !gescd to end current vote")
            return
        #make sure it responds to messages from the same user in the same channel
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        #variables
        user_vote_map = {}
        active_members = set()
        emote_to_game={}
        game_to_votes={}
        input_messges = []

        try:
            async def waitForGame():
                await ctx.send('Paste the Game and Emoji used to vote for it. If this is the last game reply with "done". Use the !geschelp command for a format reference:')
                message = await self.bot.wait_for('message', check=check, timeout=60.0)
                if message.content == 'done':
                    return
                input_messages.append(message)
                try:
                    #check for formatting here
                    game = message.content.split('=')[0]
                    emote = message.content.split('=')[1]
                    emote_to_game[emote] = game
                    game_to_votes[game] = 0
                    print(game,emote)

                except Exception as error:
                    print(error)
                    await ctx.send("poll creation aborted")

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


    @commands.has_role('Executives')
    @commands.command(aliases=['gescd'])
    async def endpoll(self,ctx):
        if self.current_poll_id == None:
            await ctx.send('no vote running, use geschelp for info on how to use the bot!!')
        poll = await self.get_current_poll()
        game_to_votes = poll['votes']
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
        try:
            user = await self.bot.fetch_user(payload.user_id)
            if user.bot:
                return

            poll = await self.get_current_poll()
            emote_to_game = poll['games']
            game_to_votes = poll['votes']
            member_votes = poll['member_votes']
            members_active = poll['members_active']
            print(poll)

            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            user = await self.bot.fetch_user(payload.user_id)
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            reaction = (f'{payload.emoji.name}')
            print(reaction, reaction == '🍕')

            print(user.bot,message.id != poll['msg_id'],reaction not in emote_to_game)
            if user.bot or message.id != poll['msg_id'] or reaction not in emote_to_game:
                return

            voted_game = emote_to_game[reaction]
            print(voted_game)

            vote_power = 3
            if user.id in members_active:
                vote_power = 5

            # remove previous vote if already voted
            print(f'{user} voted')
            if str(user.id) in member_votes:
                game_to_votes[member_votes[str(user.id)]] -= vote_power



            # add vote
            #voteCollection.update_one({'_id':ObjectId(self.current_poll_id)},{'$set':{'current_poll':False}})
            if str(user.id) not in member_votes:
                member_votes[str(user.id)] = ''
            member_votes[str(user.id)] = voted_game
            game_to_votes[voted_game] += vote_power
            await message.channel.send(f'{member.display_name} voted')

            voteCollection.update_one({'_id':ObjectId(self.current_poll_id)},{'$set':{'member_votes':member_votes}})
            voteCollection.update_one({'_id':ObjectId(self.current_poll_id)},{'$set':{'votes':game_to_votes}})
            await message.remove_reaction(payload.emoji,member)

        except Exception as error:
            print(error)
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            await message.channel.send('vote for game failed')




    # pulls the current poll from the database and
    @commands.has_role('Executives')
    @commands.command(aliases=['gescs'])
    async def synccurrentpoll(self, ctx):

        try:
            # find current poll
            poll = voteCollection.find_one({'current_poll':True})
            print(poll)

            if poll != None:
                self.current_poll_id = poll['_id']
                await ctx.send(f'synced vote based on current vote boolean {self.current_poll_id}')
                msg = await self.make_poll_msg(ctx,poll)

            # we need to ask for the id and pass it in
            #else:
                ## if no current poll then use passed in poll ID
                #param_id = arg[0]
                #poll = voteCollection.find_one({'_id':ObjectId(param_id)})
                #print(poll)

                #if poll != None:
                    #self.current_poll_id = poll['_id']
                    #await ctx.send(f'synced vote based on current vote id {self.current_poll_id}')
                    #print('called above func')
                    #msg = await make_poll_msg(ctx,poll)

        except Exception as error:
            print(error)
            await ctx.send('sync command failed')

    @commands.command(aliases=['gesca'])
    async def toggle_attendance(self,ctx):
        try:
            poll = await self.get_current_poll()
            if poll == None:
                return
            members_active = poll['members_active']
            member_votes = poll['member_votes']
            games_to_votes = poll['votes']
            if ctx.author.id in members_active:
                members_active.remove(ctx.author.id)
                games_to_votes[member_votes[str(ctx.author.id)]] -= 2
                await ctx.send("You actually didn't attend, vote is worth 3")
            else:
                members_active.append(ctx.author.id)
                games_to_votes[member_votes[str(ctx.author.id)]] += 2
                await ctx.send("You attended last meeting! Vote is worth 5")

            voteCollection.update_one({'_id':ObjectId(self.current_poll_id)},{'$set':{'member_votes':member_votes}})
            voteCollection.update_one({'_id':ObjectId(self.current_poll_id)},{'$set':{'members_active':members_active}})
            voteCollection.update_one({'_id':ObjectId(self.current_poll_id)},{'$set':{'votes':games_to_votes}})
        except Exception as error:
            print(error)
            await ctx.send('attendance command failed')




        #voteCollection.update_one({'_id':ObjectId(self.current_poll_id)},{'$set':{'current_poll':False}})




    async def get_current_poll(self):
            return voteCollection.find_one({'_id':ObjectId(self.current_poll_id)})



async def setup(bot):
    await bot.add_cog(Gesc(bot))
