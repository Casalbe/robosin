import discord
import yt_dlp
from discord.ext import commands
import asyncio

intents = discord.Intents.all()
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

queue = []  # List to store requested videos

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

async def play_next(ctx):
    if queue:
        yt_link = queue.pop(0)  # Get the first item from the queue
        try:
            ydl_opts = {
                'format': 'worstaudio/worstaudio*',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(yt_link, download=False)
                url = info['url']

            voice_client = ctx.voice_client
            if not voice_client:
                voice_channel = ctx.author.voice.channel
                voice_client = await voice_channel.connect()

            def after_play(error):
                if error:
                    print(f"Error after playback: {error}")
                if voice_client.is_connected() and queue:  # Check if bot is still connected and if there are songs in the queue
                    bot.loop.create_task(play_next(ctx))  # Play the next video after the current one finishes

            # Inside your play_next function where you call FFmpegPCMAudio
            ffmpeg_options = "-bufsize 512k -loglevel debug"  # Adding -loglevel debug for verbose FFmpeg logs
            log_file_path = "ffmpeg_logs.txt"  # Specify the path to your log file
            ffmpeg_options_with_logging = f"{ffmpeg_options} -report"  # -report option tells FFmpeg to generate a log file

            voice_client.play(discord.FFmpegPCMAudio(url, options=ffmpeg_options_with_logging), after=after_play)

            embed = discord.Embed(title=f"Bosin está imitando:", description=f"[{info['title']}]({yt_link})", color=discord.Color.blue())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Aaaaasustei o play next:  {e}")



@bot.command()
async def bosin(ctx, *, yt_link):
    if not ctx.author.voice:
        await ctx.send("Entra numa call né porra")
        return

    queue.append(yt_link)  # Add the requested video to the queue
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(yt_link, download=False)
        # Create the embed object with a title and description
        embed = discord.Embed(title=f"Botei na fila:", description=f"[{info['title']}]({yt_link})", color=discord.Color.blue())
        await ctx.send(embed=embed)  # Send the embed object

    # If bot is not playing anything, start playing the requested video
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        await play_next(ctx)


@bot.command()
async def fila(ctx):
    if len(queue) == 0:
        await ctx.send("Não tem nada na fila tabacudo.")
        return
    
    #If the queue is not empty, add the queued songs to a neatly organized embeded discord message along with their links
    embed = discord.Embed(title="Bosin vai imitar a seguir:", color=discord.Color.blue())

    for index, song in enumerate(queue):
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(song, download=False)
                embed.add_field(name=f"#{index+1}: {info['title']}", value=f"[Link]({song})", inline=False)
        except Exception as e:
            embed.add_field(name="Aaaaasustei a fila:  ", value=str(e), inline=False)

    await ctx.send(embed=embed)



@bot.command()
async def vaza(ctx):
    try:
        #Disconnect bot from channel and empty the queue
        voice = ctx.voice_client
        await voice.disconnect()
        await ctx.send("TA BOM PORRA!!!")
        queue.clear()
    except Exception as e:
        await ctx.send(f"Aaaaasustei o vaza:  {e}")

@bot.command()
async def limpa(ctx):
    try:
        queue.clear()
        await ctx.send(f"Limpei a fila igual eu limpo meu cu.")
    except Exception as e:
        await ctx.send(f"Aaaaasustei o limpa:  {e}")

@bot.command()
async def move(ctx, current_position: int, new_position: int):
    # Check if the positions are valid
    if current_position <= 0 or new_position <= 0 or current_position > len(queue) or new_position > len(queue):
        await ctx.send("Filho da puta essa posição não existe, AAAAAAAHHHHHHHR.")
        return

    # Adjusting index to work with list indexing (starts from 0)
    current_index = current_position - 1
    new_index = new_position - 1

    try:
        # Move the song in the queue
        song_to_move = queue.pop(current_index)
        queue.insert(new_index, song_to_move)
        await ctx.send(f"Movi a música para a posição {new_position}.")
    except Exception as e:
        await ctx.send(f"Error moving the song: {e}")


@bot.command()
async def tira(ctx, position: int):
    global queue
    if len(queue) == 0:
        await ctx.send("A fila ta vazia tabacudo.")
        return

    # Check if the position is valid
    if position < 1 or position > len(queue):
        await ctx.send(f"Filho da putaaaa, não tem essa posição corno, só tem nas posições de 1 a {len(queue)}.")
        return

    try:
        # Adjust the position to match Python's 0-based indexing
        song_to_remove = queue.pop(position - 1)

        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(song_to_remove, download=False)
            title = info.get('title', 'Unknown title')

        await ctx.send(f"Tirei: **{title}** da fila.")
    except Exception as e:
        await ctx.send(f"Aaaassustei o tira: {e}")


@bot.command()
async def bosinskip(ctx, *, yt_link):
    if not ctx.author.voice:
        await ctx.send("Entra numa call filho da puta.")
        return

    # Check if the bot is connected to a voice channel
    if not ctx.voice_client:
        await ctx.send("Eu não to em uma call buceta")
        return

    # Add the requested song to the front of the queue
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(yt_link, download=False)
        queue.insert(0, yt_link)  # Insert the song at the beginning of the queue

    # Skip the current song to immediately start playing the requested song
    ctx.voice_client.stop()
    # play_next will automatically be called due to the stop event


@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_playing():
        voice_client.stop()  # This will trigger the after_play callback if implemented, which should then play the next song
        await ctx.send("Ãhr, ta bom então.")
    else:
        await ctx.send("Não tem nada tocando porra, ta maluco!?.")


@bot.command()
async def socorro(ctx):
    commands_description = """
Sou burro, então só sei fazer isso por enquanto:
- `!bosin <Link do YouTube>`: Adiciona uma música a fila.
- `!fila`: Mostra a fila de vídeos a serem tocados.
- `!vaza`: Me expulsa da call e me deixa puto.
- `!limpa`: Limpa a fila.
- `!move <Posição atual> <Nova posição>`: Muda a order da musica selecionada.
- `!tira <Posição>`: Tira uma musíca da fila.
- `!bosinskip <Link do YouTube>`: Pula a música atual e toca a solicitada.
- `!skip`: Pula a música atual.
- `!clube`: Xenofobia.
"""
    await ctx.send(commands_description)
    return

@bot.command()
async def clube(ctx):
    # The path to your local image
    image_path = './bosin_clube.png'
    
    # Open the image file in binary mode
    with open(image_path, 'rb') as image_file:
        # Create a Discord File object from the image file
        discord_image = discord.File(image_file, filename="bosin_clube.jpg")  # The filename here is what will be used in the embed
        
        # Create an embed object with a title
        embed = discord.Embed(title="O que a política do clube tem contra ESTE HOMEM:")
        
        # Set the image in the embed using a special URL format for attachments
        embed.set_image(url="attachment://bosin_clube.jpg")  # The URL matches the filename given to the discord.File
        
        # Send the embed along with the file
        await ctx.send(file=discord_image, embed=embed)





@bot.event
async def on_voice_state_update(member, before, after):

    #If bot isn't playing something when another user enters/exits the channel, the bot disconnects
    if not member.guild.voice_client:
        return
    if not member.guild.voice_client.is_playing():
        await member.guild.voice_client.disconnect()

bot.run(token)
