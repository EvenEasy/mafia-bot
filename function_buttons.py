try:
    import discord, config, asyncio, random, grequests
    from BaseData import Basedata
    from discord.ext import commands
    from discord.utils import get
    from discord.ui import Button, View, Select
    from discord import ButtonStyle, SelectOption
    from bs4 import BeautifulSoup as BS
except Exception as E:
    print(f"ERROR - {E}")

class TruthOrDare:
    CardsENG = {}
    CardsUA = {}

    def GetCardsENG():
        AllCards = {
            "Truth Question" : [],
            "Dare Tasks" : []
        }
        headers = {
            "User-agent" : "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 OPR/77.0.4054.298"    
        }
        url = "https://www.cosmopolitan.com/uk/worklife/a32313763/truth-or-dare-questions"
        r = grequests.map([grequests.get(url=url, headers=headers)])[0]
        try:
            soup = BS(r.text, "html.parser")
            cards = soup.find_all("ul", class_="body-ul")
            for card in cards[0].find_all("li"):
                AllCards["Truth Question"].append(card.text.strip())

            for card in cards[1].find_all("li"):
                AllCards["Dare Tasks"].append(card.text.strip())
            return AllCards
            
        except Exception as E:
            print(f"Error - {E}")
            return

    def GetCardsUA():
        AllCards = {
            "Truth Question" : [],
            "Dare Tasks" : []
        }
        headers = {
            "User-agent" : "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 OPR/77.0.4054.298"    
        }
        url = "https://men.24tv.ua/pravda-diya-pitannya-zavdannya-dlya-druziv-hloptsiv-divchat_n1774441"
        r = grequests.map([grequests.get(url=url, headers=headers)])[0]
        try:
            soup = BS(r.text, "html.parser")
            cards = soup.find_all("ol")
            for card in cards[random.randint(0, len(cards)-1)].find_all("li"):
                AllCards["Truth Question"].append(card.text.strip())

            for card in cards[-1].find_all("li"):
                AllCards["Dare Tasks"].append(card.text.strip())
            return AllCards
        except Exception as E:
            print(f"Error - {E}")
            return


