
#!/usr/bin/env python3
import discord
from api_key import apikey
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot

intents = discord.Intents.default()

scheduler = AsyncIOScheduler()

intents.message_content = True
intents.members = True
intents.messages = True
intents.reactions = True


client = discord.Client(intents=intents)

client.vote_running = False
poll_msg_id = ''
client.user_vote_map = {}
client.has_voted = set()
client.active_members = set()


@client.event
async def on_ready():
    print(f'we have logged in as {client.user}')
    if not scheduler.running:
        scheduler.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!scrimblo'):
        sent_message = await message.channel.send('the lovable scrunko')

    if message.content.startswith('!gescvote'):
        start_vote(message)

    if message.content.startswith('!gescstatus'):
        sent_message = await message.channel.send(f"""vote status:\n{client.vote_dict}""")

    if message.content.startswith('!gescend'):
        await end_vote(message)

    if message.content.startswith('!gescattended'):
        attended(message)

    if message.content.startswith('!geschelp'):
        help()

async def attended(message):
    #if no vote running
    if not client.vote_running:
        sent_message = await message.channel.send(f"no vote running, use !geschelp for info")
        return

    #if you already attended, toggle but add to your current vote what it would've been (+2 or -2)
    #This is cuz vote gets reset when it's changed
    if message.author.id in client.active_members:
        client.active_members.remove(message.author.id)
        if message.author.id in client.user_vote_map:
            client.vote_dict[client.user_vote_map[message.author.id]] -= 2
        sent_message = await message.channel.send(f"nvm, user {message.author} didn't attend,vote power updated")

    # reset vote if already voted
    if message.author.id in client.user_vote_map:
        client.vote_dict[client.user_vote_map[message.author.id]] += 2

    # add to members present at meeting
    client.active_members.add(message.author.id)
    sent_message = await message.channel.send(f"user {message.author} has extra vote power, vote reseted (if they already voted)")

async def end_vote(message):
    print('ending the vote')
    if not client.vote_running:
        sent_message = await message.channel.send(f"no vote running, use !geschelp for info")
        return
    highest = 0
    winning_game = max(client.vote_dict, key=client.vote_dict.get)
    output = winning_game
    higest = client.vote_dict[winning_game]

    # check for tie
    for game in client.vote_dict:
        if client.vote_dict[game] == client.vote_dict[winning_game] and game != winning_game:
            output = "A Tie"

    sent_message = await message.channel.send(f"""Vote over!\n The winner is: {output}!\n{client.vote_dict}""")
    client.vote_running = False


async def start_vote(message):
    if client.vote_running:
        sent_message = await message.channel.send("Vote already running, Use !gescendvote to end current vote")

    # games and emoji in alue pairs, time limit, members at last meeting
    # !gescvote(funger#emoji1$funger2#emoji2$Confident and Satiated#emoji3,2,memberids)
    raw_msg = message.content[10:-1]
    arg_strings = raw_msg.split(',')
    game_dict_raw = arg_strings[0].split('$')
    print(game_dict_raw)
    hours = int(arg_strings[1])
    game_dict = {}
    vote_dict = {}

    # calculate end time
    end_time = datetime.now() + timedelta(hours=hours)
    scheduler.add_job(end_vote, 'date', run_date=end_time, args=[message])


    # game_maps emoji -> game
    # vote maps game -> vote count
    for game in game_dict_raw:
        game_dict[game.split('#')[1]] = game.split('#')[0]
        #game_dict[game.split('#')[1][:1]] = game.split('#')[0]
        #game_dict[game.split('#')[1][1:-1]] = game.split('#')[0]
        vote_dict[game.split('#')[0]] = 0
    print(game_dict)
    vote_annoucement = '\nNew GESC Vote for the following Games:\n'
    for game in game_dict:
        output = f'{game} -> {game_dict[game]}\n'
        vote_annoucement += output
    vote_annoucement+= f'vote ends at {end_time}'


    sent_message = await message.channel.send(vote_annoucement)
    client.poll_msg_id = sent_message.id
    client.game_dict = game_dict
    client.vote_dict = vote_dict
    for emoji in game_dict.keys():
        await sent_message.add_reaction(emoji)
    client.vote_running = True

async def help(ctx):
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



@client.event
#game dict: emoji -> game
#vote_dict: game -> vote
#user_vote_map: user.id -> game

async def on_reaction_add(reaction, user):
    # Check if the reaction is not added by the bot itself
    print(reaction.message.id, client.poll_msg_id)
    if user.bot or reaction.message.id != client.poll_msg_id:
        return
    print(reaction)
    print(client.game_dict.keys())
    print(type(client.active_members))
    print(type(user.id))

    # remove reactions that aren't votes
    if f'{reaction}' not in client.game_dict:
        await reaction.remove(user)
        return

    # work with a string of the game instead of an emote please
    game_chosen = client.game_dict[f'{reaction}']
    vote_power = 3
    if user.id in client.active_members:
        vote_power = 5

    # add vote to user map and vote count
    print(f'{user} voted')

    # remove previous vote if already voted
    if user.id in client.user_vote_map:
        client.vote_dict[client.user_vote_map[user.id]] -= vote_power

    # populate and add vote to user -> vote map
    if user.id not in client.user_vote_map:
        client.user_vote_map[user.id] = ''
    client.user_vote_map[user.id] = game_chosen
    client.vote_dict[game_chosen] += vote_power
    sent_message = await reaction.message.channel.send(f'{user} voted')

    await reaction.remove(user)







