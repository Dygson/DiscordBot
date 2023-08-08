import discord
import yt_dlp as youtube_dl
import asyncio
from discord import app_commands
from discord.ext import commands, tasks
from auth import Token
import os
from dotenv import load_dotenv
from pathlib import Path
from youtube_dl import YoutubeDL
import time
from discord.utils import get

load_dotenv()
DISCORD_TOKEN = os.getenv(Token)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
client = discord.Client(intents=discord.Intents.all())
intents = discord.Intents.all()
intents.voice_states = True
intents.members = True
intents.guilds = True
removeFile=""
songTitle=""
songDuration=0
seconds = songDuration % (24 * 3600)
hour = seconds // 3600
seconds %= 3600
minutes = seconds // 60
seconds %= 60
#sprawdzanie połączenia
@bot.event
async def on_ready():
    print("Gotowy do działania!")
    try:
        synced=await bot.tree.sync()
        print(f"Aktywny bot {len(synced)}: {bot.user}")
    except Exception as e:
        print(e)


@client.event
async def on_raw_reaction_add(payload):
    message_id = 1133020474427850883
    channel_id = 1129806701302906934
    if payload.message_id == message_id and payload.emoji.name == "✅": # OR paylod.emoji.name == u"\U0001F44D"
        channel = await client.fetch_channel(channel_id)
        await channel.send("OK")

@bot.event
async def on_reaction_add(reaction, user):
    await reaction.message.channel.send(f'{user} reacted with {reaction.emoji}')



GUILD_VC_TIMER = {}
# this event runs when user leave / join / defen / mute 
@bot.event
async def on_voice_state_update(member, before, after):
    # if event is triggered by the bot? return
    if member.id == bot.user.id:
        return

    # when before.channel != None that means user has left a channel
    if before.channel != None:
        voice = discord.utils.get(bot.voice_clients , channel__guild__id = before.channel.guild.id)

        # voice is voiceClient and if it's none? that means the bot is not in an y VC of the Guild that triggerd this event 
        if voice == None:
            return

        # if VC left by the user is not equal to the VC that bot is in? then return
        if voice.channel.id != before.channel.id:
            return

        # if VC has only 1 member (including the bot)
        if len(voice.channel.members) <= 1:

            GUILD_VC_TIMER[before.channel.guild.id] = 0

            while True:
                print("Time" , str(GUILD_VC_TIMER[before.channel.guild.id]) , "Total Members" , str(len(voice.channel.members)))

                await asyncio.sleep(1)

                GUILD_VC_TIMER[before.channel.guild.id] += 1
                
                # if vc has more than 1 member or bot is already disconnectd ? break
                if len(voice.channel.members) >= 2 or not voice.is_connected():
                    break

                # if bot has been alone in the VC for more than 60 seconds ? disconnect
                if GUILD_VC_TIMER[before.channel.guild.id] >= 5:
                    await voice.disconnect()
                    return


#ustawianie parametrów przesyłanego audio z serwisu youtube.com(tylko dla użytku personalnego)
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

#przekazywanie tytułu do bota, wyłaczanie zapetlania i ustawienie głośności
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume = 0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ''

#pobieranie pierwszego wyniku 
    @classmethod
    async def from_url(cls, url, *, loop = None, stream = False):
        global songTitle, songDuration
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download= not stream))
            if 'entries' in data:
                data = data['entries'][0]
            filename = data['title'] if stream else ytdl.prepare_filename(data)
            songTitle = data['title']
            songDuration = data['duration']
            #print(f"Tytuł: {songTitle} , długość: {songDuration}s")
            return filename
        except Exception as e:
            print(f"Błąd pobierania informacji z yt {str(e)}")
            return None
          
        

#dodawanie komend do dołączenia/wyjścia do/z kanału i do sterowania muzyką 
#próba opcji tree.command
@bot.tree.command(name = "join", description="Przywołuje bota na twój kanał")
async def join(interaction: discord.Interaction, member: discord.Member):
    try:
        if not getattr(interaction.user.voice, "channel", None):
            await interaction.response.send_message(f"{interaction.user.mention} dołącz najpierw do kanału głosowego!!!")
            return
        else:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.response.send_message("Już dołączam!!")
    except Exception as e:
         print(interaction.user.voice.channel.id)

