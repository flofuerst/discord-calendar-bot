import discord
from discord.ext import commands, tasks
import os
import fetchDates
import re
import random
import logging
import createEvent
from datetime import datetime


bot = commands.Bot(command_prefix=',cal ', intents=discord.Intents.all())
daysToDisplay = 14
activeMessages = set()
addedParticipants = []

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# define help command for available commands


class MyHelp(commands.HelpCommand):
    @bot.event
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", color=discord.Color.blurple())
        for cog, commands in mapping.items():
            command_signatures = [
                self.get_command_signature(c) for c in commands]
            if command_signatures:
                availableCommands = []
                cog_name = getattr(cog, "qualified_name", "Available commands")
                for command in command_signatures:
                    if ("create" in command or "help" in command):
                        availableCommands.append(command)
                embed.add_field(name=cog_name, value="\n".join(
                    availableCommands), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    @bot.event
    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(
            command), color=discord.Color.blurple())
        if command.help:
            embed.description = command.help
        if alias := command.aliases:
            embed.add_field(
                name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


bot.help_command = MyHelp()


#   init bot
# get message id and call loop which edits message in specific time
@bot.event
async def on_ready():
    logging.info('Bot ready, starting to display dates')
    channel = bot.get_channel(id=955592796482437140)  # 955592796482437140

    global writtenMessage
    # 986402491430207529
    writtenMessage = await channel.fetch_message(986402491430207529)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(',cal help'))
    task_loop.start(writtenMessage)


#   command not found exception message
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(
            title=f"Error!", description=f"Command not found.", color=ctx.author.color)
        await ctx.send(embed=em)
    # raise error


def displayDates():
    entry = fetchDates.print_dates(daysToDisplay)
    output = ''

    for content in entry:
        displayedParticipants = content[2]
        displayedParticipants = '-' if displayedParticipants == "" or displayedParticipants == "None" else displayedParticipants

        text = '<t:'+str(content[0])+':F>' + '\n' + content[1] + \
            ' ' + '<t:'+str(content[0])+':R>\nTeilnehmer:\n' + \
            displayedParticipants + '\n\n'
        output += text+'\n' if content != entry[len(entry)-1] else text
    return output

#   define init command: write dates one time and then call async task_loop with parameter writtenMassage
#   last 10 messages are getting deleted before writing dates
#   cancel async task_loop before new setup


@bot.command()
async def init(ctx):
    # global var for ctx
    createContext = ctx

    task_loop.cancel()
    await createContext.channel.purge(limit=10)

    writtenMessage = await createContext.send("Loading...")
    task_loop.start(writtenMessage)


#   define async loop to edit message which was written in setup function
@tasks.loop(minutes=5)
async def task_loop(writtenMessage):
    logging.info('Updated events which are being displayed')
    logging.info('Wait for 5 minutes')
    date_content = displayDates()
    em = discord.Embed(description=date_content)

    await writtenMessage.edit(content="", embed=em if date_content != "" else "`In den nächsten 14 Tagen stehen keine wichtigen Termine an!🥳`", inline=True)

createContext = None


