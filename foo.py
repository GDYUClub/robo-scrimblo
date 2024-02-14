#!/usr/bin/env python3
import discord
import emoji
from api_key import apikey

intents = discord.Intents.default()

intents.message_content = True
intents.members = True
intents.messages = True
intents.reactions = True


client = discord.Client(intents=intents)

vote_running = False
winning_game = 'no vote rn'
poll_msg_id = ''
client.has_voted = set()

def set_poll_id(id):
    print(id)
    poll_msg_id = id


@client.event
async def on_ready():
    print(f'we have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!scrimblo'):
        sent_message = await message.channel.send('the lovable scrunko')
        await sent_message.add_reaction('\<:everybodywantstobemy:1062484258624647269>')

    if message.content.startswith('!gescvote'):
        # games and emoji in key value pairs, time limit, members at last meeting
        # !gescvote(funger#emoji1$funger2#emoji2$Confident and Satiated#emoji3,2,memberids)
        raw_msg = message.content[10:-1]
        arg_strings = raw_msg.split(',')
        game_dict_raw = arg_strings[0].split('$')
        print(game_dict_raw)
        day_limit = int(arg_strings[1])
        active_members = arg_strings[2].split('$')
        game_dict = {}
        vote_dict = {}

        # maps emoji -> game
        # vote maps game -> vote count
        for game in game_dict_raw:
            game_dict[game.split('#')[1][:1]] = game.split('#')[0]
            vote_dict[game.split('#')[0]] = 0
        print(game_dict)
        sent_message = await message.channel.send(f"""Voting on the following games:\n{game_dict}""")
        client.poll_msg_id = sent_message.id
        client.game_dict = game_dict
        client.vote_dict = vote_dict
        for emoji in game_dict.keys():
            await sent_message.add_reaction(emoji)
        client.vote_running = True


@client.event
async def on_reaction_add(reaction, user):
    # Check if the reaction is not added by the bot itself
    print(reaction.message.id, client.poll_msg_id)
    if user.bot or reaction.message.id != client.poll_msg_id:
        return
    print(reaction)
    print(client.game_dict.keys())
    if f'{reaction}' in client.game_dict:
        #Check if the reaction is on a specific message by ID
        print(user.id)
        client.has_voted.add(user.id)
        if user.id in client.has_voted:
            name = await client.fetch_user(id).name
            sent_message = await reaction.message.channel.send(f'user {name} already voted')



    await reaction.remove(user)





client.run(apikey)
