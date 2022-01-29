from types import ClassMethodDescriptorType
import discord
from auth import auth
from discord.ext import commands
import asyncio
import random
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
import json

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#utility functions
async def timerObject(ctx, time, user):
    await asyncio.sleep(time)
    await ctx.send(f"{user.mention}, your timer has expired.")

async def legacyRemindObject(ctx, time, user, input):
    await asyncio.sleep(time)
    await ctx.send(f"{user.mention}, {input}.")

async def getNextOccurance(targetDate, targetTime):
    date = datetime.now()
    est = pytz.timezone('US/Eastern')
    date = date.astimezone(est)
    day = date.day
    if day < targetDate or (day == targetDate and date.hour < targetTime):
        delta = targetDate - day
        date += relativedelta(days=delta)
    else:
        delta = day - targetDate
        date.replace(month=date.month + 1)
        date += relativedelta(months=1, days=-delta)
    date = date.replace(hour=targetTime, minute=0, second=0, microsecond=0)
    return date

async def remindObject(bot, mid, dateString):
    date = datetime.fromisoformat(dateString)
    est = pytz.timezone('US/Eastern')
    delta = date - datetime.now().astimezone(est)
    
    await asyncio.sleep(delta.total_seconds())
    #await asyncio.sleep(5)
    
    filename = "../temp/reminders.json"
    with open (filename) as f:
        data = json.load(f)
        
    if mid in data:
        gid = data[mid]["gid"]
        cid = data[mid]["cid"]
        uid = data[mid]["uid"]
        input = data[mid]["name"]
        
        guild = bot.get_guild(gid)
        channel = discord.utils.get(guild.channels, id=cid)
        user = await bot.fetch_user(uid)
        
        await channel.send(f"{user.mention}, {input}.")
        data.pop(str(mid))
        with open (filename, 'w') as f:
            json.dump(data, f, indent=4)
    
async def loadReminds(bot):
    filename = "../temp/reminders.json"
    with open (filename) as f:
        data = json.load(f)
    for mid in data:
        await remindObject(bot, mid, data[mid]["date"])
    
class Utility(commands.Cog, description="Various utilities"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(loadReminds(self.bot))
        
    @commands.command(brief="Returns mentioned user's id", description="Returns mentioned user's id. Defaults to message author.")
    async def id(self, ctx):
        try:
            userId = str(ctx.message.mentions[0].id)
        except:
            userId = str(ctx.message.author.id)
        await ctx.send("Mentioned user's ID is: " + userId + ".")

    @commands.command(brief="Flips a coin", description="Flips a coin.")
    async def coinflip(self, ctx):
        res = random.choice(["Heads.", "Tails."])
        await ctx.send(res)

    @commands.command(brief="Picks a random choice from a list of inputs separated by commas", description="Picks a random choice from a list of inputs separated by commas.")
    async def choose(self, ctx, *args):
        choices = ' '.join(args[:]).split(',')
        res = random.choice(choices)
        await ctx.send(res)

    @commands.command(brief="Sets a timer for the specified amount of time", description="Sets a timer for the specified amount of time.", aliases=["t"])
    async def timer(self, ctx, time, unit):
        print(f"cmdTimer: Permission given ({ctx.author}).")
        user = ctx.message.author
        await ctx.send(f"Timer set for {time} {unit}.")
        if str(unit) == "second" or str(unit) == "seconds" or str(unit) == "sec" or str(unit) == "secs":
            time = int(time)
        elif str(unit) == "hour" or str(unit) == "hours" or str(unit) == "hr" or str(unit) == "hrs":
            time = int(time) * 3600
        elif str(unit) == "day" or str(unit) == "days":
            time = int(time) * 86400
        else:
            time = int(time) * 60
        await timerObject(ctx, time, user)

    @commands.command(brief="Reminds you to do something in a specified amount of time", description="Reminds you to do something in a specified amount of time.")
    async def legacyremind(self, ctx, time, unit, *input):
        print(f"cmdLegacyRemind: Permission given ({ctx.author}).")
        input = ' '.join(input[:])
        user = ctx.message.author
        await ctx.send(f"Reminder set for {time} {unit} from now.")
        if str(unit) == "second" or str(unit) == "seconds" or str(unit) == "sec" or str(unit) == "secs":
            time = int(time)
        elif str(unit) == "hour" or str(unit) == "hours" or str(unit) == "hr" or str(unit) == "hrs":
            time = int(time) * 3600
        elif str(unit) == "day" or str(unit) == "days":
            time = int(time) * 86400
        else:
            time = int(time) * 60
        await legacyRemindObject(ctx, time, user, input)

    # $reminder day number, time of day military, name
    # ../temp/reminders.json
    @commands.command(brief="Set reminders with [day(number)] [time of day]", description="Set reminders with [day(number)] [time of day].", aliases=["r"]) 
    async def remind(self, ctx, date, hour, *name):
        name = ' '.join(name[:])
        mid = ctx.message.id
        gid = ctx.guild.id
        cid = ctx.channel.id
        uid = ctx.message.author.id
        remind = await getNextOccurance(int(date), int(hour))
        remindString = remind.isoformat()

        await ctx.send("Reminder set for " + remind.strftime("%m-%d | %H:%M") + ".")
        #dumper
        filename = "../temp/reminders.json"
        with open (filename) as f:
            data = json.load(f)
        data.update({mid: {'gid': gid, 'cid': cid, 'uid': uid, 'date': remindString, 'name': name}})
        with open (filename, 'w') as f:
            json.dump(data, f, indent=4)
            
        await remindObject(self.bot, mid, remindString)

    @commands.command(brief="Displays current reminders for your user", description="Displays current reminders for your user.", aliases=["rl"]) 
    async def remindList(self, ctx):
        filename = "../temp/reminders.json"
        with open (filename) as f:
            data = json.load(f)
            
        reminders = {}
        for mid in data:
            if data[mid]["uid"] == ctx.message.author.id:
                date = datetime.fromisoformat(data[mid]["date"])
                est = pytz.timezone('US/Eastern')
                date.astimezone(est)
                reminders.update({date: data[mid]["name"]})
        
        reminders = sorted(reminders.items())
        
        out = "```yaml\nYour Reminders:"
        i = 0
        for date, name in reminders:
            out += "\n" + str(i + 1) + ") " + name + " --> " + date.strftime("%m-%d | %H:%M")
            i += 1
        await ctx.send(out + "```")
        
    @commands.command(brief="Deletes current reminders for your user", description="Deletes current reminders for your user.", aliases=["rr"]) 
    async def remindRm(self, ctx, *label):
        label = ' '.join(label[:])
        
        filename = "../temp/reminders.json"
        with open (filename) as f:
            data = json.load(f)
            
        for mid in data:
            if label in data[mid]["name"]:
                data.pop(str(mid))
                await ctx.send("Reminder deleted.")
                with open (filename, 'w') as f:
                    json.dump(data, f, indent=4)
                break

    @commands.command(brief="Displays user information", description="Displays user information.")
    async def userinfo(self, ctx, member:discord.Member=None):
        if not member: member = ctx.message.author
        embed = discord.Embed(title="User Information", timestamp=datetime.now(), color=0x454599)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Name", value=str(member))
        embed.add_field(name="Bot?", value=member.bot)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        embed.set_footer(text="ID: " + str(member.id))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))