import discord, time, json, random, requests, numpy
from discord.ext import commands


intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False, users=True, roles=True)
token = open("token.txt", "r").readline()
startTime = time.time()

bot = commands.Bot(command_prefix="=", intents=intents, allowed_mentions=allowed_mentions, help_command=None)

icons = ["🍒", "🍉", "🍇", "💎", "🔔", "⭐", "👑", "💵", "🍀"]
weights = [0.3, 0.20, 0.18, 0.10, 0.09, 0.05, 0.04, 0.03, 0.01]

@bot.event
async def on_ready():
    await bot.is_owner(bot.user) # load owner ids
    await bot.change_presence(activity=discord.Game("/help"), status=discord.Status.idle)
    print(f"logged in as {bot.user}")
    try: 
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="help", description="list all faith bot commands")
async def help(interaction: discord.Interaction):
    e = discord.Embed(title="faith bot commands", colour=discord.Colour(0xaa7bff))

    for command in bot.tree.walk_commands():
        e.add_field(name=f"/{command.name}", value=command.description or "no description", inline=False)
    
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="ping", description="show faith bots latency to discord")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"{round(bot.latency * 1000)}ms", ephemeral=True)

@bot.tree.command(name="info", description="displays information about faith bot")
async def info(interaction: discord.Interaction):
    seconds = time.time() - startTime
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    w, d = divmod(d, 7)
    uptime_str = f"{int(w)}w : {int(d)}d : {int(h)}h : {int(m)}m : {int(s)}s"
    
    owners = ""
    if bot.owner_id:
        user = bot.get_user(bot.owner_id)
        owners += "Owner: " + user.mention
    elif bot.owner_ids:
        owners += "Owners: "
        for id in bot.owner_ids:
            user = bot.get_user(id)
            owners += user.mention + " "
            
    e = discord.Embed(title="Information about me",
                      url="https://github.com/RKREEE/FaithBot",
                      colour=discord.Colour(0xaa7bff))
    e.set_thumbnail(url=bot.user.display_avatar)
    e.add_field(name="Info", value=f"Name: {bot.user}\nID: {bot.user.id}\n{owners}", inline=False)
    e.add_field(name="Uptime", value=uptime_str, inline=True)
    e.add_field(name="Guild Count", value=f"{len(bot.guilds)} guilds with {len(bot.users)} users", inline=True)

    await interaction.response.send_message(embed=e)

@bot.tree.command(name="findseed", description="generate imaginary minecraft end portal")
async def findseed(interaction: discord.Interaction):
    inner = "<:lava:891481514741731359>" 
    portal ="<:portal:891481514821423127>" 
    noeye = "<:portalnoeye:891481514959855627>" 
    eye = "<:portaleye:891481515073085471>" 
    empty = "<:empty:891481515152789524>" 
    eyes = 0
    p = []
    for _ in range(12):
        if not random.randint(0,9):
            eyes += 1
            p.append(eye)
        else:
            p.append(noeye)

    if eyes == 12:
        inner = portal

    output = ""
    output += f"{empty}{p[0]}{p[1]}{p[2]}{empty}\n"
    output += f"{p[3]}{inner}{inner}{inner}{p[4]}\n"
    output += f"{p[5]}{inner}{inner}{inner}{p[6]}\n"
    output += f"{p[7]}{inner}{inner}{inner}{p[8]}\n"
    output += f"{empty}{p[9]}{p[10]}{p[11]}{empty}"

    e = discord.Embed(title=f"{interaction.user.name}, your seed is a {eyes} eye", description=output, colour=discord.Colour(0xaa7bff))
    await interaction.response.send_message(embed=e)

    user_id = str(interaction.user.id)
	
    # potentially update guild bests
    if interaction.guild: 
        guild_id = str(interaction.guild.id)

        with open("data/bestseed.json", "r") as f:
            data = json.load(f)
        
        if guild_id not in data or data[guild_id]['best'] < eyes:
            data[guild_id] = {"best": eyes, "user": int(user_id)}

        with open("data/bestseed.json", "w") as f:
            json.dump(data, f, indent=4)
    
    # update users findseed stats
    with open("data/findseedstats.json", "r") as f:
        data = json.load(f)
    
    if user_id not in data:
        data[user_id] = {f"{eyes} eyes": 0, "streak": {f"{eyes} eyes": 0} }
    elif f"{eyes} eyes" not in data[user_id]:
        data[user_id][f"{eyes} eyes"]
    
    if "streak" not in data[user_id] or f"{eyes} eyes" not in data[user_id]["streak"]:
        data[user_id]["streak"] = {f"{eyes} eyes": 0}
    
    data[user_id][f"{eyes} eyes"] += 1
    data[user_id]["streak"][f"{eyes} eyes"] += 1

    user_streak = data[user_id]["streak"][f"{eyes} eyes"]
    with open("data/findseedstats.json", "w") as f:
        json.dump(data, f, indent=4)    

    # update findseed streaks 
    with open("data/findseedstreak.json", "r") as f:
        data = json.load(f)
    
    if f"{eyes} eyes" in data["current_streak"]:
        data["current_streak"][f"{eyes} eyes"] += 1
    else: 
        data["current_streak"] = {f"{eyes} eyes": 1}
    
    if data["longest_streak"][f"{eyes} eyes"]["streak"] < user_streak:
        data["longest_streak"][f"{eyes} eyes"] = {"streak": user_streak, "user": int(user_id)}

    with open("data/findseedstreak.json", "w") as f:
        json.dump(data, f, indent=4)

    # update balance
    with open("data/balance.json", "r") as f:
    	data = json.load(f)
    
    try: 
        data[user_id] += eyes
    except KeyError:
        data[user_id] = 1000 + eyes
    
    with open("data/balance.json", "w") as f:
        json.dump(data, f, indent=4)


