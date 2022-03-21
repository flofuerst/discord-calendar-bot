from distutils.command.clean import clean
from email import message
from multiprocessing.connection import Client
import discord
import os
import fetchDates
import time

client = discord.Client()
daysToDisplay = 21

#   init bot
@client.event
async def on_ready():
    print(client.user ,"ready")

# define messages
@client.event
async def on_message(message):
    channel = client.get_channel(955592796482437140)

    #   ignore messages from bot itself
    if message.author == client.user:
        return

    #   attention: bot doesn't care where init command comes from. He strictly writes output in specified channel, 
    #   regardless of the server
    if message.content.startswith('§init'):
        writtenDates = await channel.send(fetchDates.print_dates(daysToDisplay))
        while(True):
            time.sleep(5)
            await writtenDates.edit(content = fetchDates.print_dates(daysToDisplay))

client.run(os.getenv('TOKEN'))


