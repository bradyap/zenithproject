import discord
from auth import auth
from discord.ext import commands
import os
import json
from discord.utils import get

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class Roles(commands.Cog, description="Roles module commands. Requires level 2."):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Creates a role", description="Creates a role.", aliases=["mr"])
    async def makerole(self, ctx):
        filename = "/home/brady_p/zenithproject/zenithlegacy/level2/" + str(ctx.guild.id) + ".json"
        if os.path.exists(filename):
            with open (filename) as f:
                data = json.load(f)
            if data["roles"]["status"]:
                guild = ctx.guild
                id = ctx.message.author.id
                rolelist = data["roles"]["rolelist"]
                if str(id) in rolelist: await ctx.send("You've already created a role.")
                else:
                    role = await guild.create_role(name=id)
                    await ctx.author.add_roles(role)
                    rolelist.update({str(id): role.id})
                    await ctx.send("Role created.")
                with open (filename, 'w') as f:
                    json.dump(data, f, indent=4)
            else:await ctx.send("The roles module is not enabled on this server.")
        else: await ctx.send("Level 2 features are not enabled on this server.")

    @commands.command(brief="Names your role", description="Names your role.", aliases=["rn"])
    async def rolename(self, ctx, *input):
        filename = "/home/brady_p/zenithproject/zenithlegacy/level2/" + str(ctx.guild.id) + ".json"
        if os.path.exists(filename):
            with open (filename) as f:
                data = json.load(f)
            if data["roles"]["status"]:
                guild = ctx.guild
                id = ctx.message.author.id
                rolelist = data["roles"]["rolelist"]
                input = ' '.join(input[:])
                if len(input) <= 100 and len(input) > 0:
                    if str(id) in rolelist: 
                        role = get(guild.roles, id=rolelist.get(str(id)))
                        await role.edit(name=input)
                        await ctx.send("Role name successfully changed.")
                    else: await ctx.send("Please create a role before using this command.")
                else: await ctx.send("Please enter a role name that is between one and one hundred charaters long.")
            else:await ctx.send("The roles module is not enabled on this server.")
        else: await ctx.send("Level 2 features are not enabled on this server.")

    @commands.command(brief="Sets your role color", description="Sets your role color.", aliases=["rc"])
    async def rolecolor(self, ctx, *input):
        filename = "/home/brady_p/zenithproject/zenithlegacy/level2/" + str(ctx.guild.id) + ".json"
        if os.path.exists(filename):
            with open (filename) as f:
                data = json.load(f)
            if data["roles"]["status"]:
                guild = ctx.guild
                id = ctx.message.author.id
                rolelist = data["roles"]["rolelist"]
                input = ' '.join(input[:])
                hex = input.lstrip('#')
                color_val = int(hex, base=16)
                color = discord.Color(color_val)
                if str(id) in rolelist: 
                    role = get(guild.roles, id=rolelist.get(str(id)))
                    try:
                        await role.edit(color=color)
                        await ctx.send("Role color successfully changed.")
                    except: await ctx.send("Invalid color. Please enter a valid hex value.")
                else:
                    await ctx.send("Please create a role before using this command.")
            else:await ctx.send("The roles module is not enabled on this server.")
        else: await ctx.send("Level 2 features are not enabled on this server.")
    
    #deletes role when member leaves
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        filename = "/home/brady_p/zenithproject/zenithlegacy/level2/" + member.guild.name.replace(" ", "_") + ":" + str(member.guild.id) + ".json"
        if os.path.exists(filename):
            with open (filename) as f:
                data = json.load(f)
            if data["roles"]["status"]:
                guild = member.guild
                id = member.id
                rolelist = data["roles"]["rolelist"]
                if str(id) in rolelist:
                    role = get(guild.roles, id=rolelist.get(str(id)))
                    await role.delete()
                    rolelist.pop(str(id))
                with open (filename, 'w') as f:
                    json.dump(data, f, indent=4)

def setup(bot):
    bot.add_cog(Roles(bot))