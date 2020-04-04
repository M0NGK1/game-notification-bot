import discord, requests, asyncio, json, re, datetime
from bs4 import BeautifulSoup
app = discord.Client()

lol_data = lol_champions = lol_OPGGnotification = {}
logo_url = None

async def league_of_legends_info():
    await app.wait_until_ready()
    global lol_OPGGnotification, lol_champions, logo_url
    while not app.is_closed():
        members = app.get_guild(695647949430063162).members
        for m in members:
            if m.bot or m.status == discord.Status.offline or m.activity == None or m.activity.large_image_text == None:
                continue
            if m.activity.name == "League of Legends" and m.activity.state == "게임 중":
                if m.id in lol_OPGGnotification and lol_OPGGnotification[m.id] == m.activity.timestamps.get("start"):
                    continue
                lol_OPGGnotification[m.id] = m.activity.timestamps.get("start")
                chm = m.activity.large_image_text.replace(" ","")
                url = "https://www.op.gg/champion/" + lol_champions[chm] + "/statistics/"
                html = requests.get(url).text
                soup = BeautifulSoup(html, 'html.parser')
                url_list = soup.find_all(src=re.compile("opgg-static.akamaized.net/images/lol/champion/"))
                icon_url = "https:"+url_list[0].attrs["src"]
                embed = discord.Embed(description=m.name+"님께서 현재 게임에서 플레이 중인 챔피언 "+m.activity.large_image_text+"의 추천 빌드를 확인하시려면 위의 OP.GG 확인하기를 눌러 주세요!",color=0x0080ff)
                embed.set_author(name=m.activity.large_image_text+"의 추천 빌드 OP.GG에서 확인하기",url=url, icon_url = icon_url)
                embed.set_thumbnail(url=logo_url)
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(text="Game Notification For Gamer")
                await m.send(embed=embed)

                print(m.name+"님께서 리그 오브 레전드를 시작하였습니다. 챔피언("+chm+")")
        await asyncio.sleep(1)

async def get_datas():
    await app.wait_until_ready()
    global logo_url
    while not app.is_closed():
        url = 'https://op.gg'
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        url_list = soup.find_all(src=re.compile("https://attach.s.op.gg/logo/"))
        logo_url = url_list[0].attrs["src"]
        await asyncio.sleep(60)

@app.event
async def on_ready():
    game=discord.Game(name="실시간 게임 알림 봇")
    await app.change_presence(status=discord.Status.online, activity=game)
    url = "http://ddragon.leagueoflegends.com/cdn/10.7.1/data/ko_KR/champion.json"
    data = requests.get(url).text
    global lol_champions, lol_data
    lol_data = json.loads(data)
    for chm in lol_data.get("data"):
        lol_champions[lol_data.get("data").get(chm).get("name").replace(' ','')] = chm
    print("롤 챔피언 데이터를 불러 왔습니다.")
    app.loop.create_task(get_datas())
    app.loop.create_task(league_of_legends_info())
@app.event
async def on_message(message):
    if message.author.bot:
        return None
    if message.channel.name == "명령어":
        if message.content.lower().startswith("!op.gg"):
            args = message.content.lower().split("!op.gg")
            chm = args[1].replace(" ", "")
            if chm == "":
                await message.channel.send("챔피언 이름을 입력하여 주세요. ex) !OP.GG 트위스티드 페이트")
                return
            global lol_champions
            url = "존재하지 않는 챔피언 이름입니다."
            if chm in lol_champions:
                m = message.author
                url = "https://www.op.gg/champion/" + lol_champions[chm] + "/statistics/"
                html = requests.get(url).text
                soup = BeautifulSoup(html, 'html.parser')
                url_list = soup.find_all(src=re.compile("opgg-static.akamaized.net/images/lol/champion/"))
                icon_url = "https:" + url_list[0].attrs["src"]
                embed = discord.Embed(description="챔피언 " + chm + "의 추천 빌드를 확인하시려면 위의 OP.GG 확인하기를 눌러 주세요!",color=0x0080ff)
                embed.set_author(name=chm + " 추천 빌드 OP.GG에서 확인하기", url=url, icon_url=icon_url)
                embed.set_thumbnail(url=logo_url)
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(text="Game Notification For Gamer")
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="존재하지 않는 챔피언의 이름입니다.",description="입력하신 챔피언 이름을 확인 후 명령어를 재입력하여 주세요.",color=0xff8080)
                embed.set_thumbnail(url=logo_url)
                await message.channel.send(embed=embed)

app.run("Njk1Njk3MTkyNDY3NDMxNDU0.Xod81w.xgNlfal6moLUv3RUQef-L_ziHig")