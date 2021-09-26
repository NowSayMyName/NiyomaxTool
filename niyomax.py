import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

@bot.command(name='close')
async def close(ctx):
    await ctx.message.delete()
    await bot.close()

@bot.command(name='add')
async def add(ctx, *args):
    await ctx.message.delete()
    if len(args) < 3:
        await ctx.send("expected command: !add \"section\" \"band\” \"music1\" \"music2\" ...")
    else:
        lst_bands = await create_band_list(args[0], await ctx.channel.history(limit=200).flatten())
        add_music(lst_bands, args[1], args[2:]) 
        for msg in create_messages(args[0], lst_bands): 
            await ctx.send(msg)

@bot.command(name='rm')
async def remove(ctx, *args):
    await ctx.message.delete()
    if len(args) != 3:
        await ctx.send("expected command: !rm \"section\" \"band\” \"music\"")
    else:
        lst_bands = await create_band_list(args[0], await ctx.channel.history(limit=200).flatten())
        remove_music(lst_bands, args[1], args[2:]) 
        for msg in create_messages(args[0], lst_bands): 
            await ctx.send(msg)

@bot.command(name='redo')
async def redo(ctx):
    await ctx.message.delete()
    lst_bands = await create_band_list_from_java(await ctx.channel.history(limit=200).flatten())
    for msg in create_messages("6 cordes", lst_bands): 
        await ctx.send(msg)

def is_in_tuple_list(lst, key):
    for list_key, obj in lst:
        if list_key == key:
            return True
    return False

async def create_band_list_from_java(messages):
    lst_bands = []

    for msg in messages:
        if "```java\n" in msg.content:
            lines = msg.content.splitlines()
            for line in lines[3:-1]:
                if line != "":
                    line = line.split()
                    if len(line) > 0:
                        if "()" in line[-1]:
                            name =  ' '.join(line[0:])
                            if not is_in_tuple_list(lst_bands, name[:-2]):
                                lst_bands.append((name[:-2], []))
                        else:
                            lst_bands[-1][1].append(' '.join(line[0:]))

            await discord.Message.delete(msg)

    return lst_bands

async def create_band_list(section, messages):
    lst_bands = []

    for msg in messages:
        if ("```md\n> " + section) in msg.content:
            lines = msg.content.splitlines()
            for line in lines[3:-1]:
                if line != "":
                    line = line.split()
                    if line[0] == '#' and not is_in_tuple_list(lst_bands, line[1]):
                        lst_bands.append((line[1], []))
                    elif line[0] == '*':
                        lst_bands[-1][1].append(' '.join(line[1:]))

            await discord.Message.delete(msg)

    return lst_bands

def add_music(lst_bands, name, lst_musics):
    name_exists = False
    for band_name, band_musics in lst_bands:
        if band_name == name:
            band_musics.extend(x for x in lst_musics if x not in band_musics)
            name_exists = True
            break

    if not name_exists:
        lst_bands.append((name, lst_musics))

def remove_music(lst_bands, name, music):
    for band_name, band_musics in lst_bands:
        if band_name == name:
            if music in band_musics:
                band_musics.remove(music)
            break

def create_messages(section, lst_bands):
    lst_msgs = []

    appended = False
    msg = "```md\n"
    msg += "> " + section + '\n'
    for name, lst_musics in sorted(lst_bands, key=lambda tup: tup[0]):
        msg += "\n# " + name + "\n"
        for music in sorted(lst_musics):
            next_line = "* " + music + '\n'
            if (len(msg) + len(next_line) + len("```")) >= 2000:
                msg += "```"
                lst_msgs.append(msg)
                appended = True
                msg = "```md\n"
                msg += "> " + section + '\n'
                msg += "\n# " + name + "\n"

            msg += next_line
            appended = False

    if not appended:
        msg += "```"
        lst_msgs.append(msg)

    return lst_msgs

bot.run(TOKEN)