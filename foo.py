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

client.vote_running = False
winning_game = 'no vote rn'
poll_msg_id = ''
client.user_vote_map = {}
client.has_voted = set()
client.active_members = set()

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
        if client.vote_running:
            sent_message = await message.channel.send("Vote already running, Use !gescendvote to end current vote")

        # games and emoji in key value pairs, time limit, members at last meeting
        # !gescvote(funger#emoji1$funger2#emoji2$Confident and Satiated#emoji3,2,memberids)
        raw_msg = message.content[10:-1]
        arg_strings = raw_msg.split(',')
        game_dict_raw = arg_strings[0].split('$')
        print(game_dict_raw)
        day_limit = int(arg_strings[1])
        #client.active_members = set(arg_strings[2].split('$'))
        game_dict = {}
        vote_dict = {}

        # game_maps emoji -> game
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

    if message.content.startswith('!gescstatus'):
        sent_message = await message.channel.send(f"""vote status:\n{client.vote_dict}""")

    if message.content.startswith('!gescendvote'):
        sent_message = await message.channel.send(f"""vote status:\n{client.vote_dict}""")

    if message.content.startswith('!gescattended'):
        #if no vote running
        if not client.vote_running:
            sent_message = await message.channel.send(f"no vote running, use !geschelp for info")
            return
        '''
        #if you already attended, toggle and reset vote
        if message.author.id in client.active_members:
            client.active_members.remove(message.author.id)
            client.vote_dict[client.user_vote_map[user.id]] -= 5
            sent_message = await message.channel.send(f"user {message.author.id} didn't attend, reset vote (if they already voted)")
        '''
        # reset vote if already voted
        if message.author.id in client.user_vote_map:
            client.vote_dict[client.user_vote_map[message.author.id]] -= 3

        # add to members present at meeting
        client.active_members.add(message.author.id)
        sent_message = await message.channel.send(f"user {message.author.id} has extra vote power, vote reset (if they already voted)")


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
    print(f'{user.id} voted')

    # remove previous vote if already voted
    if user.id in client.user_vote_map:
        client.vote_dict[client.user_vote_map[user.id]] -= vote_power

    # populate and add vote to user -> vote map
    if user.id not in client.user_vote_map:
        client.user_vote_map[user.id] = ''
    client.user_vote_map[user.id] = game_chosen
    client.vote_dict[game_chosen] += vote_power
    sent_message = await reaction.message.channel.send(f'{user.id} (who?) voted')

    await reaction.remove(user)







client.run(apikey)
