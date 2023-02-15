# import asyncio
# from multiprocessing.connection import Client
import discord
from discord.ext import commands, tasks
import os
import fetchDates
import re
import time

#   TODO: make server and channel based messages (prevent declared problem where bot only writes on specified channel,
#         regardless of server and channel of initialized message)
#   TODO: help function
#   TODO: zero events allowed
#   TODO: reminder einbauen
#   TODO: Edit message in event creation
#   TODO: Logging


bot = commands.Bot(command_prefix=',cal ', intents=discord.Intents.all())
daysToDisplay = 14

#   create logging-file
# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)


#   init bot
# get message id and call loop which edits message in specific time
@bot.event
async def on_ready():
    print(bot.user, "ready, starting to display dates...")
    channel = bot.get_channel(id=954518491422138469)

    global writtenMessage
    writtenMessage = await channel.fetch_message(1075501291989639168)
    task_loop.start(writtenMessage)


#   command not found exception message
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(
            title=f"Error!", description=f"Command not found.", color=ctx.author.color)
        await ctx.send(embed=em)
    # raise error


#   define §init command: write dates one time and then call async task_loop with parameter writtenMassage
#   last 10 messages are getting deleted before writing dates
#   cancel async task_loop before new setup
@bot.command()
async def init(ctx):
    task_loop.cancel()
    await ctx.channel.purge(limit=10)
    writtenMessage = await ctx.send(fetchDates.print_dates(daysToDisplay))
    task_loop.start(writtenMessage)


#   define async loop to edit message which was written in setup function
@tasks.loop(minutes=5)
async def task_loop(writtenMessage):
    print('updated', task_loop.current_loop, 'times')
    date_content = fetchDates.print_dates(daysToDisplay)
    await writtenMessage.edit(content=date_content if date_content != "" else "`In den nächsten 14 Tagen stehen keine wichtigen Termine an!`")


@bot.command()
async def create(ctx, title, startDate, startTime, endDate, endTime):
    #global var for create-message
    global createMessage
    createMessage = ctx.message

    #global var for ctx
    global createContext
    createContext = ctx

    task_loop.cancel()
    dateRegex = "^(0[1-9]|[1-2][0-9]|3[0-1])\.(0[1-9]|1[0-2])\.\d{4}$"
    timeRegex = "^([0-1]\d|2[0-3])\:[0-5]\d$"
    startD = bool(re.search(dateRegex, startDate))
    endD = bool(re.search(dateRegex, endDate))
    startT = bool(re.search(timeRegex, startTime))
    endT = bool(re.search(timeRegex, endTime))

    #only create event if specified dates (and time) are correct
    if (startD and endD and startT and endT):
        em = discord.Embed(title=f"Do you really want to create this event?", 
            description=f"Title: {title}\nstart date: {startDate} at {startTime}\nend date: {endDate} at {endTime}", color=ctx.author.color)
        message = await ctx.send(embed=em)

        #global var for confirm-message
        global eventConfirm
        eventConfirm = message
        await message.add_reaction("✅")
        await message.add_reaction("❌")
    #error if not correct date(s) specified
    else:
        em = discord.Embed(title=f"Error!", description=f"Incorrect input\nSYNPOPSIS:\n,cal create TITLE DD.MM:YYYY HH:MM DD.MM:YYYY HH:MM", color=ctx.author.color)
        await ctx.send(embed=em)

    task_loop.start(writtenMessage)

@bot.event
async def on_raw_reaction_add(payload):
    #check if same user, correct message id and correct emoji
    print(payload.user_id)
    print(createContext.author.id)
    if(payload.user_id == createContext.author.id and payload.message_id == eventConfirm.id and payload.emoji.name == "✅"):
        #delete create and confirm messages
        await eventConfirm.delete()
        await createMessage.delete()

        ##################
        #create event with caldav



        ##################
        em = discord.Embed(title=f"Event created successfully!", color=createContext.author.color)
        infoMsg = await createContext.send(embed=em)
        time.sleep(10)
        await infoMsg.delete()
    #check if same user, correct message id and correct emoji
    elif(payload.user_id == createContext.author.id and payload.message_id == eventConfirm.id and payload.emoji.name == "❌"):
        #delete create and confirm messages
        await eventConfirm.delete()
        await createMessage.delete()

        em = discord.Embed(title=f"Event not created!", color=createContext.author.color)
        infoMsg = await createContext.send(embed=em)
        time.sleep(10)
        await infoMsg.delete()

    
    # await ctx.send("reacted");

@bot.command()
async def test(ctx, arg1, arg2):
    task_loop.cancel()
    await ctx.send(f'You passed {arg1} and {arg2}')

#   define §clear command to clear last 10 messages from channel
#   cancel async task_loop before clearing


@bot.command()
async def clear(ctx):
    task_loop.cancel()
    await ctx.channel.purge(limit=10)


# clear only one message
@bot.command()
async def clearOne(ctx):
    task_loop.cancel()
    await ctx.channel.purge(limit=1)

#   get token from .env-file
bot.run(os.getenv('TOKEN'))
