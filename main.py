import discord
import yt_dlp as youtube_dl
import asyncio
from discord import app_commands
from discord.ext import commands, tasks
from auth import Token
import os
from dotenv import load_dotenv
from pathlib import Path
import time

load_dotenv()
DISCORD_TOKEN = os.getenv(Token)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
client = discord.Client(intents=discord.Intents.all())
removeFile=""
#sprawdzanie połączenia
@bot.event
async def on_ready():
    print("Gotowy do działania!")
    try:
        synced=await bot.tree.sync()
        print(f"bot {len(synced)}")
    except Exception as e:
        print(e)

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
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download= not stream))
            if 'entries' in data:
                data = data['entries'][0]
            filename = data['title'] if stream else ytdl.prepare_filename(data)
            return filename
        except Exception as e:
            print(f"Błąd pobierania informacji z yt {str(e)}")
            return None
          
        

#dodawanie komend do dołączenia/wyjścia do/z kanału i do sterowania muzyką 

@bot.tree.command(name = "join", description="Przywołuje bota na twój kanał")
async def join(ctx: discord.Interaction, member: discord.Member):
    try:
        if not getattr(ctx.user.voice, "channel", None):
            await ctx.response.send_message(f"{ctx.user.mention} dołącz najpierw do kanału głosowego!!!")
            return
        else:
            channel = ctx.user.voice.channel
            await channel.connect()
    except Exception as e:
         print(ctx.user.voice.channel.id)

'''@bot.command(name = 'join')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} nie jest połączony z kanałem głosowym".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()
'''
#TU SKONCZYLES
@bot.tree.command(name = 'play', description="Odtwarza muzyke z podanego linka z yt")
async def play(ctx: discord.Interaction, url: discord.TextInput):
    global removeFile
    server = ctx.message.guild
    voice_channel = server.voice_client
    try:    
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop = bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable = "E:/projects/DiscordBot/ffmpeg-2023-07-16-git-c541ecf0dc-full_build/ffmpeg-2023-07-16-git-c541ecf0dc-full_build/bin/ffmpeg.exe", source = filename))
        await ctx.send('**Odtwarzam** {}'.format(filename))
        removeFile=filename
    except Exception as e:
        print(f"Błąd odtwarzania {str(e)}")

@bot.command(name = 'pause')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    try:
        if voice_client.is_playing():
             voice_client.pause()
        else:
             ctx.send("Muzyka już jest zapauzowana albo nic nie jest dodane do kolejki")
    except Exception as e:
        print(f"Błąd przy pauzie {str(e)}")

@bot.command(name = 'resume')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    try:
        if voice_client.is_paused():
             voice_client.resume()
        else:
             ctx.send("Nie ma czego wznawiać")
    except Exception as e:
        print(f"Błąd przy wznawianiu {str(e)}")

@bot.command(name = 'leave')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Nawet nie dołączyłem, a już mam wyjść? ;_;")

@bot.command(name = 'stop')
async def stop(ctx):
    global removeFile
    voice_client = ctx.message.guild.voice_client
    try:
        if voice_client.is_playing():
            voice_client.stop()
            time.sleep(1)
            if os.path.isfile(removeFile):
                os.remove(removeFile)
                removeFile=""
                print(" Zastopowano i usunieto ", removeFile)
            else:
                print("Error : %s plik nie znaleziony" % removeFile)
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