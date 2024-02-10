#!/usr/bin/env python3
import discord
from api_key import apikey

intents = discord.Intents.default()

intents.message_content = True
intents.messages = True
intents.reactions = True


client = discord.Client(intents=intents)

active_polls = {} #stores the votes of the current poll

@client.event
async def on_ready():
    print(f'we have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!scrimblo'):
        sent_message = await message.channel.send('the lovable scrunko')
        await sent_message.add_reaction('🦧')


client.run(apikey)