class function_buttons:
    def __init__(self, bot, db):
        self.client = bot
        self.db = db

    def GetView(self,buttons : list) -> discord.ui.View:
        view = View()
        for bttn in buttons : view.add_item(bttn)
        return view  


    async def set_permissions(self, isSilence = False):
        GameChannel = self.client.get_channel(961932355453480980)
        guild = self.client.get_guild(940590174117691462)
        await GameChannel.set_permissions(get(guild.roles, id=951419192781996043), send_messages=isSilence)

    async def Send_msg(self, bttn):
        try:
            await bttn.response.send_message()
        except:
            pass
        msg = await bttn.channel.send(embed=discord.Embed(title="Channel", description="Enter channel ID", colour=discord.Color.blurple()))
        try:
            chnID = await self.client.wait_for("message", check=lambda i:i.channel == bttn.channel and (i.content).isdigit(),timeout=60)
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(title="Time is up", description="", colour=discord.Color.red()))
            await asyncio.sleep(7)
            await msg.delete()
            return
        await chnID.delete()
        NewsChannel = self.client.get_channel(int(chnID.content))
        try:
            await bttn.response.send_message()
        except:
            pass
        await msg.edit(embed=discord.Embed(title="Headline", description="Enter the message headline", colour=discord.Color.blurple()))
        try:
            resp = await self.client.wait_for("message", check=lambda i:i.channel == bttn.channel,timeout=60)
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(title="Time is up", description="", colour=discord.Color.red()))
            await asyncio.sleep(7)
            await msg.delete()
            return
        title=resp.content
        await resp.delete()

        await msg.edit(embed=discord.Embed(title="Description", description="Enter the message description", colour=discord.Color.blurple()))
        try:
            resp1 = await self.client.wait_for("message", check=lambda i:i.channel == bttn.channel, timeout=600)
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(title="Time is up",description="" ,colour=discord.Color.red()))
            await asyncio.sleep(7)
            await msg.delete()
            return
        description = resp1.content
        await resp1.delete()
        while True:
            await msg.edit(embed=discord.Embed(title="Image",description="Will you use image?" ,colour=discord.Color.red()), view=self.GetView([Button(style=ButtonStyle.green,label="Set", custom_id="Set"), Button(label="No", custom_id="No")])
                )
            embedNews = discord.Embed(title=title, description=description, colour=discord.Color.blurple())
            respImage = await self.client.wait_for("interaction", check=lambda i:i.channel == bttn.channel, timeout=600)
            try:
                await respImage.response.send_message()
            except:
                pass
            if respImage.custom_id == "Set":
                await msg.edit(embed=discord.Embed(title="Image",description="Set image" ,colour=discord.Color.blurple()), view=View())
                url = await self.client.wait_for("message", check=lambda i:i.channel == bttn.channel, timeout=600)
                try:
                    url1 = url.content if url.content != "" else url.attachments[0].url
                except Exception as E:
                    print(f"EXCEPTION - {E}")
                    continue
                try:
                    embedNews.set_image(url=url1)
                    await url.delete()
                except Exception:
                    continue

            await msg.edit(embed=embedNews,
                view=self.GetView([Button(style=ButtonStyle.green, label="Send"), Button(style=ButtonStyle.red, label="Delete")])
            )
            try:
                resp2 = await self.client.wait_for("interaction", check=lambda i:i.channel == bttn.channel, timeout=60)
            except asyncio.TimeoutError:
                await msg.edit(embed=discord.Embed(title="Time is up", colour=discord.Color.blurple()))
                await asyncio.sleep(7)
                await msg.delete()
                return
            try:
                await resp2.response.send_message()
            except:
                pass
            if resp2.custom_id == "Send":
                await NewsChannel.send(embed=embedNews)
                await msg.edit(embed=discord.Embed(title="Great", description=f"The news was sent to channel {NewsChannel.mention}", colour=discord.Color.green()), view=View())
                await asyncio.sleep(5)
                await msg.delete()
                return
            elif resp2.custom_id == "Delete":
                await msg.delete()
                return
            break

    async def Send_member_project(self, bttn):
        NewsChannel = self.client.get_channel(1009433674263056384)
        try:
            await bttn.response.send_message()
        except:
            pass
        msg = await bttn.channel.send(embed=discord.Embed(title="Headline", description="Enter the news headline", colour=discord.Color.blurple()))
        try:
            resp = await self.client.wait_for("message", check=lambda i:i.channel == bttn.channel,timeout=600)
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(title="Time is up", description="", colour=discord.Color.red()))
            await asyncio.sleep(7)
            await msg.delete()
            return
        title=resp.content
        await resp.delete()

        await msg.edit(embed=discord.Embed(title="Description", description="Enter the news description", colour=discord.Color.blurple()))
        try:
            resp1 = await self.client.wait_for("message", check=lambda i:i.channel == bttn.channel, timeout=12000)
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(title="Time is up",description="" ,colour=discord.Color.red()))
            await asyncio.sleep(7)
            await msg.delete()
            return
        description = resp1.content
        await resp1.delete()
        while True:
            await msg.edit(embed=discord.Embed(title="Image",description="Will you use image?" ,colour=discord.Color.red()), view=self.GetView(
                [Button(style=ButtonStyle.green,label="Set"), Button(label="No")]))
            embedNews = discord.Embed(title=title, description=description, colour=discord.Color.blurple())
            respImage = await self.client.wait_for("interaction", check=lambda i:i.channel == bttn.channel, timeout=6000)
            try:
                await respImage.response.send_message()
            except:
                pass
            if respImage.custom_id == "Set":
                await msg.edit(embed=discord.Embed(title="Image",description="Set image" ,colour=discord.Color.blurple()), view=View())
                url = await self.client.wait_for("message", check=lambda i:i.channel == bttn.channel, timeout=600)
                try:
                    url1 = url.content if url.content != "" else url.attachments[0].url
                except Exception as E:
                    print(f"EXCEPTION - {E}")
                    continue
                try:
                    embedNews.set_image(url=url1)
                    await url.delete()
                except Exception:
                    continue

            await msg.edit(embed=embedNews,
                view=self.GetView([Button(style=ButtonStyle.green, label="Send"), Button(style=ButtonStyle.red, label="Delete")])
            )
            try:
                resp2 = await self.client.wait_for("interaction", check=lambda i:i.channel == bttn.channel, timeout=6000)
            except asyncio.TimeoutError:
                await msg.edit(embed=discord.Embed(title="Time is up", colour=discord.Color.blurple()))
                await asyncio.sleep(7)
                await msg.delete()
                return
            try:
                await resp2.response.send_message()
            except:
                pass
            if resp2.custom_id == "Send":
                await NewsChannel.send(embed=embedNews)
                await msg.edit(embed=discord.Embed(title="Great", description=f"The news was sent to channel {NewsChannel.mention}", colour=discord.Color.green()), view=View())
                await asyncio.sleep(5)
                await msg.delete()
                return
            elif resp2.custom_id == "Delete":
                await msg.delete()
                return
            break

    async def news(self, bttn):
        NewsChannel = self.client.get_channel(940607866912510003)
        try:
            await bttn.response.send_message()
        except:
            pass
        msg = await bttn.channel.send(embed=discord.Embed(title="Headline", description="Enter the news headline", colour=discord.Color.blurple()))
        try:
            resp = await self.client.wait_for("message", check=lambda i:i.channel == bttn.channel,timeout=600)
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(title="Time is up", description="", colour=discord.Color.red()))
            await asyncio.sleep(7)
            await msg.delete()
            return
        title=resp.content
        await resp.delete()

        await msg.edit(embed=discord.Embed(title="Description", description="Enter the news description", colour=discord.Color.blurple()))
        try:
            resp1 = await self.client.wait_for("message", check=lambda i:i.channel == bttn.channel, timeout=6000)
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(title="Time is up",description="" ,colour=discord.Color.red()))
            await asyncio.sleep(7)
            await msg.delete()
            return
        description = resp1.content
        await resp1.delete()
        while True:
            await msg.edit(embed=discord.Embed(title="Image",description="Will you use image?" ,colour=discord.Color.red()), view=self.GetView([Button(style=ButtonStyle.green,label="Set", custom_id="Set"), Button(label="No", custom_id="No")]))
            embedNews = discord.Embed(title=title, description=description, colour=discord.Color.blurple())
            respImage = await self.client.wait_for("interaction", check=lambda i:i.channel == bttn.channel, timeout=6000)
            try:
                await respImage.response.send_message()
            except:
                pass
            if respImage.custom_id == "Set":
                await msg.edit(embed=discord.Embed(title="Image",description="Set image" ,colour=discord.Color.blurple()), view=View())
                url = await self.client.wait_for("message", check=lambda i:i.channel == bttn.channel, timeout=600)
                try:
                    url1 = url.content if url.content != "" else url.attachments[0].url
                except Exception as E:
                    print(f"EXCEPTION - {E}")
                    continue
                try:
                    embedNews.set_image(url=url1)
                    await url.delete()
                except Exception:
                    continue

            await msg.edit(embed=embedNews,
                view=self.GetView([Button(style=ButtonStyle.green, label="Send", custom_id="Send"), Button(style=ButtonStyle.red, label="Delete", custom_id="Delete")])
            )
            try:
                resp2 = await self.client.wait_for("interaction", check=lambda i:i.channel == bttn.channel, timeout=6000)
            except asyncio.TimeoutError:
                await msg.edit(embed=discord.Embed(title="Time is up", colour=discord.Color.blurple()))
                await asyncio.sleep(7)
                await msg.delete()
                return
            try:
                await resp2.response.send_message()
            except:
                pass
            if resp2.custom_id == "Send":
                await NewsChannel.send("@everyone",embed=embedNews)
                await msg.edit(embed=discord.Embed(title="Great", description=f"The news was sent to channel {NewsChannel.mention}", colour=discord.Color.green()), view=View())
                await asyncio.sleep(5)
                await msg.delete()
                return
            elif resp2.custom_id == "Delete":
                await msg.delete()
                return
            break

    async def start(self):
        Number_Night = 1
        GameChannel = self.client.get_channel(961932355453480980)
        guild = self.client.get_guild(940590174117691462)
        await asyncio.sleep(2)
        Message = await GameChannel.send(embed=discord.Embed(description="Розпочнем)", colour=discord.Color.blurple()))
        players = self.db.GetSqlite("SELECT user_id FROM Game")
        PlayerID=random.randint(0, len(players)-1)
        self.db.GetSqlite(f"UPDATE Game SET status = 'Мафія' WHERE user_id = {players[PlayerID][0]}")
        for id, status in self.db.GetSqlite("SELECT user_id, status FROM Game"):
            try:
                user = await self.client.fetch_user(id)
                url = self.db.peoplePhotoUrl if status == "Мирний житель" else self.db.mafiaPhotoUrl
                embed = discord.Embed(title="Ваша Карточка", description=f"Ви {status}", colour=discord.Color.blurple()).set_thumbnail(url=url)
                await user.send(embed=embed)
            except:
                continue
        while True:
            await asyncio.sleep(5)
            await Message.edit(embed=discord.Embed(title="Настала Ніч", description="Місто засинає", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlNight))
            await asyncio.sleep(5)
            await Message.edit(embed=discord.Embed(title="Настала Ніч", description="Просинається Мафія", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlNight))
            await asyncio.sleep(5)
            if not bool(len(self.db.GetSqlite("SELECT user_id FROM Game WHERE status = 'Мирний житель'"))):
                await Message.edit(embed=discord.Embed(title="Гра закінчена", description=f"Гра закінчина, більше не залишелось мирних жителів !", colour=discord.Color.blurple()), view=View())
                break
            await Message.edit(embed=discord.Embed(title="Настала Ніч", description="Мафія виберає жертву", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlNight))
            print(self.db.GetSqlite("SELECT user_id FROM Game WHERE status = 'Мафія'"))
            mafia = await self.client.fetch_user(self.db.GetSqlite("SELECT user_id FROM Game WHERE status = 'Мафія'")[0][0])
            options = [SelectOption(label=name,value=user_id, emoji="👤") for name, user_id in self.db.GetSqlite("SELECT user_name, user_id FROM Game WHERE status = 'Мирний житель'")]
            killedUser : discord.Member
            msg1 = await mafia.send(embed=discord.Embed(title="Жертва", description="Вибери жертву", colour=discord.Color.blurple()), view=self.GetView([
                Select(
                    placeholder="вибери жертву",
                    options=options
                )
            ]))
            try:
                resp = await self.client.wait_for("select_option", timeout=60)
                try:
                    killedUser = await guild.fetch_member(int(resp.values[0]))
                except:
                    pass
                try:
                    await resp.response.send_message()
                except:
                    pass
            except asyncio.TimeoutError:
                await msg1.edit(embed=discord.Embed(title="Time is up", description="Вибери жертву", colour=discord.Color.blurple()), view=View())
            await asyncio.sleep(5)
            await msg1.delete()
            await Message.edit(embed=discord.Embed(title="Настала Ніч", description="Мафія виберає жертву", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlNight))
            role = get(guild.roles, id=951419192781996043)
            await killedUser.remove_roles(role)
            if not bool(len(self.db.GetSqlite("SELECT user_id FROM Game WHERE status = 'Мирний житель'"))):
                await Message.edit(embed=discord.Embed(title="Гра закінчена", description=f"Гра закінчина, більше не залишелось мирних жителів !", colour=discord.Color.blurple()), view=View())
                break

            self.db.GetSqlite(f"DELETE FROM Game WHERE user_id = {resp.values[0]}")
            await Message.edit(embed=discord.Embed(title="Настала Ніч", description="Мафія вибрала жертву", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlNight))
            await asyncio.sleep(5)
            await Message.edit(embed=discord.Embed(title=f"День {Number_Night}", description="Місто просинається", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlDay))
            await asyncio.sleep(2)
            await Message.edit(embed=discord.Embed(title=f"День {Number_Night}", description=f"За цю ніч мафія забрала {killedUser.mention}", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlDay))
            await asyncio.sleep(6)
            await Message.edit(embed=discord.Embed(title=f"День {Number_Night}", description="Як ви думаєте\nХто Мафія?\nу вас є 70 секунд щоб вирішити хто це зробив", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlDay))
            await asyncio.sleep(70)
            await Message.edit(embed=discord.Embed(title=f"День {Number_Night}", description="Час вийшов", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlDay))
            await asyncio.sleep(5)

            while True:
                await Message.edit(embed=discord.Embed(title=f"День {Number_Night}", description="Виберіть того хто на вашу думку є мафією", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlDay), components=[
                    Select(
                        placeholder="Виберіть учасника",
                        options=[SelectOption(label=name, value=user_id, emoji="👤") for name, user_id in self.db.GetSqlite("SELECT user_name, user_id FROM Game")]
                    )
                ])
                try:
                    resp = await self.client.wait_for("select_option", timeout=60)
                except asyncio.TimeoutError:
                    await Message.edit(embed=discord.Embed(title="Time is up", description="Вибери жертву", colour=discord.Color.blurple()), view=View())
                try:
                    await resp.response.send_message()
                except:
                    pass
                self.db.playerID = resp.values[0]
                await Message.edit(embed=discord.Embed(title=f"День {Number_Night}", description="Ви впевнені?", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlDay),
                    view=self.GetView([Button(style=ButtonStyle.green,label="Так", custom_id="Так"), Button(style=ButtonStyle.red,label="Ні", custom_id="Ні")]))
                resp1 = await self.client.wait_for("interaction", check=lambda i:i.channel == GameChannel and i.custom_id in ['Так', 'Ні'])
                try:
                    await resp1.response.send_message()
                except:
                    pass
                if resp1.custom_id == "Так":
                    await Message.edit(embed=discord.Embed(title=f"День {Number_Night}", description="Гаразд", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlDay), view=View())
                    break
                else:
                    continue
            Player = await guild.fetch_member(self.db.playerID)
            await Message.edit(embed=discord.Embed(title=f"День {Number_Night}", description=f"{Player.mention} був(ла): {self.db.GetSqlite(f'SELECT status FROM Game WHERE user_id = {self.db.playerID}')[0][0]}", colour=discord.Color.blurple()).set_thumbnail(url=self.db.urlDay), view=View())
            if self.db.playerID != 0:
                self.db.remove_user(self.db.playerID)
                self.db.playerID = 0
            await Player.remove_roles(role)
            await asyncio.sleep(5)
            if not bool(len(self.db.GetSqlite("SELECT user_id FROM Game WHERE status = 'Мафія'"))):
                await Message.edit(embed=discord.Embed(title="Гра закінчена", description=f"Гра закінчина, всі мафії були зловленні !", colour=discord.Color.blurple()), view=View())
                break
            elif not bool(len(self.db.GetSqlite("SELECT user_id FROM Game WHERE status = 'Мирний житель'"))):
                await Message.edit(embed=discord.Embed(title="Гра закінчена", description=f"Гра закінчина, більше не залишелось мирних жителів !", colour=discord.Color.blurple()), view=View())
                break

        self.db.isStarted = False
        self.db.readyPeople = 0
        await asyncio.sleep(10)
        role = get(guild.roles, id=951419192781996043)
        for uid in self.db.GetSqlite("SELECT user_id FROM Game"):
            Player = await guild.fetch_member(uid[0])
            await Player.remove_roles(role)
        self.db.GetSqlite("DELETE FROM Game")
        await GameChannel.purge()
        self.db.GameMessage = await GameChannel.send(embed=discord.Embed(title="Готові?", description="Натисніть **Готовий** якщо ви готові до гри\n*гра почнеться тільки після того як всі учасники будуть готові*", colour=discord.Color.greyple()),
            view=self.GetView([Button(style=ButtonStyle.green,label="Готовий")])
            )

    async def StartTruthOrDare(self, interaction : discord.InteractionResponse):
        await interaction.response.send_message(
            embed=discord.Embed(title="Truth Or Dare", description="Are you ready?", colour=discord.Color.green()),
            view=self.GetView([Button(style=ButtonStyle.blurple, label="Start", custom_id="start_truth_or_dare")])
        )
        try:
            resp = await self.client.wait_for("interaction", check=lambda i:i.data["custom_id"] == "start_truth_or_dare" and interaction.user.id == i.user.id and i.type == discord.InteractionType.component and i.data.get("type") == 2, timeout=600)
        except asyncio.TimeoutError:
            await interaction.response.edit_message(embed=discord.Embed(title="Truth Or Dare", description="timeout", colour=discord.Color.red()))
            await asyncio.sleep(5)
            await interaction.message.delete()

        await resp.response.edit_message(
            embed=discord.Embed(title="Truth Or Dare", description="Select your language", colour=discord.Color.green()),
            view=self.GetView([
                Select(placeholder="language",options=[
                    SelectOption(label="ENG", value="language_ENG", emoji="🇬🇧"),
                    SelectOption(label="UA", value="language_UA", emoji="🇺🇦")
                ])
            ])
            )
        resp1 = await self.client.wait_for("interaction", check=lambda i:"language_" in i.data.get("values")[0] and interaction.user.id == i.user.id and i.type == discord.InteractionType.component and i.data.get("type") == 3, timeout=600)
        language = resp1.data.get("values")[0].split("_")
        if language[1] == "UA":
            embed = discord.Embed(title="Правда чи дія", colour=discord.Color.green())
            await resp1.response.edit_message(embed=embed,
            view=self.GetView([
                Button(style=ButtonStyle.blurple, label="Правда", custom_id="TruthOrDare_Truth Question_UA"),
                Button(style=ButtonStyle.blurple, label="Дія", custom_id="TruthOrDare_Dare Tasks_UA"),
                Button(style=ButtonStyle.red, label="Вийти з гри", custom_id="ok")
                ])
            )

        else:
            embed = discord.Embed(title="Truth Or Dare", colour=discord.Color.green())
            await resp1.response.edit_message(embed=embed,
            view=self.GetView([
                Button(style=ButtonStyle.blurple, label="Truth", custom_id="TruthOrDare_Truth Question_ENG"),
                Button(style=ButtonStyle.blurple, label="Dare", custom_id="TruthOrDare_Dare Tasks_ENG"),
                Button(style=ButtonStyle.red, label="Exit game", custom_id="ok")
                ])
            )