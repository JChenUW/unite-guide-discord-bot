#imports
import os
import discord
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import scraper
import yt_dlp
import ffmpeg
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD=os.getenv('DISCORD_GUILD')
DEV=os.getenv('DEV')
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())



# Actions performed when connected
@bot.event
async def on_ready():
    # Print bot, guild name and members
    print(f'{bot.user} connected to Discord')
    for guild in bot.guilds:
        if guild.name==GUILD:
            break
    print(f'Bot: {bot.user}')
    print(f'Server: {guild.name}')
    members = [member.name for member in guild.members]
    print(f'guild members are {members}')
    #fetch my member class
    dev=await bot.fetch_user(DEV)
    # just for testing purposes
    #await dev.create_dm()
    #await dev.dm_channel.send(f'Hello {dev.mention}')

#updates scraped data (runs scraper again)
async def update_tier_list():
    scraper.scrape_tier_list()

# Actions performed when member joins
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Welcome to the server {member.mention}')

# Actions performed when message received
@bot.event
async def on_message(message):
    #records messages in chat_log.txt
    guild=message.guild
    chat_log = open('chat_log.txt', 'a+')
    if not guild:
        chat_log.write(f'In DM  {message.author.name}: {message.content}\n')
    else:
        chat_log.write(f'Time: {message.created_at} In {guild}/{message.channel.name}\
        {message.author.name}: {message.content}\n')
    chat_log.close()

    #prevents looping
    if message.author==bot.user:
        return

    #process commands
    await bot.process_commands(message)


# allows bot to join vc
async def join_vc(ctx):
    vc=ctx.author.voice.channel
    await vc.connect()

#wipes the chat log text file
def cleanse_log():
    open('chat_log.txt', 'w').close()

#commands

#updates tierlist
@bot.command()
async def update(ctx):
    await ctx.channel.send('Updating tierlist from Unite DB')
    await update_tier_list()
    await ctx.channel.send('Tierlist info updated. (Source:https://unite-db.com/tier-list/pokemon)')


#joins vc
@bot.command()
async def join(ctx):
    await join_vc(ctx)


#disconnect from vc
@bot.command()
async def disconnect(ctx):
    await bot.voice_clients[0].disconnect(force=True)


#play YT url in vc
@bot.command()
async def play(ctx):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels)
    voice_client=discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client is None:
        voice_client=await voiceChannel.connect()
    url = ctx.message.content[6:]
    ydl_opts = {'format': "bestaudio/best"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        src = discord.FFmpegPCMAudio(url2)
        await voice_client.play(src)

#stop playing
@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client is None:
        return
    else:
        voice_client.stop()

#get pokemon tier
@bot.command()
async def tier(ctx):
    if ctx.message.content[0:6] == '!tier ':
        tier_list = pd.read_csv('Data\\tier_list.csv', index_col=0)
        query = ctx.message.content[6:].lower()
        if query in tier_list.values:
            response = f'{query} is in {tier_list.index.to_list()[np.where(tier_list == query)[0][0]]} tier'
            await ctx.channel.send(response)
        else:
            await ctx.channel.send('Please enter a valid Pokemon name after !tier')


#sends message
@bot.command()
async def say(ctx):
    if ctx.author==await bot.fetch_user(624670296909021184):
        channel=await bot.fetch_channel(int(ctx.message.content[5:24]))
        await channel.send(ctx.message.content[24:])
    else:
        await ctx.message.channel.send('You don\'t have permission to do that')

bot.run(TOKEN)