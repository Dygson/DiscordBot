import discord
from discord import app_commands
from discord.ext import commands
from auth import Token
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Gotowy do działania!")
    try:
        synced=await bot.tree.sync()
        print(f"bot {len(synced)}")
    except Exception as e:
        print(e)
    

@bot.tree.command(name = "powitanie", description="Nie masz przyjaciół? to pozwól że chociaż bot Cię przywita :D")
async def powitajka(interaction: discord.Interaction):
    await interaction.response.send_message(f"Siemka {interaction.user.mention}, co tam byq?", ephemeral=True)

'''@bot.event  Odpisywanie, wykonywanie akcji po wysłaniu wiadomości z daną frazą
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('hi'):
        await message.channel.send('Hello')

    if message.content.startswith('listwa'):
        await message.channel.send(file = discord.File("listwa.gif"))
'''
@bot.tree.command(name = "listwa", description="Solidna listwa w formie gifa!")
async def listwa(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"{interaction.user.mention} przesyła solidną listwę {member.mention}", file = discord.File("listwa.gif"))


bot.run(Token)