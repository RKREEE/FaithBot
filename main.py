import discord
from discord.ext import commands
from random import randint as rand
import time
import json

intents=discord.Intents.all()
bot = commands.Bot(command_prefix='=', intents=intents)
token = open('token.txt', "r").readline()

startTime = time.time()

@bot.event
async def on_ready():
    game = discord.Game("=help")
    await bot.change_presence(activity=game, status=discord.Status.idle)
    print(f'logged in as {bot.user}')

@bot.command()
async def info(ctx):
    seconds = time.time() - startTime
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    w, d = divmod(d, 7)
    uptime_str = f'{int(w)}w : {int(d)}d : {int(h)}h : {int(m)}m : {int(s)}s'
    
    e = discord.Embed(title="Information about me",
                      url="https://github.com/RKREEE/FaithBot",
                      colour=discord.Colour(0xaa7bff))
    e.set_thumbnail(url=bot.user.avatar_url_as(format="png"))
    e.add_field(name="Info", value=f"Name: {bot.user}\nID: {bot.user.id}", inline=False)
    e.add_field(name="Uptime", value=uptime_str, inline=True)
    e.add_field(name="Guild Count", value=f"{len(bot.guilds)} guilds with {len(bot.users)} users", inline=True)
               
    await ctx.send(embed=e)
    
@bot.command()
async def findseed(ctx):
    eyes = 0
    for i in range(12):
        if rand(1,10) == 10:
            eyes += 1
    await ctx.send(f'{ctx.author.mention} your seed is a {eyes} eye')
    
    with open('findseedstats.json', 'r') as f:
        data = json.load(f)
        
    if str(ctx.guild.id) not in data or data[str(ctx.guild.id)]["best"] < eyes:
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
