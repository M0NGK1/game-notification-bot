import discord, requests, asyncio, json, re, datetime, copy, os
from bs4 import BeautifulSoup
app = discord.Client()

lol_data = lol_champions = lol_OPGGnotification = {}
logo_url = None
rune_emoji = {"마법": '🟣', "지배": '🔴', "영감": '🔵', "정밀": '🟡', "결의": '🟢'}
runepage_element_set = {"마법": [3, 3, 3, 3], "지배": [4, 3, 3, 4], "영감": [3, 3, 3, 3], "정밀": [4, 3, 3, 3],"결의": [3, 3, 3, 3]}
rank_emoji = {None: '❌', 'Iron': '⬛', 'Bronze': '🟫', 'Silver': '⬜', 'Gold': '🟨', 'Platinum': '🟩','Diamond': '🟦', 'Master': '🟪', 'Grandmaster': '🟥', 'Challenger': '👑'}
state_emoji = {'패배': '🟥', '승리': '🟦', '다시하기': '⬜'}
hdr = {'Accept-Language': 'ko_KR,en;q=0.8', 'User-Agent': ('Chrome/78.0.3904.70')}

async def add_rune_embed(embed, soup):
    nickname = soup.find_all(src=[re.compile("//opgg-static.akamaized.net/images/lol/perk/"),re.compile("//opgg-static.akamaized.net/images/lol/perkStyle/")], class_='tip')
    rune_count = line = 0
    page_check = True
    for rune in nickname:
        if rune.attrs.get('alt') is None:
            runename = rune.attrs.get('title').split('</b><br><span>')
            runename = runename[0].replace("<b style='color: #ffc659'>", "")
            emoji = rune_emoji[runename]
            line = rune_count = 0
            if page_check:
                page_line = runepage_element_set[runename]
                page_check = False
                runename = "**첫번째 룬 ("+runename+")**\n"
            else:
                page_line = copy.deepcopy(runepage_element_set[runename])
                del page_line[0]
                runename = "**두번째 룬 (" + runename + ")**\n"
                page_check = True
            if page_line[line] == 4:
                rune_text = '> '
            else:
                rune_text = '> ...'
            continue
        rune_count += 1
        if rune.attrs['src'].count('e_grayscale') == 0:
            rune_text = rune_text + emoji + " "
        else:
            rune_text = rune_text + "⚪" + " "
        if (rune_count == page_line[line]):
            if len(page_line) != line + 1:
                line += 1
            else:
                embed.add_field(name="-", value=runename+rune_text, inline=True)
                if page_check is True:
                    break
            rune_count = 0
            rune_text = rune_text + "\n> "

            if page_line[line] != 4:
                rune_text = rune_text+'...'
    return embed
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
                html = requests.get(url, headers=hdr).text
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
        html = requests.get(url, headers=hdr).text
        soup = BeautifulSoup(html, 'html.parser')
        url_list = soup.find_all(src=re.compile("https://attach.s.op.gg/logo/"))
        logo_url = url_list[0].attrs["src"]
        await asyncio.sleep(60)

