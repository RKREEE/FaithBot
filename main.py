import discord
from discord.ext import commands
from random import randint as rand
import time
import json

intents=discord.Intents.all()
allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False)

bot = commands.Bot(command_prefix='=', intents=intents, allowed_mentions=allowed_mentions)
token = open('token.txt', "r").readline()
startTime = time.time()

def isMod(ctx):
    try:
        return ctx.author.guild_permissions.manage_channels
    except AttributeError:
        return False
    
@bot.event
async def on_ready():
    game = discord.Game("=help")
    await bot.change_presence(activity=game, status=discord.Status.idle)
    print(f'logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    with open('phrases.json', 'r') as f:
        data = json.load(f)

    if str(message.guild.id) not in data:
        pass
    else:
        for phrase in data[str(message.guild.id)]:
            if phrase in message.content.lower():
                await message.channel.send(data[str(message.guild.id)][phrase])

    await bot.process_commands(message)
    
@bot.event
async def on_command_error(ctx, exception):
	error = str(exception).lower().replace("\"","`")
	await ctx.send(f'{error}.\npro tip: ```you can use =help to view a list of commands or get extra information.```')
    
@bot.command()
async def ping(ctx):
    await ctx.send(f"{round(bot.latency * 1000)}ms")
    
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
        data[str(ctx.guild.id)] = {"best": eyes, "user": str(ctx.author.id)}
    
    with open("findseedstats.json", 'w') as f:
        json.dump(data, f, indent=4)
    
    with open("findseedUsers.json", "r") as f:
        data = json.load(f)
        
    if str(ctx.author.id) not in data:
        data[str(ctx.author.id)] = {f"{str(eyes)} eyes": "1"}
    elif f"{str(eyes)} eyes" not in data[str(ctx.author.id)]:
        data[str(ctx.author.id)][f"{str(eyes)} eyes"] = "1"
    else:
        data[str(ctx.author.id)][f"{str(eyes)} eyes"] = str(int(data[str(ctx.author.id)][f"{str(eyes)} eyes"]) + 1)
        
    with open("findseedUsers.json", "w") as f:
        json.dump(data, f, indent=4)
        
@bot.command()
async def bestseed(ctx):
    with open('findseedstats.json', 'r') as f:
        data = json.load(f)
       
    if str(ctx.guild.id) not in data:
        await ctx.send(f"**{ctx.guild.name}** doesnt have a seed history")
    else:
        num = data[str(ctx.guild.id)]["best"]
        member = bot.get_user(int(data[str(ctx.guild.id)]["user"]))
        await ctx.send(f'**{ctx.guild.name}** has a best seed of {num} eyes, set by **{member.display_name}#{member.discriminator}**')

@bot.command()
async def findseedstats(ctx, user: discord.User = None):
    if user == None: 
        user = ctx.author
    user = bot.get_user(user.id)
    
    with open('findseedUsers.json', 'r') as f:
        data = json.load(f)
        
    if str(user.id) not in data:
        await ctx.send(f"{user.display_name}#{user.discriminator} hasnt used findseed yet")
    else:
        total = 0
        for i in range(13):
            try:
                total += int(data[str(user.id)][f'{i} eyes'])
            except KeyError:
                continue
                
        e = discord.Embed(title=f"{user.display_name}\'s findseed stats from {total:,} seeds", colour=discord.Colour(0xaa7bff))
        
        for x in data[str(user.id)]:
            try:
                e.add_field(name=f"{str(x)}:", value=f"{int(data[str(user.id)][f'{x} eyes']):,}", inline=True)
            except KeyError:
                e.add_field(name=f"{str(x)} eyes:", value="0", inline=True)
                                                    
        await ctx.send(embed=e)

@bot.command()
async def addphrase(ctx, phrase :str = None, reaction :str = None):
    if isMod(ctx) != False:
        with open('phrases.json', 'r') as f:
            data = json.load(f)

        if str(ctx.guild.id) not in data:
            data[str(ctx.guild.id)] = {}
        if phrase != None and reaction != None:
            data[str(ctx.guild.id)][phrase] = reaction
        elif phrase != None and reaction == None:
            await ctx.send('what do you want me to reply with?')
            return
        elif phrase == None and reaction == None:
            await ctx.send(f'hint:\n```=addphrase \"the phrase\" \"the reply\"```')
            return

        with open('phrases.json', 'w') as f:
            json.dump(data, f, indent=4)

        await ctx.send(f'{phrase} has been added as a phrase for this server')
    else:
        await ctx.send(f'you dont have permission to use this command')

@bot.command()
async def removephrase(ctx, phrase: str):
    if isMod(ctx) != False:
        with open('phrases.json', 'r') as f:
            data = json.load(f)

        try:
            data[str(ctx.guild.id)].pop(phrase)
        except KeyError:
            await ctx.send(f'i cant find `{phrase}`, are you sure you spelt it correctly?')
            return

        with open('phrases.json', 'w') as f:
            json.dump(data, f, indent=4)

        await ctx.send(f'{phrase} has been removed from this server')
    else: 
        await ctx.send('you dont have permission to use this command')
bot.run(token)