@bot.tree.command(name="bestseed", description="show the highest number of eyes from a findseed in this server")
async def bestseed(interaction: discord.Interaction):
    if interaction.guild:
        with open("data/bestseed.json", "r") as f:
            data = json.load(f)

        guild_id = str(interaction.guild.id)
        
        if guild_id not in data: 
            await interaction.response.send_message(f"**{interaction.guild.name}** does not have a best findseed")
        else: 
            best = data[guild_id]["best"]
            user = bot.get_user(data[guild_id]["user"])
            if not user:
                await interaction.response.send_message(f"**{interaction.guild.name}** has a best seed of {best} eyes")
            elif user.discriminator != "0":
                await interaction.response.send_message(f"**{interaction.guild.name}** has a best seed of {best} eyes, set by **{user.name}#{user.discriminator}**")
            else:
                await interaction.response.send_message(f"**{interaction.guild.name}** has a best seed of {best} eyes, set by **{user.name}**")
    else:
        await interaction.response.send_message("this command can only be used inside servers")

@bot.tree.command(name="findseedstats", description="list of findseeds a user has rolled")
async def findseedstats(interaction: discord.Interaction, user: discord.Member | discord.User = None):
    if not user: 
        user = interaction.user
    
    with open("data/findseedstats.json", "r") as f:
        data = json.load(f)

    user_id = str(user.id)

    if user_id not in data and str(bot.user.id) != user_id:
            if user.discriminator != "0":
                await interaction.response.send_message(f"**{user.name}#{user.discriminator}** hasnt used findseed before")
            else:
                await interaction.response.send_message(f"**{user.name}** hasnt used findseed before")
    elif user_id == str(bot.user.id):
        seeds = {}
        total = 0
        for u in data:
            for i in range(13): 
                if f"{i} eyes" in data[u]:
                    try:
                        seeds[f'{i} eyes'] += data[u][f"{i} eyes"]
                    except KeyError:
                        seeds[f'{i} eyes'] = data[u][f"{i} eyes"]

                    total += data[u][f"{i} eyes"]

        e = discord.Embed(title=f"{bot.user.name}'s findseed stats from {total:,} seeds", colour=discord.Colour(0xaa7bff))

        for x in range(13):
            try:
                e.add_field(name=f"{x} eyes:", value=f"{seeds[f'{x} eyes']:,}")
            except KeyError:
                e.add_field(name=f"{x} eyes:", value="0")

        await interaction.response.send_message(embed=e)
    
    else: 
        total = 0
        for i in range(13):
            try:
                total += data[user_id][f"{i} eyes"]
            except KeyError:
                continue
        
        e = discord.Embed(title=f"{user.name}'s findseed stats from {total:,} seeds", colour=discord.Colour(0xaa7bff))

        for x in range(13):
            try:
                e.add_field(name=f"{x} eyes:", value=f"{data[user_id][f'{x} eyes']:,}")
            except KeyError:
                e.add_field(name=f"{x} eyes:", value="0")
        await interaction.response.send_message(embed=e)

@bot.tree.command(name="findseedstreak", description="show streaks of eyes from findseed")
async def findseedstreak(interaction: discord.Interaction):
    with open("data/findseedstreak.json", "r") as f:
        data = json.load(f)
    
    e = discord.Embed(title="findseed eye streaks", colour=discord.Colour(0xaa7bff))

    for i in range(13): 
        if data["longest_streak"][f"{i} eyes"]["streak"]:
            user = bot.get_user(data['longest_streak'][f'{i} eyes']['user'])

            if not user:
                e.add_field(name=f"longest {i} eye user streak:", value=f"{data['longest_streak'][f'{i} eyes']['streak']}")
            elif user.discriminator != "0":
                e.add_field(name=f"longest {i} eye user streak:", value=f"{data['longest_streak'][f'{i} eyes']['streak']} by `{user.name}#{user.discriminator}`")
            else: 
                e.add_field(name=f"longest {i} eye user streak:", value=f"{data['longest_streak'][f'{i} eyes']['streak']} by `{user.name}`")

        if f"{i} eyes" in data["current_streak"]:
            current_streak = (f"{i} eyes", data["current_streak"][f"{i} eyes"])
    if data["current_streak"]:
        e.add_field(name=f"current global streak:", value=f"`{current_streak[0]}` {current_streak[1]} eyes", inline=False) 

    await interaction.response.send_message(embed=e)
