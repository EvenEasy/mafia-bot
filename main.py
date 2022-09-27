import json
import discord, config, random
from function_buttons import function_buttons, TruthOrDare
from BaseData import Basedata
from discord.ext import commands
from discord.utils import get
from discord import ButtonStyle
from discord.ui import Button
from discord import app_commands

class BotClient(commands.Bot):
    def __init__ (self):
        super().__init__(command_prefix="$",intents=discord.Intents.all())
        #self.synced = False

    async def on_ready(self):
        print (f"[ {client.user} ] Bot is ready ! ")
        #await tree.sync()
        TruthOrDare.CardsENG = TruthOrDare.GetCardsENG()
        TruthOrDare.CardsUA = TruthOrDare.GetCardsUA()

client = BotClient()
tree = client.tree

#client = commands.Bot(command_prefix='$', intents=discord.Intents.all())
db = Basedata("database.db")
function_button = function_buttons(client, db)

#----------------------------------------------------MAIN-EVENT------------------------------------------------------
@client.event
async def on_member_join(member):
    WelcomeChannel = client.get_channel(940592256258293821)
    ChatChannel = client.get_channel(940596989509394463)

    guild = client.get_guild(940590174117691462)
    WelcomeEmbed = discord.Embed(title="WELCOME", description=f"""WELCOME TO {guild.name} SERVER
{member.mention}
<#940592983944855572> - **Rules** of the SERVER
<#940607866912510003> - **News** of the SERVER
<#940619063317626900> - Choose your **Skills**
    """, colour=discord.Color.random())
    try:
        WelcomeEmbed.set_thumbnail(url=member.avatar.url)
    except Exception:
        pass
    WelcomeEmbed.set_image(url=config.imgs[random.randint(0, len(config.imgs) - 1)])
    roles = [get(guild.roles, id=id1) for id1 in (940600596124274748, 940599148862914562, 940600398614519858)]
    for role in roles:
        await member.add_roles(role)
    await WelcomeChannel.send(embed=WelcomeEmbed)
    await ChatChannel.send(f"What's up {member.mention}")


    #reqisterCHn = client.get_channel(961932279087763517)
    #GameChannel = client.get_channel(961932355453480980)
    #AdminChannel = client.get_channel(962959320696360990)

    #await reqisterCHn.purge()
    #await GameChannel.purge()
    #await AdminChannel.purge()
    #await AdminChannel.send(embed=discord.Embed(title="Admin Panel", colour=discord.Color.blurple()), view=function_button.GetView
    #    ([Button(style=ButtonStyle.green,label="News", custom_id="send_news"), Button(label="Send Message", custom_id="send_message"), Button(style=ButtonStyle.blurple,label="Add member Project", custom_id="add_project")]))
    #await reqisterCHn.send(embed=discord.Embed(title="Реєстрація", description="Натисніть **Join** для того щоб приєднатись до гри", colour=discord.Color.greyple()),view=function_button.GetView(
    #    [Button(style=ButtonStyle.green,label="Join", custom_id="join_to_the_game"), Button(label="unjoin", custom_id="unjoin_from_the_game")]))
    #db.GameMessage = await GameChannel.send(embed=discord.Embed(title="Готові?", description="Натисніть **Готовий** якщо ви готові до гри\n*гра почнеться тільки після того як всі учасники будуть готові*", colour=discord.Color.greyple()),view=function_button.GetView(
    #    [Button(style=ButtonStyle.green,label="Готовий", custom_id="iready")]))
    #await function_button.set_permissions()