@bot.hybrid_command(name='play', help="Odtwarza muzyke z podanego linka z yt")
async def play(ctx, tytul):
    global removeFile, songTitle, songDuration
    server = ctx.message.guild
    voice_channel = server.voice_client
    try:    
        async with ctx.typing():
            filename = await YTDLSource.from_url(tytul, loop = bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable = "E:/projects/DiscordBot/ffmpeg-2023-07-16-git-c541ecf0dc-full_build/ffmpeg-2023-07-16-git-c541ecf0dc-full_build/bin/ffmpeg.exe", source = filename))
        await ctx.send(f'**Odtwarzam** {songTitle}({time.strftime("%H:%M:%S", time.gmtime(songDuration))})')
        removeFile=filename
        #print(filename)
    except Exception as e:
        print(f"Błąd odtwarzania {str(e)}")
        print(filename)
    
    voice_client = ctx.message.guild.voice_client
    try:
        time.sleep(songDuration)
        if not voice_channel.is_playing():
            time.sleep(1)            
            if os.path.isfile(removeFile):
                os.remove(removeFile)
                removeFile=""
                print(" Zastopowano i usunieto ", removeFile)
            else:
                print("Error : %s plik nie znaleziony" % removeFile)
    except Exception as e:
        print(f"Błąd przy stopowaniu {str(e)}")
    

'''@bot.tree.command(name = 'play', description="Odtwarza muzyke z podanego linka z yt")
async def play(ctx: discord.Interaction, tytul: str):
    global removeFile
    voice_channel = ctx.user.voice.channel
    try:    
        filename = await YTDLSource.from_url(tytul, loop = bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(executable = "E:/projects/DiscordBot/ffmpeg-2023-07-16-git-c541ecf0dc-full_build/ffmpeg-2023-07-16-git-c541ecf0dc-full_build/bin/ffmpeg.exe", source = filename))
        await ctx.response.send_message('**Odtwarzam** {}'.format(filename))
        removeFile=filename
    except Exception as e:
        print(f"Błąd odtwarzania {str(e)}")
'''
@bot.hybrid_command(name = 'pause', help = 'Zatrzymanie bieżącej muzyki')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    try:
        if voice_client.is_playing():
             voice_client.pause()
             await ctx.send("Muzyka zapauzowana!")
        else:
             await ctx.send("Muzyka już jest zapauzowana albo nic nie jest dodane do kolejki")
    except Exception as e:
        print(f"Błąd przy pauzie {str(e)}")

@bot.hybrid_command(name = 'resume', help= 'Wznawia zapauzowaną muzykę')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    try:
        if voice_client.is_paused():
             voice_client.resume()
             await ctx.send("Muzyka wznowiona!")
        else:
             await ctx.send("Nie ma czego wznawiać")
    except Exception as e:
        print(f"Błąd przy wznawianiu {str(e)}")

@bot.hybrid_command(name = 'leave', help ='Opuszczenie przez bota kanału głosowego')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Żegnam i polecam się na przyszłość!")
    else:
        await ctx.send("Nawet nie dołączyłem, a już mam wyjść? ;_;")

@bot.hybrid_command(name = 'stop', help='Stopuje muzyke bez możliwości wznawiania(usuwa z kolejki)')
async def stop(ctx):
    global removeFile
    voice_client = ctx.message.guild.voice_client
    try:
        if voice_client.is_playing():
            voice_client.stop()
            async with ctx.typing():
                time.sleep(1)            
                if os.path.isfile(removeFile):
                    os.remove(removeFile)
                    removeFile=""
                    print(" Zastopowano i usunieto ", removeFile)
                else:
                    print("Error : %s plik nie znaleziony" % removeFile)
                await ctx.send("Zatrzymano!")
        else:
            ctx.send("Nie ma czego zatrzymywać")
    except Exception as e:
        print(f"Błąd przy stopowaniu {str(e)}")
    
    
#komenda witająca

@bot.tree.command(name = "powitanie", description="Nie masz przyjaciół? to pozwól że chociaż bot Cię przywita :D")
async def powitajka(interaction: discord.Interaction):
    await interaction.response.send_message(f"Siemka {interaction.user.mention}, co tam byq?")

#Odpisywanie, wykonywanie akcji po wysłaniu wiadomości z daną frazą
'''@bot.event  
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('hi'):
        await message.channel.send('Hello')

    if message.content.startswith('listwa'):
        await message.channel.send(file = discord.File("listwa.gif"))
'''

#komenda listwa
@bot.tree.command(name = "listwa", description="Solidna listwa w formie gifa!")
async def listwa(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"{interaction.user.mention} przesyła solidną listwę {member.mention}", file = discord.File("listwa.gif"))

if __name__ == "__main__":
    bot.run(Token)
#bot.run(Token)