@bot.tree.command(name="lichess", description="show a users lichess profile")
async def lichess(interaction: discord.Interaction, username: str = "faith_bot"):
    url = f"https://lichess.org/api/user/{username}"
    r = requests.get(url)
    user_info = r.json()

    name = user_info["username"]
    flag = ""
    try:
        user_country = user_info['profile']['flag']
        flag = f":flag_{user_country.lower()}: "
    except KeyError:
        pass

    e = discord.Embed(title=f"{flag}{name}", url=f"https://lichess.org/@/{user_info['id']}", colour=discord.Colour(0xaa7bff))

    ratings = []
    for variant in user_info['perfs']:
        if "prov" not in user_info['perfs'][variant]:
            try:
                if user_info['perfs'][variant]['games']:
                    ratings.append((user_info['perfs'][variant]['rating'], variant))
            except KeyError:
                continue
    ratings.sort(reverse=True)
    best_ratings = ""
    try: 
        for i in range(5):
            best_ratings += f"{ratings[i][0]} {ratings[i][1]}\n"
    except IndexError:
        pass

    e.add_field(name="best ratings", value=best_ratings)

    await interaction.response.send_message(embed=e)

@bot.tree.command(name="richest", description="show top rich people")
async def richest(interaction: discord.Interaction):
    with open("data/balance.json", "r") as f:
        data = json.load(f)
    
    
    output = ""
    index = 1
    n = min(len(data), 10)
    for id, bal in sorted(data.items(), key=lambda item: item[1], reverse=True)[:n]:
        user = bot.get_user(int(id))

        if user.discriminator != "0":
            name = f"**{user.name}#{user.discriminator}**"
        else:
            name = f"**{user.name}**"

        output += f"{index}. {name}: {bal}\n"
        index += 1

    e = discord.Embed(title=f"Top {n} Balances",
            colour=discord.Colour(0xaa7bff),
            description=output)

    await interaction.response.send_message(embed=e)

@bot.tree.command(name="balance", description="show ur balance!!")
async def bal(interaction: discord.Interaction):
    with open("data/balance.json", "r") as f:
        data = json.load(f)
    try: 
        balance = data[str(interaction.user.id)]
    except KeyError:
        balance = 1000
        data[str(interaction.user.id)] = balance

        with open("data/balance.json", "w") as f:
            json.dump(data, f, indent=4)

    await interaction.response.send_message(f"your balance is {balance}")
@bot.tree.command(name="slots", description="play slot machine omg")
async def slots(interaction: discord.Interaction, bet: int = 1):
    if bet <= 0:
        await interaction.response.send_message("you cant just play for fun, bet something!")
        return
    
    user_id = interaction.user.id
    with open("data/balance.json", "r") as f:
        data = json.load(f)
    
    try:
        balance = data[str(user_id)] - bet
    except KeyError:
        balance = 1000 - bet

    if balance < 0:
        await interaction.response.send_message("u dont have this money sorry")
        return

    choices = []
    for i in range(3):
        choice = numpy.random.choice(icons, 1, p=weights, replace=False)
        choices.append(choice[0])
        

    odds = 0
    if choices[0] == choices[1] and choices[1] == choices[2]:
        odds = weights[icons.index(choices[0])] ** 3

    elif "⭐" in choices: 
        odds = ( weights[icons.index("⭐")] ** choices.count("⭐") ) * 10

    if odds:
        value = int(bet / odds)
        won = True
    else:
        value = 0
        won = False
        
    thresholds = [
        (30_000, 50_000),
        (2500, 2500),
        (250, 500),
        (30, 50)
    ]
    for threshold, multiple in thresholds:
        if value > threshold:
            value = round(value / multiple) * multiple
            break
        
    if won:
        output_str = f"# {choices[0]} | {choices[1]} | {choices[2]}\n\n### You won {value}"
    else:
        output_str = f"# {choices[0]} | {choices[1]} | {choices[2]}\n\n### You lost {bet}"

    data[str(user_id)] = (balance + value)
    with open("data/balance.json", "w") as f:
        json.dump(data, f, indent=4)

    await interaction.response.send_message(output_str)


bot.run(token)