@client.listen()
async def on_interaction(bttn : discord.Integration):
    print(bttn.type)
    print(bttn.data)
    if bttn.type == discord.InteractionType.component:
        match bttn.data["custom_id"].split("_"):
            case ["iready"]:
                if db.readyPeople <= len(db.GetSqlite("SELECT * FROM Game")) and not db.isStarted:
                    try:
                        await bttn.response.send_message()
                    except:
                        pass
                    try:
                        if db.GetSqlite(f"SELECT Took FROM Game WHERE user_id = {bttn.author.id}")[0][0] == "Ready":
                            return
                    except IndexError:
                        pass
                    db.readyPeople += 1
                    db.GetSqlite(f"UPDATE Game SET Took = 'Ready' WHERE user_id = {bttn.author.id}")
                    embed = discord.Embed(title="Готові?",description=f"Натисніть **Готовий** якщо ви готові до гри\n*гра почнеться тільки після того як всі учасники будуть готові*", colour=discord.Color.greyple())
                    if db.readyPeople > 0:
                        embed.set_footer(text=f'Готові : {db.readyPeople}')
                    await db.GameMessage.edit(embed=embed)
                    if db.readyPeople >= len(db.GetSqlite("SELECT Took FROM Game")):# and db.readyPeople >= 4:
                        db.isStarted = True
                        await db.GameMessage.delete()
                        await function_button.start()
            #--------------GAME-MENU-BUTTONS---------------
            case ["join", "to", "the", "game"]:
                GameChannelVoice = client.get_channel(965921503638069279)
                if db.GetLastId() >= 15:
                    await bttn.response.send_message(content="Все, я вже не приймаю,\nГравців вже 15")
                elif db.isStarted:
                    await bttn.response.send_message(content="Гра вже розпочата, очікуй кінець гри)")
                elif db.in_game(bttn.author.id) != True:
                    db.add_user(db.GetLastId(), bttn.author.id, bttn.author)
                    role = get(bttn.author.guild.roles, id=951419192781996043)
                    await bttn.author.add_roles(role)
                    await bttn.response.send_message(content=f"Добре, я тебе долучила до гри)\nочікуйте початок тут <#961932355453480980>\nі тут {GameChannelVoice.mention}")
                else:
                    await bttn.response.send_message(content=f"Ти в ігрі\nОчікуй початок ігри тут <#961932355453480980>\nі тут {GameChannelVoice.mention}")

            case ["unjoin","from","the", "game"]:
                if db.in_game(bttn.author.id):
                    db.remove_user(bttn.author.id)
                    role = get(bttn.author.guild.roles, id=951419192781996043)
                    await bttn.author.remove_roles(role)
                    await bttn.response.send_message(content="Я тебе вилучила з гри)")
                else:
                    await bttn.response.send_message(content="Тебе і так немає в списку гравців)")
            
            case ["TruthOrDare",type_card, language]:
                type_card1 = ('Правда' if type_card=='Truth Question' else 'Дія') if language == "UA" else type_card.split(" ")[0]
                cards = TruthOrDare.CardsUA if language == "UA" else TruthOrDare.CardsENG
                n = cards[type_card]
                n1 = n[random.randint(0, len(n)-1)]
                await bttn.response.edit_message(embed=discord.Embed(title="Truth Or Dare", description = f"**{type_card1}** :\n {n1}", colour=discord.Color.green()))

            #--------------ADMIN-MENU-BUTTONS---------------

            case ["send","news"]:
                try:
                    await function_button.news(bttn)
                except Exception as E:
                    print(f"NEWS - {E}")

            case ["send","message"]:
                try:
                    await function_button.Send_msg(bttn)
                except Exception as E:
                    print(f"SendMsg - {E}")

            case ["add", "project"]:
                try:
                    await function_button.Send_member_project(bttn)
                except Exception as E:
                    print(f"NEWS - {E}")
            case ["complaint", from_user_id]:
                msg1 = await bttn.channel.send(embed=discord.Embed(title="Message", description="Enter your message to the user", colour=discord.Color.from_rgb(54,57,63)).set_footer(text="""Or type none for skip message"""))
                message = await client.wait_for("message", check=lambda i:bttn.channel.id == i.channel.id and i.author.id == bttn.user.id)
                try:
                    await msg1.delete()
                except Exception:
                    pass
                try:
                    await message.delete()
                except Exception:
                    pass

                message_to_user = " " if message.content.lower() in ("none") else f"\n\n``{message.content}``"

                user = await client.fetch_user(from_user_id)
                embed = discord.Embed(title=f"COMPLAINT", description=f"""Your complaint has been considered. thanks a lot for your assistance. Moderator response: {message_to_user}""", colour=discord.Color.from_rgb(54,57,63))
                embed.set_author(name=str(bttn.user), icon_url=bttn.user.avatar.url)
                await user.send(embed=embed)


                try:
                    await bttn.message.delete()
                except Exception:
                    pass
            case ["ok"]:
                try:
                    await bttn.message.delete()
                except Exception:
                    pass


@tree.command(description="complaint")
async def complaint(ctx, member:discord.Member, reason:str):
    admin_channel = client.get_channel(962959320696360990)
    await admin_channel.send(
        embed=discord.Embed(title="COMPLAINT", description=f"User {ctx.author.mention} enter a complaint", colour=discord.Color.green()).add_field(
            name="Member", value=f"{member.mention}"
        ).add_field(
            name="Reason", value=reason
        ),
        view=function_button.GetView([
            Button(style=ButtonStyle.blurple, label="Answer", custom_id=f"complaint_{ctx.user.id}"),
            Button(style=ButtonStyle.green, label="Ok", custom_id="ok")
        ]))
    await ctx.response.send_message(ephemeral=True, embed=discord.Embed(title="complaint", description="Your complaint has been sent to the server administration, wait for a solution", color=discord.Color.green()))

