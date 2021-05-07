import discord
from discord.ext import commands
from random import randint as rand
import time
import json

intents=discord.Intents.all()
bot = commands.Bot(command_prefix='=', intents=intents)
token = open('token.txt', "r").readline()

startTime = None

@bot.event
async def on_ready():
    startTime = time.time()
    game = discord.Game("=help")
    await bot.change_presence(activity=game, status=discord.Status.idle)
    print(f'logged in as {bot.user}')
    
@bot.command()
async def findseed(ctx):
    eyes = 0
    for i in range(12):
        if rand(1,10) == 10:
            eyes += 1
    await ctx.send(f'{ctx.author.mention} your seed is a {eyes} eye')
    
    with open('findseedstats.json', 'r') as f:
        data = json.load(f)
        
    if str(ctx.guild.id) not in data or data[str(ctx.guild.id)]["best"] <= eyes:
        data[str(ctx.guild.id)] = {"best": eyes, "user": str(ctx.author)}
    
    with open("findseedstats.json", 'w') as f:
        json.dump(data, f, indent=4)
        
@bot.command()
async def bestseed(ctx):
    with open('findseedstats.json', 'r') as f:
        data = json.load(f)
       
    if str(ctx.guild.id) not in data:
        await ctx.send(f"**{ctx.guild.name}** doesnt have a seed history")
    else:
        num = data[str(ctx.guild.id)]["best"]
        member = data[str(ctx.guild.id)]["user"]
        await ctx.send(f'**{ctx.guild.name}** has a best seed of {num} eyes, set by **{member}**')

bot.run(token)