@app.event
async def on_ready():
    game=discord.Game(name="실시간 게임 알림 봇")
    await app.change_presence(status=discord.Status.online, activity=game)
    url = "http://ddragon.leagueoflegends.com/cdn/10.7.1/data/ko_KR/champion.json"
    data = requests.get(url, headers=hdr).text
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
                html = requests.get(url, headers=hdr).text
                soup = BeautifulSoup(html, 'html.parser')
                url_list = soup.find_all(src=re.compile("opgg-static.akamaized.net/images/lol/champion/"))
                icon_url = "https:" + url_list[0].attrs["src"]
                embed = discord.Embed(description="챔피언 " + chm + "의 추천 빌드를 확인하시려면 위의 OP.GG 확인하기를 눌러 주세요!",color=0x0080ff)
                embed.set_author(name=chm + " 추천 빌드 OP.GG에서 확인하기", url=url, icon_url=icon_url)
                embed.set_thumbnail(url=logo_url)
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(text="Game Notification For Gamer")
                embed = await add_rune_embed(embed, soup)
                await message.channel.send(embed=embed)
            else:
                url = 'https://www.op.gg/summoner/userName=' + chm
                html = requests.get(url, headers=hdr).text
                soup = BeautifulSoup(html, 'html.parser')
                SummonerName = soup.select('div[class=Information] > span[class=Name]')
                if SummonerName != []:
                    profile_link = "https:"+soup.find(src=re.compile("//opgg-static.akamaized.net/images/profile_icons/")).attrs["src"]
                    SummonerName =SummonerName[0].text
                    solorank_info = soup.select("div[class=TierRank]")
                    freerank_info = soup.select("div[class=sub-tier__rank-tier]")

                    if len(solorank_info):
                        solorank_info = solorank_info[0].text.strip()
                        sololp = "_(" + soup.select('span[class=LeaguePoints]')[0].text.strip().replace(" ", "") + ")_"
                        if solorank_info.count(" "):
                            solorank = solorank_info.split(" ")[0]
                        else:
                            solorank = solorank_info
                    else:
                        solorank = None
                        solorank_info = "Unranked"
                        sololp = ""
                    if len(freerank_info):
                        freerank_info = freerank_info[0].text.strip()
                        freelp = "_(" + \
                                 soup.select('div[class=sub-tier__league-point]')[0].text.strip().replace(" ", "").split(
                                     "/")[0] + ")_"
                        if freerank_info.count(" "):
                            freerank = freerank_info.split(" ")[0]
                        else:
                            freerank = freerank_info
                    else:
                        freerank = None
                        freerank_info = "Unranked"
                        freelp = ""
                    GameResult = []
                    KDA = []
                    Champion = []
                    GameType = []
                    for result in soup.find_all(class_="GameType"):
                        GameType.append(result.text.strip())
                    for result in soup.find_all(class_="GameResult"):
                        GameResult.append(result.text.strip())
                    for result in soup.select("div[class=GameItemList] div[class=KDA] div[class=KDA]"):
                        KDA.append(result.text.replace("\n", "").replace("\t", ""))
                    for result in soup.select("div[class=GameItemList] div[class=ChampionName] a"):
                        Champion.append(result.text.strip())
                    embed = discord.Embed(description=SummonerName+"님의 전적을 OP.GG에서 검색하였습니다. 더 자세한 정보를 원하신다면 위의 "+SummonerName+"님의 전적을 눌러 확인하여 주세요!",color=0x0080ff)
                    embed.set_author(name=SummonerName+"님의 전적",icon_url=profile_link, url=url)
                    embed.add_field(name="-", value="솔로 랭크 _(SoloRank)_\n"+rank_emoji[solorank]+ " **" + solorank_info + "**" + sololp, inline=True)
                    embed.add_field(name="-", value="자유 랭크 _(FreeRank)_\n" + rank_emoji[freerank] + " **" + freerank_info + "**" + freelp, inline=True)
                    if len(GameResult) < 5:
                        max = len(GameResult)
                    else:
                        max = 5
                    text = "⚔ **최근 진행한 경기 전적**("+str(max)+")"
                    if max == 0:
                        text = text+"\n_최근 진행한 경기가 없습니다._"
                    else:
                        for i in range(max):
                            text = text+"\n"+state_emoji[GameResult[i]] +" "+ GameType[i] + " | " + Champion[i]+" "+ KDA[i].replace(" ", "")
                    embed.add_field(name="-",value=text,inline=False)
                    embed.set_thumbnail(url=logo_url)
                    embed.timestamp = datetime.datetime.utcnow()
                    embed.set_footer(text="Game Notification For Gamer")
                    await message.channel.send(embed=embed)
                else:
                    embed = discord.Embed(title="존재하지 않는 챔피언 혹은 소환사의 이름입니다.",description="입력하신 이름을 확인 후 명령어를 재입력하여 주세요.",color=0xff8080)
                    embed.set_thumbnail(url=logo_url)
                    await message.channel.send(embed=embed)

access_token = os.environ["BOT_TOKEN"]
app.run(access_token)
