import asyncio
import random

import discord
import yt_dlp as youtube_dl  # Cambiar a yt_dlp
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """Joins a voice channel"""
        if channel is None and ctx.author.voice:
            channel = ctx.author.voice.channel
        elif channel is None:
            await ctx.send("You need to specify a channel or be in one!")
            return

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        
        try:
            await channel.connect()
        except Exception as e:
            await ctx.send(f"Failed to join channel: {e}")
            print(f"Failed to join channel: {e}")

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
        await ctx.send(f'Now playing: {query}')

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything yt_dlp supports)"""
        async with ctx.typing():
            print(f"Attempting to play URL: {url}")  # Mensaje de depuración
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gen_password(self, ctx):
        """Generates a random password"""
        contrasena = ""
        caracteres = "+-/*!&$#?=@abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        for _ in range(8):
            contrasena += random.choice(caracteres)
        await ctx.send(contrasena)

    @commands.command()
    async def gen_emodji(self, ctx):
        """Sends a random emoji"""
        emodji = ["\U0001f600", "\U0001f642", "\U0001F606", "\U0001F923", "\U0001F609", "\U0001F60E", "\U0001F605"]
        await ctx.send(random.choice(emodji))

    @commands.command()
    async def flip_coin(self, ctx):
        """Flips a coin"""
        flip = random.randint(0, 1)
        if flip == 0:
            await ctx.send("CARA")
        else:
            await ctx.send("SELLO")

    @commands.command()
    async def hello(self, ctx):
        """Says hello"""
        await ctx.send(f'Hola, soy un bot {self.bot.user}!')

    @commands.command()
    async def heh(self, ctx, count_heh=5):
        """Repeats 'he' a specified number of times"""
        await ctx.send("he" * count_heh)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'Hemos iniciado sesión como {bot.user}')

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.add_cog(Fun(bot))
        await bot.start("token")

asyncio.run(main())