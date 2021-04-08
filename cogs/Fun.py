import aiosqlite3
import asyncio
import datetime
import discord
import random
import os
from discord.ext import commands, menus
from udpy import AsyncUrbanClient

UClient = AsyncUrbanClient()

import idiotlibrary
from idiotlibrary import red, green

sheets = {
    'interview':
    [['plural noun', 'plural noun', 'noun', 'color', 'verb', 'adjective', 'noun', 'noun', 'adjective', 'adjective', 'number', 'adjective', 'adjective', 'adjective', 'noun', 'verb'],
    '''
    QUESTION: Whatever made you choose the name "The Psycho {0}" for your group?
    ANSWER:   All the other good names like the "Rolling {1}," "{2} Jam," and "{3} Floyd" were taken.
    QUESTION: You not only {4} songs, but you play many {5} instruments, don't you?
    ANSWER:   Yes. I play the electric {6}, the bass {7}, and the {8} keyboard.
    QUESTION: You now have a(n) {9} song that is number {10} on the {11} charts. What was the inspiration for this {12} song?
    ANSWER:   Believe it or not, it was a(n) {13} song that my mother used to sing to me when it was time for {14}, and it never failed to {15} me to sleep.
    '''
    ]
}


class SnakeGame(menus.Menu):
    def __init__(self):
        self.length = 10
        self.width = 10
    
    def __str__(self):
        return self.board
    
    async def generate_board(self, index:int) -> list:
        width = []
        height = []
        [width.append(index) for item in range(self.width)]
        [height.append(width) for item in range(self.length)]
        self.board = height
        return height

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Get the definition of a word off of Urban Dictionary.')
    async def urban(self, ctx, *, word):
        defs = await UClient.get_definition(word)
        try:
            definition = defs[0].definition
        except IndexError:
            return await ctx.send('Could not find a definition for that')
        if len(definition) < 1000:
            await ctx.send(f'```{definition}```')
        else:
            await idiotlibrary.pages_simple(ctx, definition)

    @commands.command(description='Use the bot to send an embed in the chat with {0}embed [title] [description]')
    async def embed(self, ctx, title="Title", *, description="Description"):
        e = discord.Embed(description=description, title=title,
                          color=0x7ae19e, author=ctx.author.name)
        if len(ctx.message.attachments) >> 0:
            embed = ctx.message.attachments[0]
            e.set_image(url=embed.url)
        web = await ctx.channel.create_webhook(name=ctx.author.name)
        await web.send(embed=e, avatar_url=ctx.author.avatar_url)
        await web.delete()
        await ctx.message.delete()

    @commands.command(description='Roll a n dies with n sides, with the format [number]d[sides]. Use {0}roll NdN to roll.')
    async def roll(self, ctx, *, dice: str = None):
        result = []
        sum = 0
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception as e:
            print(e)
            try:
                ndice = int(dice)
                embed = discord.Embed(
                    title=f"Rolls- **1d{ndice}**", description=f'You rolled a **{random.randint(1, ndice)}**',
                    color=0x7ae19e)
                await ctx.reply(embed=embed)
                return
            except Exception:
                embed = discord.Embed(
                    title="Error", description='Please only use the **NdN** format', color=0x7ae19e)
                await ctx.reply(embed=embed)
                return

        for r in range(rolls):
            result.append(random.randint(1, limit))

        for r in range(len(result)):
            sum += result[r]

        if rolls == 1:
            embed = discord.Embed(
                title=f"Rolls- **{dice}**", description=f'{result[0]}', color=0x7ae19e)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Rolls- **{dice}**", description=f'{sum} - {result}', color=0x7ae19e)
            await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def birthday(self, ctx, date: str):
        now = datetime.datetime.now().strftime("%m/%d")
        await ctx.send(now)
        if now == date:
            await ctx.send("Happy Birthday!")
        if len(date.split('/')[0]) == 2 and len(date.split('/')[1]) == 2:
            async with aiosqlite3.connect('idiotbot.db') as db:
                await db.execute("INSERT INTO birthdays (person, date) VALUES (?, ?)", (ctx.author.id, date))
                await db.commit()
            e = discord.Embed(
                title="Success.", description=f"Birthday set to {date}!", color=0x7ae19e)
            await ctx.send(embed=e)
        else:
            e = discord.Embed(
                title="Error you idiot",
                description="You have to use the format `mm/dd`, alright? It's simple, like this one for May 17th: `05/17`. Okay?",
                color=0xdf4e4e)
            await ctx.send(embed=e)

    @commands.command(description='Monke')
    async def monke(self, ctx):
        e = discord.Embed(title='MONKE?????')
        e.set_image(url='https://www.placemonkeys.com/500/350?random')
        await ctx.send(embed=e)

    @commands.command(description='Yum')
    async def eat(self, ctx, *, eat:str='nothing'):
        await ctx.send(f' :point_right: {eat} <:OMEGALUL:803681453715226645> {(ctx.author.name if ctx.author.nick == None else ctx.author.nick)}')

    @commands.command(description='Praise the Sun!')
    async def praise(self, ctx):
        '''Praise the Sun'''
        await ctx.send('https://i.imgur.com/K8ySn3e.gif')

    @commands.command(description='Start a madlibs session! Use {0}madlibs to start a random one and {0}madlibs <sheet> for a specific sheet. The bot will tell you the type of word you need, and the owner can reply to the message to submit it. When you are done, you can see the sheet.')
    async def madlibs(self, ctx, sheet=None):
        if sheet is None:
            sheet = sheets['interview']
        else:
            try:
                sheet = sheets[sheet]
            except IndexError:
                await ctx.send('That\'s not a sheet idiot.')
        responses = []
        for word in sheet[0]:
            e = discord.Embed(
                title=f'Madlibs',
                description=f'Word for: **{word}**? (Reply to this message with your word)',
                color=green
            )
            message = await ctx.send(embed=e)
            def check(m):
                try:
                    return m.author == ctx.author and message.channel == m.channel and m.reference.message_id == message.id
                except AttributeError:
                    return False
            msg = await self.bot.wait_for('message', check=check, timeout=180.0)
            responses.append(msg.content)
        await idiotlibrary.pages_simple(ctx, sheet[1].format(*responses))

    @commands.command(description='Monke Noises!')
    async def monkenoises(self, ctx, vc: discord.VoiceChannel = None):
        if vc is None:
            await ctx.send('Please specify a voice channel.')
        else:
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
            message = await ctx.send(f'Monke-ing the voice channel **{vc.name}**')
            player = discord.FFmpegPCMAudio('MonkeySounds.mp3')
            await vc.connect()
            ctx.voice_client.play(player)
            await message.edit(content=f'**{vc.name}** has been monke noised.')
            await asyncio.sleep(120)
            if ctx.voice_client.is_playing():
                pass
            else:
                await ctx.voice_client.disconnect()



def setup(client):
    client.add_cog(Fun(client))

async def main():
    snake_game = SnakeGame()
    await snake_game.generate_board(3)

if __name__ == '__main__':
    asyncio.run(main())
    os.system(r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:\workspace\idiotbot\idiot bot.py"')