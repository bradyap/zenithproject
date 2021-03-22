import discord
import auth
import random
import insultResources
from discord.ext import commands

#discord
bot = commands.Bot(command_prefix="$")
bot.remove_command('help')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")
    print('----')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="$help"))

@bot.command(hidden=True, brief="Returns bot state")
async def info(ctx):
    print(f"cmdInfo: Permission given ({ctx.message.author}).")
    await ctx.send('Insults - logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")




#converted pickup line 
@bot.command(brief="Makes insults, you moist jukebox", description="Makes insults, you moist jukebox. Current nouns to use are short.")
async def insult(ctx, noun):
    if noun == "short":
        shortReturn = random.choice(insultResources.short)

    line = random.choice(insultResources.adjectivesList) + "  " + shortReturn
    await ctx.send(line)

bot.run(auth.TOKEN)