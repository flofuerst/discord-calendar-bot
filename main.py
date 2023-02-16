import discord
from discord.ext import commands, tasks
import os
import fetchDates
import re
import asyncio
import logging
import createEvent
from datetime import datetime

#   TODO: make server and channel based messages (prevent declared problem where bot only writes on specified channel,
#         regardless of server and channel of initialized message)
#   TODO: upload memes from #memes channel?
#   TODO: implement reminder in event creation
#   TODO: Edit message in event creation (or after, like ',cal edit...')
#   TODO: Create recurring event

bot = commands.Bot(command_prefix=',cal ', intents=discord.Intents.all())
daysToDisplay = 14
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# define help command for available commands
class MyHelp(commands.HelpCommand):
    @bot.event
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", color=discord.Color.blurple())
        for cog, commands in mapping.items():
           command_signatures = [self.get_command_signature(c) for c in commands]
           if command_signatures:
                availableCommands = []
                cog_name = getattr(cog, "qualified_name", "Available commands")
                for command in command_signatures:
                    if("create" in command or "help" in command):
                        availableCommands.append(command)
                embed.add_field(name=cog_name, value="\n".join(availableCommands), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    @bot.event
    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), color=discord.Color.blurple())
        if command.help:
            embed.description = command.help
        if alias := command.aliases:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

bot.help_command = MyHelp()


#   init bot
# get message id and call loop which edits message in specific time
@bot.event
async def on_ready():
    logging.info('Bot ready, starting to display dates')
    channel = bot.get_channel(id=954518491422138469)

    global writtenMessage
    writtenMessage = await channel.fetch_message(1075709231044501514)
    task_loop.start(writtenMessage)


#   command not found exception message
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(
            title=f"Error!", description=f"Command not found.", color=ctx.author.color)
        await ctx.send(embed=em)
    # raise error


#   define init command: write dates one time and then call async task_loop with parameter writtenMassage
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
    logging.info('Updated events which are being displayed')
    logging.info('Wait for 5 minutes')
    date_content = fetchDates.print_dates(daysToDisplay)
    await writtenMessage.edit(content=date_content if date_content != "" else "`In den nächsten 14 Tagen stehen keine wichtigen Termine an!🥳`")


@bot.command()
async def create(ctx, startDate, startTime, endDate, endTime, *title):
    """Used to add events to calendar\n\nSYNOPSIS:\n,cal create DD.MM.YYYY HH:MM DD.MM.YYYY HH:MM TITLE...\n\n
    example: ,cal create 17.02.2023 18:00 17.02.2023 20:10 [ANA] Anmeldung Test1"""
    global createMessage, createContext, createTitle, createStartDate, createStartTime, createEndDate, createEndTime
    # global var for create-message
    createMessage = ctx.message

    createTitle = ""
    for t in title:
        createTitle+=t + " "
    createStartDate = startDate
    createStartTime = startTime
    createEndDate = endDate
    createEndTime = endTime

    # global var for ctx
    createContext = ctx

    task_loop.cancel()
    dateRegex = "^(0[1-9]|[1-2][0-9]|3[0-1])\.(0[1-9]|1[0-2])\.\d{4}$"
    timeRegex = "^([0-1]\d|2[0-3])\:[0-5]\d$"
    startD = bool(re.search(dateRegex, startDate))
    endD = bool(re.search(dateRegex, endDate))
    startT = bool(re.search(timeRegex, startTime))
    endT = bool(re.search(timeRegex, endTime))

    # only create event if specified dates (and time) are correct
    if (startD and endD and startT and endT and createTitle != ""):
        em = discord.Embed(title=f"Do you really want to create this event?",
                           description=f"Title: {createTitle}\nStart date: {startDate} at {startTime}\nEnd date: {endDate} at {endTime}",
                           color=ctx.author.color)
        message = await ctx.send(embed=em)

        # global var for confirm-message
        global eventConfirm
        eventConfirm = message
        await message.add_reaction("✅")
        await message.add_reaction("❌")
    # error if not correct date(s) specified
    else:
        em = discord.Embed(
            title=f"Error!", description=f"Incorrect input\nSYNOPSIS:\n,cal create DD.MM.YYYY HH:MM DD.MM.YYYY HH:MM TITLE...",
            color=ctx.author.color)
        errMsg = await ctx.send(embed=em)
        logging.info('Failed event creation - incorrect input')

        # async sleep
        await asyncio.sleep(60)
        await createMessage.delete()
        await errMsg.delete()

    task_loop.start(writtenMessage)


@bot.event
async def on_raw_reaction_add(payload):
    # check if same user, correct message id and correct emoji
    if (payload.user_id == createContext.author.id and payload.message_id == eventConfirm.id and payload.emoji.name == "✅"):
        # delete create and confirm messages
        await eventConfirm.delete()
        await createMessage.delete()

        # build up correct datetime
        startDate = createStartDate.split('.')
        startTime = createStartTime.split(':')
        endDate = createEndDate.split('.')
        endTime = createEndTime.split(':')
        startDt = datetime(int(startDate[2]), int(startDate[1]), int(
            startDate[0]), int(startTime[0]), int(startTime[1]))
        endDt = datetime(int(endDate[2]), int(endDate[1]), int(
            endDate[0]), int(endTime[0]), int(endTime[1]))

        # create event with specified title and datetimes
        createEvent.create_event(startDt, endDt, createTitle)

        em = discord.Embed(title=f"Event created successfully!",
                           description=f"Following event was created:\n\nTitle: {createTitle}\nStart date: {createStartDate} at {createStartTime}\nEnd date: {createEndDate} at {createEndTime}",
                           color=createContext.author.color)
        infoMsg = await createContext.send(embed=em)
        logging.info('Successful event creation')

        # async sleep
        await asyncio.sleep(60)
        await infoMsg.delete()
    # check if same user, correct message id and correct emoji
    elif (payload.user_id == createContext.author.id and payload.message_id == eventConfirm.id and payload.emoji.name == "❌"):
        # delete create and confirm messages
        await eventConfirm.delete()
        await createMessage.delete()

        em = discord.Embed(title=f"Event not created!",
                           color=createContext.author.color)
        infoMsg = await createContext.send(embed=em)
        logging.info('Aborted event creation')

        # async sleep
        await asyncio.sleep(60)
        await infoMsg.delete()


# @bot.command()
# async def help(ctx):
#     print("Help called")

#   define clear command to clear last 10 messages from channel
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
