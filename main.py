from distutils.command.clean import clean
from email import message
from multiprocessing.connection import Client
import discord
import os
import fetchDates
import time

client = discord.Client()

#   init bot
@client.event
async def on_ready():
    print(client.user ,"ready")
    channel = client.get_channel(954518491422138469)

# define messages
@client.event
async def on_message(message):
    #   ignore messages from bot itself
    if message.author == client.user:
        return

    if message.content.startswith('§init'):
        writtenDates = await message.channel.send(fetchDates.print_dates(21))
        while(True):
            time.sleep(5)
            await writtenDates.edit(content = fetchDates.print_dates(21))


client.run(os.getenv('TOKEN'))


