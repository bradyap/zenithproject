import discord
from auth import auth
from discord.ext import commands
import os
from PIL import Image, ImageOps, ImageFilter
import requests
from io import BytesIO
import binascii
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
from colorthief import ColorThief

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class Images(commands.Cog, description="Images processing, manipulation, etc"):
    def __init__(self, bot):
        self.bot = bot

    async def sendAsEmbed(ctx, member):
        embed = discord.Embed()
        embed.set_image(url=member.avatar_url_as(size=512))
        await ctx.send(embed=embed)

    @commands.command(brief="Returns image of the specified user's profile picture", description="Returns image of the specified user's profile picture. Defaults to message sender.")
    async def pfp(self, ctx, *args):
        if len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]
        else:
            member = ctx.message.author
        if args:
            res = requests.get(member.avatar_url)
            image = Image.open(BytesIO(res.content)).convert('RGB')
                
            for i in args:
                if i == "inv" or i == "invert" or i == "ivt":
                    image = ImageOps.invert(image)
                elif i == "blur":
                    image = image.filter(ImageFilter.BLUR)
                elif i == "contour":
                    image = image.filter(ImageFilter.CONTOUR)
                elif i == "emboss":
                    image = image.filter(ImageFilter.EMBOSS)
                elif i == "edges":
                    image = image.filter(ImageFilter.FIND_EDGES)
                elif i == "communism":
                    filter = Image.open(r"./images/communism.jpg")
                    image.paste(filter, (0, 0))
                        
            with BytesIO() as imageBinary:
                image.save(imageBinary, 'PNG')
                imageBinary.seek(0)
                await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))
        else: 
            embed = discord.Embed()
            embed.set_image(url=member.avatar_url_as(size=512))
            await ctx.send(embed=embed)

    @commands.command(brief="Returns a collage of the inputted pictures", description="Returns a collage of the inputted pictures")
    async def collage(self, ctx):
        images = []
        stops = []
        for i in ctx.message.attachments:
            res = requests.get(i.url)
            image = Image.open(BytesIO(res.content)).convert('RGB')
            images.append(image)
        for i in range(100, 0, -1):
            if len(images) >= i ** 2 and len(images) % i == 0:
                height = i * 50
                width = int(len(images) / i) * 50
                for j in range(1, i):
                    stops.append(int(len(images) / i * j))
                break
        #print(str(width) + " , " + str(height))
        output = Image.new('RGB', (width, height))
        xOffset = 0
        yOffset = 0
        index = 0
        for image in images:
            for stop in stops:
                if index == stop:
                    yOffset += 50
                    xOffset = 0
            #print(str(xOffset) + " , " + str(yOffset))
            output.paste(image, (xOffset, yOffset))
            xOffset += image.size[0]
            index += 1
        with BytesIO() as imageBinary:
            output.save(imageBinary, 'PNG')
            imageBinary.seek(0)
            await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))

    @commands.command(hidden=True, brief="Returns the most used colors in an image", description="Returns the most used colors in an image.")
    async def legacypalette(self, ctx):
        clusters = 5
        res = requests.get(ctx.message.attachments[0].url)
        image = Image.open(BytesIO(res.content)).convert('RGB')
        image = image.resize((256, 256))
        array = np.asarray(image)
        shape = array.shape
        array = array.reshape(np.product(shape[:2]), shape[2]).astype(float)
        codes, dist = scipy.cluster.vq.kmeans(array, clusters)
        vecs, dist = scipy.cluster.vq.vq(array, codes)        
        counts, bins = np.histogram(vecs, len(codes))    
        max = np.argmax(counts)                    
        peak = codes[max]
        hex = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
        await ctx.send("#" + hex)
        rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        output = Image.new('RGB', (50, 50), rgb)
        with BytesIO() as imageBinary:
            output.save(imageBinary, 'PNG')
            imageBinary.seek(0)
            await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))

    @commands.command(brief="Returns the most used colors in an image", description="Returns the most used colors in an image.", aliases=["pal"])
    async def palette(self, ctx, num):
        images = []
        stops = []
        res = requests.get(ctx.message.attachments[0].url)
        image = Image.open(BytesIO(res.content)).convert('RGB')
        cthief = ColorThief(BytesIO(res.content))
        if int(num) == 1:
            rgb = cthief.get_color(quality=1)
            image = Image.new('RGB', (50, 50), rgb)
            images.append(image)
        elif int(num) == 2:
            for i in range(1, 3):
                rgb = cthief.get_color(quality=2)
                image = Image.new('RGB', (50, 50), rgb)
                images.append(image)
        else:
            palette = cthief.get_palette(color_count=int(num) + 1)
            for rgb in palette:
                image = Image.new('RGB', (50, 50), rgb)
                images.append(image)
        for i in range(100, 0, -1):
            if len(images) >= i ** 2 and len(images) % i == 0:
                height = i * 50
                width = int(len(images) / i) * 50
                for j in range(1, i):
                    stops.append(int(len(images) / i * j))
                break
        #print(str(width) + " , " + str(height))
        output = Image.new('RGB', (width, height))
        xOffset = 0
        yOffset = 0
        index = 0
        for image in images:
            for stop in stops:
                if index == stop:
                    yOffset += 50
                    xOffset = 0
            #print(str(xOffset) + " , " + str(yOffset))
            output.paste(image, (xOffset, yOffset))
            xOffset += image.size[0]
            index += 1
        with BytesIO() as imageBinary:
            output.save(imageBinary, 'PNG')
            imageBinary.seek(0)
            await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))
    
    @commands.command(brief="Returns preview of colors", description="Returns preview of colors.", aliases=["c"])
    async def color(self, ctx, *args):
        images = []
        stops = []
        for i in args:
            hex = i.lstrip('#')
            rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
            image = Image.new('RGB', (50, 50), rgb)
            images.append(image)
        for i in range(100, 0, -1):
            if len(images) >= i ** 2 and len(images) % i == 0:
                height = i * 50
                width = int(len(images) / i) * 50
                for j in range(1, i):
                    stops.append(int(len(images) / i * j))
                break

        #print(str(width) + " , " + str(height))
        output = Image.new('RGB', (width, height))
        xOffset = 0
        yOffset = 0
        index = 0
        for image in images:
            for stop in stops:
                if index == stop:
                    yOffset += 50
                    xOffset = 0
            #print(str(xOffset) + " , " + str(yOffset))
            output.paste(image, (xOffset, yOffset))
            xOffset += image.size[0]
            index += 1
        with BytesIO() as imageBinary:
            output.save(imageBinary, 'PNG')
            imageBinary.seek(0)
            await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))

    @commands.command(brief="Converts image to ASCII art", description="Converts image to ASCII art.")
    async def ascii(self, ctx):
        #open image
        res = requests.get(ctx.message.attachments[0].url)
        image = Image.open(BytesIO(res.content)).convert('RGB')
        #ascii chars
        chars = ["@", "#", "$", "%", "?", "*", "+", ";", ":", ",", "."]
        #chars = ['#', '?', '%', '.', 'S', '+', '.', '*', ':', ',', '@']
        #chars = ['@', '#', 'S', '$', '*', ';', ':', ',', '.','-', '_']
        width, height = image.size #old dimesions
        #preserve aspect ratio
        new_width = 100
        new_height = int(new_width * (height / width) * 0.55)
        resized = image.resize((new_width, new_height))
        greyscale = resized.convert("L") #convert to greyscale
        ascii_string = ""
        pixels = greyscale.getdata()
        #convert each pixel to ascii character depending on pixel value
        for pixel in pixels:
            ascii_string += chars[pixel // 25]
        #text splitting based on image width
        chunks = [ascii_string[i:i+greyscale.width] for i in range(0, len(ascii_string), greyscale.width)]
        #form image from chunks
        ascii_image = ""
        for chunk in chunks:
            ascii_image += chunk + "\n"
        #write to file and save
        filename = "/home/brady_p/zenithproject/zenithlegacy/temp/ascii.txt"
        with open(filename, "w") as f:
            f.write(ascii_image)
        #read file and send
        with open(filename, "rb") as f:
            await ctx.send(file=discord.File(f, "ascii.txt"))

def setup(bot):
    bot.add_cog(Images(bot))