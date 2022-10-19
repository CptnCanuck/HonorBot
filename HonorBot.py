import discord
import logging
import sqlite3
import os.path
import typing
from discord.ext import commands

#Connect to Database to read and write honor points and other data
con = sqlite3.connect('honordb.sqlite')
cur = con.cursor()

#Check if the honor table exists already. If not, create it in the database.
cur.execute('''CREATE TABLE if not exists honor(username, honor, honorreceived, honorgiven, dishonorreceived, dishonorgiven)''')
con.commit()

#Set bot command prefix.
bot = commands.Bot(command_prefix='?')

#Log Bot login for debugging
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

#Main honor command. Allows user to input another user, and a value to adjust their honor score by. Cheekily reduces your score if you try to adjust your own.
@bot.command()
async def honor(ctx, member: discord.Member, points: int):
    honorrecipient = str(member)
    honorgiver = str(ctx.message.author)
    if ctx.message.author == member and points > 0:
        await ctx.send('Cant give yourself honor bozo. Very dishonorable. Minus 5 points.')
        cur.execute('UPDATE honor SET honor = honor - 5 WHERE username = ?',(honorgiver,))
        cur.execute('UPDATE honor SET dishonorreceived = dishonorreceived - 5 WHERE username = ?',(honorgiver,))
        con.commit()
    elif points <= 20 and points >= -20:
        await ctx.send('Awarded {person} {honor} honor points.'.format(person = member, honor = points))
        cur.execute('SELECT username FROM honor WHERE username = ?',(honorrecipient,))
        if cur.fetchone():
            cur.execute('UPDATE honor SET honor = honor + ? WHERE username = ?',(points,honorrecipient,))
            if points < 0:
                cur.execute('UPDATE honor SET dishonorreceived = dishonorreceived + ? WHERE username = ?',(points,honorrecipient,))
            else:
                cur.execute('UPDATE honor SET honorreceived = honorreceived + ? WHERE username = ?',(points,honorrecipient,))
            con.commit()
        else:
            if points < 0:
                cur.execute("INSERT INTO honor VALUES (?,?,?,?,?,?)",(honorrecipient,points,0,0,0,points,))
            else:
                cur.execute("INSERT INTO honor VALUES (?,?,?,?,?,?)",(honorrecipient,points,0,points,0,0,))
            con.commit()
        cur.execute('SELECT username FROM honor WHERE username = ?',(honorgiver,))
        if cur.fetchone():
            if points < 0:
                cur.execute('UPDATE honor SET dishonorgiven = dishonorgiven + ? WHERE username = ?',(points,honorgiver,))
            else:
                cur.execute('UPDATE honor SET honorgiven = honorgiven + ? WHERE username = ?',(points,honorgiver,))
            con.commit()
        else:
            if points < 0:
                cur.execute("INSERT INTO honor VALUES (?,?,?,?,?,?)",(honorgiver,0,0,0,0,points,))
            else:
                cur.execute("INSERT INTO honor VALUES (?,?,?,?,?,?)",(honorgiver,0,0,points,0,0,))
            con.commit()
    else:
        await ctx.send("Whoah, that's way too much. No one is that (dis)honorable. Try again.")

#Leaderboard command. Reads columns from honordb.sqlite and prints it to a discord embed message.
@bot.command()
async def honorboard(ctx, size: typing.Optional[int] = 10):
    embed=discord.Embed(title="Honor Leaderboard", color=discord.Color.red())
    cur.execute('SELECT * FROM honor ORDER BY honor DESC')
    leaderboard = cur.fetchall()
    Username = ''
    Honor = ''
    Honorreceived = ''
    Honorgiven = ''
    Dishonorreceived = ''
    Dishonorgiven = ''
    leaderboardsize = 0
    for row in leaderboard:
        if leaderboardsize < size:
            Username += row[0] + '\n'
            Honor += str(row[1]) + '\n'
            #Honorreceived += str(row[2]) + '\n'
            #Honorgiven += str(row[3]) + '\n'
            #Dishonorreceived += str(row[4]) + '\n'
            #Dishonorgiven += str(row[5]) + '\n'
            leaderboardsize += 1
        else:
            break
    embed.add_field(name='Username', value=Username, inline=True)
    embed.add_field(name='Honor', value=Honor, inline=True)
    #embed.add_field(name='Honor Received', value=Honorreceived, inline=True)
    #embed.add_field(name='Honor Given', value=Honorgiven, inline=True)
    #embed.add_field(name='Dishonor Received', value=Dishonorreceived, inline=True)
    #embed.add_field(name='Dishonor Given', value=Dishonorgiven, inline=True)
    return await ctx.send(embed=embed)

#Run the bot with private discord key
bot.run('ODcyMDM4NDcwODQxOTI5NzY4.YQkDHQ.yj-Lnvu6iCejtnbeT28mQiV0lPs')
