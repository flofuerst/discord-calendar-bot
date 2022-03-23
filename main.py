import asyncio
from multiprocessing.connection import Client
import discord
from discord.ext import commands, tasks
import os
import fetchDates
import logging

#   TODO: make server and channel based messages (prevent declared problem where bot only writes on specified channel,
#         regardless of server and channel of initialized message)
    
#   TODO: read data from calendar url, not fixed .ics file

client = commands.Bot(command_prefix='§')
daysToDisplay = 21

#   create logging-file
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#   init bot
@client.event
async def on_ready():
    print(client.user, "ready, starting to display dates...")
    channel = client.get_channel(id=955592796482437140)
    await channel.purge(limit = 10)
    writtenMessage = await channel.send(fetchDates.print_dates(daysToDisplay))
    task_loop.start(writtenMessage)

#   command not found exception message
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(title=f"Error!!!", description=f"Command not found.", color=ctx.author.color) 
        await ctx.send(embed=em)
    # raise error

#   define §setup command: write dates one time and then call async task_loop with parameter writtenMassage
#   last 10 messages are getting deleted before writing dates
#   cancel async task_loop before new setup
@client.command()
async def init(ctx):
    task_loop.cancel()
    await ctx.channel.purge(limit = 10)
    writtenMessage = await ctx.send(fetchDates.print_dates(daysToDisplay))
    task_loop.start(writtenMessage)

#   define async loop to edit message which was written in setup function
@tasks.loop(minutes = 5)
async def task_loop(writtenMessage):
    print('updated', task_loop.current_loop, 'times')
    await writtenMessage.edit(content = fetchDates.print_dates(daysToDisplay))

#   define §clear command to clear last 10 messages from channel
#   cancel async task_loop before clearing
@client.command()
async def clear(ctx):
    task_loop.cancel()
    await ctx.channel.purge(limit = 10)

#   get token from .env-file
client.run(os.getenv('TOKEN'))


