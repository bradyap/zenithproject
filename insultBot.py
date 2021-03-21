import discord
import auth
from discord.ext import commands

#discord
bot = commands.Bot(command_prefix="$")
bot.remove_command('help')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user) + ".")
    print('----')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="$help"))

@bot.command(hidden=True, brief="Returns bot state")
async def info(ctx):
    print(f"cmdInfo: Permission given ({ctx.message.author}).")
    await ctx.send('Insults - logged in as {0} ({0.id})'.format(bot.user))

bot.run(auth.TOKEN)