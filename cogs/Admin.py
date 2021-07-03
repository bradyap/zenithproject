from types import ClassMethodDescriptorType
import discord
from auth import auth
from discord.ext import commands
from discord.utils import get
import asyncio
import os

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#utility functions
async def kickTimer(ctx, member:discord.Member, time):
        print("kickTimer called.")
        await ctx.send(f"Member {member.display_name} will be kicked after {time} hour(s).")
        time = time * 3600
        await asyncio.sleep(time)
        try:
            await member.kick()
            await ctx.send(f"Member {member.display_name} was kicked after timer expire.")
        except discord.Forbidden:
            await ctx.send("Member kick failed after timer expire.")

async def vcKicker(ctx, member:discord.Member):
    while True:
        if member.voice == None:
            await member.kick()
            break
        else:
            await asyncio.sleep(60)
    await ctx.send(f"Member {member.display_name} was kicked after leaving vc.")

class Admin(commands.Cog, description="Server administration"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Kicks specified user", description="Kicks  specified user. Command useable by those with kick members permission.")
    async def kick(self, ctx, member:discord.Member):
        if ctx.message.author.guild_permissions.kick_members:
            try:
                await member.kick()
            except discord.Forbidden:
                await ctx.send(":(")
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief="Changes mentioned user's nickname", description="Changes mentioned user's nickname.")
    async def nick(self, ctx, user, *args):
        if ctx.message.author.guild_permissions.manage_nicknames:
            name = " ".join(args[:])
            target = ctx.message.mentions[0]
            try:
                await target.edit(nick=name)
                await ctx.send(f"Nickname for {target} changed to {name}.")
            except:
                await ctx.send(f"Nickname change for {target} unsuccessful. Please confirm that entered nickname is below the 32 character limit.")
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief="Mutes mentioned user in text channels", description="Mutes mentioned user in text channels.")
    async def mute(self, ctx):
        if ctx.message.author.guild_permissions.mute_members:
            guild = ctx.guild
            try:
                member = ctx.message.mentions[0]
                if get(ctx.guild.roles, name="Muted"):
                    role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
                else:
                    await guild.create_role(name="Muted", permissions =  discord.Permissions(send_messages = False, read_messages = True))
                    role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
                    pos = 4
                    while True:
                        try:
                            await role.edit(position=pos)
                            break
                        except discord.Forbidden:
                            pos += 1
                            continue
                await member.add_roles(role)
            except discord.Forbidden:
                await ctx.send("Check bot permissions.")
            except:
                await ctx.send("Please mention a user.")
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief="Unmutes previously muted user", description="Unmutes previously muted user.")
    async def unmute(self, ctx):
        if ctx.message.author.guild_permissions.mute_members:
            guild = ctx.guild
            try:
                member = ctx.message.mentions[0]
                if get(ctx.guild.roles, name="Muted"):
                    role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
                    if role in member.roles:
                        await member.remove_roles(role)
                    else:
                        await ctx.send("Mentioned user is not muted.")
                else:
                    await ctx.send("Server does not have mute role.")
            except discord.Forbidden:
                await ctx.send("Check bot permissions.")
            except:
                await ctx.send("Please mention a user.")
        else:
            await ctx.send("You do not have permission to use this command.")
            
    @commands.command(brief="Delete a chosen number of messages", description="Delete a chosen number of messages. Command usable by those with manage messages permission.")
    async def purge(self, ctx, num):
        clear = int(num) + 1
        if ctx.message.author.guild_permissions.manage_messages:
            await ctx.channel.purge(limit=clear)
        else: 
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief="Creates an invite to this server", description="Creates an invite to this server.")
    async def invite(self, ctx):
        link = await ctx.channel.create_invite(max_age = 0)
        await ctx.send(link)

    @commands.command(brief="Kicks mentioned user after a specified amount of time", description="Kicks mentioned user after a specific amount of time (hours).")
    async def timekick(self, ctx, member:discord.Member, time, unit):
        if ctx.message.author.guild_permissions.kick_members:
            if str(unit) == "minute" or str(unit) == "minutes" or str(unit) == "min" or str(unit) == "mins":
                time = round(float(time) / 60, 2)
            await kickTimer(ctx, member, time)
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief="Kicks mentioned user after they leave vc", description="Kicks mentioned user after they leave vc.")
    async def vckick(self, ctx, member:discord.Member):
        if ctx.message.author.guild_permissions.kick_members:
            if member.voice == None:
                await ctx.send(f"Member {member.display_name} is not in a vc.")
            else:
                await ctx.send(f"Member {member.display_name} will be kicked after they leave vc.")
                await vcKicker(ctx, member)
                    
        else:
            await ctx.send("You do not have permission to use this command.")

def setup(bot):
    bot.add_cog(Admin(bot))