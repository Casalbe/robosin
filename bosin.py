import discord
import yt_dlp
from discord.ext import commands

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
                'format': 'bestaudio/best',
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
                    print(f"Aaaaassustei: {error}")
                bot.loop.create_task(play_next(ctx))  # Play the next video after the current one finishes

            voice_client.play(discord.FFmpegPCMAudio(url), after=after_play)
            await ctx.send(f"Bosin está imitando: {info['title']}")
        except Exception as e:
            await ctx.send(f"Aaaassutei: {e}")


@bot.command()
async def bosin(ctx, *, yt_link):
    if not ctx.author.voice:
        await ctx.send("Entra numa call né porra.")
        return

    queue.append(yt_link)  # Add the requested video to the queue
    await ctx.send(f"{yt_link}: tá na fila.")

    # If bot is not playing anything, start playing the requested video
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        await play_next(ctx)

@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Ãhr, ta bom.")
    else:
        await ctx.send("To fazendo nada carai!!")


@bot.command()
async def fila(ctx):
    if len(queue) == 0:
        await ctx.send(f"A fila ta vazia.")
    else:
        await ctx.send(f"Bosin vai imitar:")
        for song in queue:
            try:
                with yt_dlp.YoutubeDL() as ydl:
                    info = ydl.extract_info(song, download=False)
                    await ctx.send(f"{info['title']}")
            except Exception as e:
                await ctx.send(f"Aaaassutei: {e}")


@bot.command()
async def vaza(ctx):
    voice = ctx.voice_client
    await voice.disconnect()
    queue.clear()

@bot.event
async def on_voice_state_update(member, before, after):
    if not member.guild.voice_client:
        return
    if not member.guild.voice_client.is_playing():
        await member.guild.voice_client.disconnect()

bot.run('YOUR_DISCORD_TOKEN')