@bot.command()
async def create(ctx, startDate, startTime, endDate, endTime, *title):
    """Used to add events to calendar\n\nSYNOPSIS:\n,cal create DD.MM.YYYY HH:MM DD.MM.YYYY HH:MM TITLE...\n\n
    example: ,cal create 17.02.2023 18:00 17.02.2023 20:10 [ANA] Anmeldung Test1"""
    global createMessage, createTitle, createStartDate, createStartTime, createEndDate, createEndTime, possibleParticipants, createContext

    # global var for create-message
    createMessage = ctx.message

    createContext = ctx

    createTitle = ""
    for t in title:
        createTitle += t + " "
    createStartDate = startDate
    createStartTime = startTime
    createEndDate = endDate
    createEndTime = endTime

    task_loop.cancel()
    dateRegex = "^(0[1-9]|[1-2][0-9]|3[0-1])\.(0[1-9]|1[0-2])\.\d{4}$"
    timeRegex = "^([0-1]\d|2[0-3])\:[0-5]\d$"
    titleRegex = "^\[.+\].*$"
    startD = bool(re.search(dateRegex, startDate))
    endD = bool(re.search(dateRegex, endDate))
    startT = bool(re.search(timeRegex, startTime))
    endT = bool(re.search(timeRegex, endTime))
    correctTitleFormat = bool(re.search(titleRegex, createTitle))

    members = ctx.message.guild.members

    # logging.info(startD, endD, startT, endT, createTitle)
    if (createContext.author.id in activeMessages):
        em = discord.Embed(
            title=f"Error!", description=f"Ongoing event creation not completed yet",
            color=ctx.author.color)
        errMsg = await ctx.send(embed=em)
        logging.info('Failed event creation - ongoing creation not completed')
    # only create event if specified dates (and time) are correct
    elif (startD and endD and startT and endT and createTitle != "" and correctTitleFormat):
        sd = datetime.strptime(startDate, "%d.%m.%Y")
        ed = datetime.strptime(endDate, "%d.%m.%Y")
        st = datetime.strptime(startTime, "%H:%M")
        et = datetime.strptime(endTime, "%H:%M")
        if (sd == ed and st >= et):
            em = discord.Embed(
                title=f"Error!", description=f"StartTime has to be before EndTime if startDate and endDate are equal",
                color=ctx.author.color)
            errMsg = await ctx.send(embed=em)
            logging.info(
                'Failed event creation - startTime is equal or after endTime')
        elif (sd > ed):
            em = discord.Embed(
                title=f"Error!", description=f"StartDate has to be before or equal EndDate",
                color=ctx.author.color)
            errMsg = await ctx.send(embed=em)
            logging.info('Failed event creation - startDate is after endDate')
        else:
            memberCounter = 0
            participantsChoice = ""
            emojiList = ['🙌', '💝', '😜', '🔥', '⬅️', '🏙', '👿', '🔙', '😿', '⏭',
                         '🗝', '😭', '🏁', '🗒', '🔱', '✒️', '☎️', '⛄️', '🅿️', '💫',
                         '💡', '📄', '💪', '🤑', '💠', '❣', '✍', '🐇', '⚱', '🗽',
                         '🐷', '🌯', '🕊', '🚃', '‼️', '🍞', '⚒', '🗨', '🍡', '🔲',
                         '🎹', '⚾️', '⚛', '🚁', '🚻', '😂', '🏩', '🚘', '🌕', '🛬',
                         '🚍', '🏴', '🚠', '♎️', '🌝', '🎮', '🏹', '🛐', '🔃', '🍺',
                         '🐄', '🎱', '👂', '🙅', '🏨', '😯', '🌞', '🎾', '👸', '🏵',
                         '🛣', '🍁', '🚢', '🔆', '👤', '👊', '🙎', '🌫', '🍴', '⚪️',
                         '🔉', '🚧', '❓', '📞', '👽', '❗️', '🏉', '🍵', '🚈', '🔺',
                         '📊', '💿', '⛲️', '🌬', '💽', '🔒', '🎩', '🌳', '👯', '👚']

            possibleParticipants = {}

            for member in members:
                if (not member.bot):
                    digitEmoji = chr(ord("\U00000030") +
                                     memberCounter) + "\U000020E3"
                    memberMentionId = f"<@{member.id}>"
                    if (memberCounter < 10):
                        participantsChoice += digitEmoji
                        possibleParticipants[digitEmoji] = memberMentionId
                    else:
                        randomEmoji = random.sample(emojiList, 1)[0]
                        participantsChoice += randomEmoji
                        possibleParticipants[randomEmoji] = memberMentionId
                    participantsChoice += memberMentionId + "\n"
                    memberCounter += 1

            em = discord.Embed(title=f"Add Participants",
                               description=f"Please select the participants of this event.\nSelect ✅ if done.\n\n{participantsChoice}",
                               color=ctx.author.color)
            message = await ctx.send(embed=em)

            global eventParticipants
            eventParticipants = message
            activeMessages.add(createContext.author.id)

            for emoji in possibleParticipants.keys():
                await message.add_reaction("✅")
                await message.add_reaction(emoji)

    # error if not correct date(s) specified
    else:
        em = discord.Embed(
            title=f"Error!", description=f"Incorrect input\nSYNOPSIS:\n,cal create DD.MM.YYYY HH:MM DD.MM.YYYY HH:MM TITLE...",
            color=ctx.author.color)
        errMsg = await ctx.send(embed=em)
        logging.info('Failed event creation - incorrect input')

    task_loop.start(writtenMessage)


eventConfirm = None
eventParticipants = None
participants = ""


@bot.event
async def on_raw_reaction_add(payload):
    global eventConfirm, participants

    if (payload.user_id == createContext.author.id):
        if (eventParticipants is not None and payload.message_id == eventParticipants.id):
            if (payload.emoji.name == "✅"):
                participants = ", ".join(addedParticipants)
                if (participants == ""):
                    participants = "-"

                em = discord.Embed(title=f"Do you really want to create this event?",
                                   description=f"Title: {createTitle}\nStart date: {createStartDate} at {createStartTime}\nEnd date: {createEndDate} at {createEndTime}\nParticipants: {participants}",
                                   color=createContext.author.color)
                message = await createContext.send(embed=em)

                eventConfirm = message

                await message.add_reaction("✅")
                await message.add_reaction("❌")
            if (payload.emoji.name in possibleParticipants.keys()):
                addedParticipants.append(
                    possibleParticipants[payload.emoji.name])

        if (eventConfirm is not None and payload.message_id == eventConfirm.id):
            # check if same user, correct message id and correct emoji
            if (payload.emoji.name == "✅"):
                # delete confirm message
                await eventConfirm.delete()
                await eventParticipants.delete()

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
                createEvent.create_event(
                    startDt, endDt, createTitle, "\n".join(addedParticipants))

                em = discord.Embed(title=f"Event created successfully!",
                                   description=f"Following event was created:\n\nTitle: {createTitle}\nStart date: {createStartDate} at {createStartTime}\nEnd date: {createEndDate} at {createEndTime}\nParticipants: {participants}\n\n Following command was used:\n,cal create {createStartDate} {createStartTime} {createEndDate} {createEndTime} {createTitle}",
                                   color=createContext.author.color)
                infoMsg = await createContext.send(embed=em)
                activeMessages.remove(createContext.author.id)

                logging.info('Successful event creation')

            # check if same user, correct message id and correct emoji
            elif (payload.emoji.name == "❌"):
                # delete confirm message
                await eventConfirm.delete()
                await eventParticipants.delete()

                em = discord.Embed(title=f"Event not created!",
                                   description=f"Following command was used:\n,cal create {createStartDate} {createStartTime} {createEndDate} {createEndTime} {createTitle}",
                                   color=createContext.author.color)
                infoMsg = await createContext.send(embed=em)
                activeMessages.remove(createContext.author.id)
                logging.info('Aborted event creation')

            # clear participants
            addedParticipants.clear()

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
