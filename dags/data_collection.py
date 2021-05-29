from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import time
import datetime
import os
import re






# Make use of the class data structure to store the incoming data in an easily retrievable format.

class Player():
    def __init__(self):
        self.link = ''
        self.team_link = ''
        self.name = ''
        self.team = ''
        self.number = ''
        self.position = ''
        self.height = ''
        self.weight = ''
        self.last_attended = ''
        self.country = ''
        self.age = ''
        self.birth_date = ''
        self.experience = ''
        self.draft = ''
        self.ppg = ''
        self.rpg = ''
        self.apg = ''
        self.pie = ''


# Function to gather preliminary data from the players page and form the list of player objects
def get_players_list(driver_path):
    
    players_list = []
    
    site = 'https://www.nba.com/players'
    web = 'https://www.nba.com'

    position_dict = {'F': 'Foward', 'G': 'Guard', 'C': 'Center', 'C-F': 'Center-Forward', 'G-F': 'Guard-Forward', 'F-G': 'Foward-Guard', 'F-C': 'Foward-Center'}

    
    # Download html page (if you are working on your local machine)
    # set up driver

    chrome_options = Options()
    # Required parameters
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--no-gpu')
    chrome_options.add_argument('--disable-setuid-sandbox')

    # chrome directory 
    #"/usr/bin/chrome-linux/chrome"
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path)



    #driver = webdriver.Chrome(executable_path=driver_path)
    driver.get(site)
    
    # Select all option to get access to the entire player list
    page = driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div[3]/section/div/div[2]/div[1]/div[7]/div/div[3]/div/label/div/select/option[1]')
    page.click()


    # create a soup object with the downloaded html page
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    # sind the section of the html that contains a player table with "All" the players name
    
    div = soup.find('div', class_='MockStatsTable_statsTable__2edDg')

    # get the players table
    table = div.find('table', class_='players-list')
    
    body = table.find('tbody')

    # identify each player
    for row in body.find_all('tr'):
        player = Player()

        # Get player link
        p_link = row.find('td')
        a = p_link.find('a') 
        player.link = web + a['href']
        
        # Get team link
        t_link = p_link.find_next_sibling()
        b = t_link.find('a')
        
        number_link = t_link.find_next_sibling()
        position = number_link.find_next_sibling()
        position_text = position.text
        
        try:
            player.team_link = web + b['href']
        except:
            player.team_link = 'N/A'
            player.team = 'N/A'
            player.number = 'N/A'
        
        player.position = position_dict[position_text]
        
        # add player to players list
        players_list.append(player)
    
    driver.quit()
           
    return players_list

def scraper(players_list, driver):
    count = 1
    
    # create a list to store the metadata for e
    metadata = []
    #metalist = []
    num_players  = len(players_list)
    
    
    
    for player in players_list:
        
        #identify objects yet to be updated
        if player.age == '':
        

            # identify the player link
            p_site = player.link
            print(f'{count} of {len(players_list)} players')

            # go the the link and download the html
            driver.get(url=p_site)

            # to resolve errors if the network connection is too slow
            time.sleep(2)

            # Create a soup object
            soup = BeautifulSoup(driver.page_source, 'lxml')

            # Get the section we are interested in to use as a reference
            try: #in case a player player's page is currently unavailable or being updated 
                section = soup.find('section', class_='relative overflow-hidden')
                section2 = soup.find('section', class_='relative text-white lg:px-20 PlayerSummary_statsSectionBG__G3Epx')
                # Get team name, position, player
                p_tag = section.find('p', class_='t11 md:t2')

            except:
                metadata.append(count)
                print('Unsuccessful\n')
                count +=1

            else:


                if p_tag:

                    text = p_tag.text.split('|')


                    try:
                        player.team, player.number, _ = text
                    except:
                        player.team = text[0]
                    else:
                        player.number = player.number[2:]
                        #player.position = player.position[1:]

                # Get player name
                n_text = section.find('p', class_='PlayerSummary_playerNameText__K7ZXO')
                name = n_text.text

                nex = n_text.find_next_sibling()
                player.name = name + ' ' + nex.text

                # Get the other attributes
                # height

                sec = section2.find('div', class_='flex')

                part = sec.find_all('div', class_='PlayerSummary_playerInfo__1L8sx')

                at1 = part[0].find('p', 'PlayerSummary_playerInfoValue__mSfou')
                car = at1.text
                pattern = '[0-9]\.[0-9]+'
                player.height = re.findall(pattern, car)[0]

                #weight


                at2 = part[1].find('p', 'PlayerSummary_playerInfoValue__mSfou')
                car2 = at2.text
                pattern2 = '[0-9]+'
                player.weight = re.findall(pattern2, car2)[1]

                # country


                at3 = part[2].find('p', 'PlayerSummary_playerInfoValue__mSfou')
                player.country = at3.text

                # last attended

                at4 = part[3].find('p', 'PlayerSummary_playerInfoValue__mSfou')
                player.last_attended = at4.text

                # Age

                sec2 = section2.find_all('p', 'PlayerSummary_playerInfoValue__mSfou')

                car5 = sec2[4].text
                pattern5 = '[0-9]+'
                player.age = re.findall(pattern5, car5)[0]

                # birth_date

                daate = sec2[5].text
                player.birth_date = datetime.datetime.strptime(daate, '%B %d, %Y').date()

                # draft

                player.draft = sec2[6].text

                # Experience

                car8 = sec2[7].text.split(' ')
                player.experience = car8[0]



                # Stats
                one = soup.find_all('div', class_='PlayerSummary_playerStat__lQ86Y')

                stats = []

                for x in one:
                    cast = x.find('p', class_= 'PlayerSummary_playerStatValue__3hvQY')
                    if cast.text == '--':
                        stats.append(0.0)
                    else:
                        stats.append(cast.text)

                if len(stats) == 4:    
                    player.ppg = float(stats[0])
                    player.rpg = float(stats[1])
                    player.apg = float(stats[2])
                    player.pie = float(stats[3])
                else:
                    player.ppg = 0.0
                    player.rpg = 0.0
                    player.apg = 0.0
                    player.pie = 0.0

                print(f'{count} done!\n')
                count += 1
    
#     for index in metadata:
#         metalist.append(players_list.pop(index-1)) # remove the player whose details couldn't be scraped from player list
    
    
    print(f'There are {num_players} players on the NBA website.')
    #print(f'We were unable to scrap {len(metalist)} players.')
    print(f'Players {metadata} details not scraped.')
    #print(f'{len(players_list)} players details scraped.')
    
    

    return players_list



def updated_players_list(driver_path):

    # Get the players list
    players_list = get_players_list(driver_path)
    
    chrome_options = Options()
    # Required parameters
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--no-gpu')
    chrome_options.add_argument('--disable-setuid-sandbox')

    # chrome directory 
    #"/usr/bin/chrome-linux/chrome"
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path)


    #driver = webdriver.Chrome(executable_path=driver_path)
    
    player_list = scraper(players_list, driver)
    
    

    # try rescraping the players in metalist who were not scraped if exists
    time.sleep(5)
    
    # for players whose scraping section was unsuccessful

    print('\nRetrying for 2 times for players with missing entries')
        
    new = scraper(player_list, driver)
    
    new2 = scraper(new, driver)
        
    
    driver.quit()
    
    updated_list = [x for x in new2 if x.age != '']
    return updated_list