@tree.command(description="New command Help")
async def help(ctx):
    embed=discord.Embed(
        title="Commands",
        description="Your complaint has been sent to the server administration, wait for a solution",
        color=discord.Color.green(),
        )
    embed.add_field(name="/info", value="Information about the bot")
    embed.add_field(name="/complaint", value="Write a complaint about a member")
    await ctx.response.send_message(ephemeral=True,embed=embed)

@tree.command(description="Information about the bot")
async def info(ctx):
    embed=discord.Embed(
        title="Akito Bot",
        description="""
Hi, i'm Akito bot, and i'm not only a Moderator bot, i'm also a game bot !
by using the `/help` command, you will see the available commands
I have only 1 game available at the moment
it's "truth or dare"
""",
        color=discord.Color.green(),
        )
    await ctx.response.send_message(ephemeral=True,embed=embed)

@tree.command(description='Start game "Truth or Dare"')
async def truth_or_dare(ctx):
    await function_button.StartTruthOrDare(ctx)

@tree.command(description='mute member')
@commands.has_permissions(administrator=True)
async def mute(ctx, member:discord.Member, reason:str):
    role = get(ctx.guild.roles, id=1020201933933379665)
    await member.add_roles(role, reason=reason)
    await ctx.response.send_message("Done!",ephemeral=True)

@tree.command(description='unmute member')
@commands.has_permissions(administrator=True)
async def unmute(ctx, member:discord.Member):
    role = get(ctx.guild.roles, id=1020201933933379665)
    await member.remove_roles(role)
    await ctx.response.send_message("Done!",ephemeral=True)

@tree.command(description='ban member')
@commands.has_permissions(administrator=True)
async def ban(ctx, member:discord.Member, reason:str):
    try:
        await member.ban(reason=reason)
    except Exception as E:
        await ctx.response.send_message(f"Except Exception:\n{str(E)}",ephemeral=True)
    await ctx.response.send_message("Done!",ephemeral=True)

@tree.command(description='unban member')
@commands.has_permissions(administrator=True)
async def unban(ctx, member:discord.Member):
    try:
        await member.unban()
    except Exception as E:
        await ctx.response.send_message(f"Except Exception:\n{str(E)}",ephemeral=True)
    await ctx.response.send_message("Done!",ephemeral=True)

#-------------------------CLEAR-------------------------
@tree.command(description='clear')
@commands.has_permissions(administrator=True)
async def clear(ctx, limit:int=10):
    await ctx.channel.purge(limit = limit)
    await ctx.response.send_message("Done !",ephemeral=True)

#---------------------GAME_FUNCTION---------------------

@tree.command(description='contact Sqlite')
@commands.has_permissions(administrator=True)
async def sql(ctx, sql:str):
    res = db.GetSqlite(sql)
    print(res)
    await ctx.send(res)

@tree.command(description='Add role to Auto Roles')
@commands.has_permissions(administrator=True)
async def add_role_reaction(ctx, role:discord.Role, emoji:str):
    config.auto_roles[emoji] = role.id
    await ctx.response.send_message("Done !",ephemeral=True)

@tree.command(description='Remove role to Auto Roles')
@commands.has_permissions(administrator=True)
async def remove_role_reaction(ctx, emoji:str):
    del config.auto_roles[emoji]
    await ctx.response.send_message("Done !",ephemeral=True)

@tree.command(description='Add role to Auto Roles')
@commands.has_permissions(administrator=True)
async def get_all_author_roles(ctx):
    await ctx.response.send_message(f"Auto role dict{json.dumps(config.auto_roles)}",ephemeral=True)

@client.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == config.autorolesChnID and payload.user_id != client.user.id and payload.emoji.name in config.auto_roles.keys():
        role = get(client.get_guild(payload.guild_id).roles, id=config.auto_roles[payload.emoji.name])
        await payload.member.add_roles(role)

@client.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id == config.autorolesChnID and payload.emoji.name in config.auto_roles.keys():
        guild = client.get_guild(payload.guild_id)
        role = get(guild.roles, id=config.auto_roles[payload.emoji.name])
        member = await guild.fetch_member(payload.user_id)
        await member.remove_roles(role)


#------------------------RUN_BOT------------------------
client.run(config.TOKEN)