import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver

def get_day_of_week(date_str):
    # Convert the string to a datetime object
    date_obj = datetime.strptime(date_str, '%B %d, %Y')
    # Get the day of the week
    day_of_week = date_obj.strftime('%A')
    return day_of_week

def convert_dates(date_str):
    # Parse the date string
    date_str = datetime.strptime(date_str, '%A, %B %d, %Y')
    # Convert to 'YYYY-MM-DD' format
    return date_str.strftime('%Y-%m-%d')


headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

url = 'https://www.baseball-reference.com/leagues/majors/2024-schedule.shtml'
response = requests.get(url,headers=headers)   

if response.status_code == 200:
  soup = BeautifulSoup(response.text, 'html.parser')
  links = soup.find_all('a')

  mlb_game_dates = []
  
  # Find all the divs containing the dates and game info
  game_divs = soup.find_all('div')
  
  for div in game_divs:
      # Find the date in the h3 tag
      date_tag = div.find('h3')
  
      if date_tag and date_tag.text.strip() not in mlb_game_dates:
          date = date_tag.text.strip()
          
          # Find all game paragraphs in the div
          game_paragraphs = div.find_all('p', class_='game')
          
          # Check if any game paragraph does not contain "Spring"
          has_mlb_game = False
          for game_paragraph in game_paragraphs:
              if "Spring" not in game_paragraph.text:
                  has_mlb_game = True
                  break
          
          # If there is at least one non-Spring game, add the date to the list
          if has_mlb_game:
              if date == "Today's Games":
                  date = 'Sunday, October 4, 2024'
                  mlb_game_dates.append(date)
                  break
              mlb_game_dates.append(date)
  

  # Convert the dates
  dotw = [elem.split(',')[0] for elem in mlb_game_dates]
  days = [convert_dates(elem) for elem in mlb_game_dates]
  teams_last_opp = {}

  stats = {
        'Monday': 0,
        'Tuesday': 0,
        'Wednesday': 0,
        'Thursday': 0,
        'Friday': 0,
        'Saturday': 0,
        'Sunday': 0,
        'Monday_tot': 0,
        'Tuesday_tot': 0,
        'Wednesday_tot': 0,
        'Thursday_tot': 0,
        'Friday_tot': 0,
        'Saturday_tot': 0,
        'Sunday_tot': 0,
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 0,
        '1_tot': 0,
        '2_tot': 0,
        '3_tot': 0,
        '4_tot': 0
  }
  for i,day in enumerate(days):   
      url_day = 'https://www.rotowire.com/baseball/scoreboard.php?date=' + day
      print(url_day)
  
  
      response_day = requests.get(url_day,headers=headers)   
  
      if response.status_code == 200:
          soup_for_day = BeautifulSoup(response_day.text, 'html.parser')
          games = soup_for_day.find_all('div', class_="heading size-1 mb-0")
  
          for game in games:
              if game.find('a'):
  
                  #team_abbreviations = []
  
  
                  url = 'https://www.rotowire.com' + game.find('a').get('href')
  
                  # Set up the Chrome options
                  chrome_options = webdriver.ChromeOptions()
                  chrome_options.add_argument('--no-sandbox')
                  chrome_options.add_argument('--headless')
  
                  # Initialize the Chrome driver
                  driver = webdriver.Chrome(options=chrome_options) 
  
                  # Fetch the webpage
                  driver.get(url)
  
                  # Get the HTML content
                  html = driver.page_source
  
                  # Close the driver
                  driver.quit()
  
  
                  soup_for_game = BeautifulSoup(html, 'html.parser')
  
  
                  if soup_for_game.find('td',class_ ="align-l pad-0-10"):
  
                      away_team = soup_for_game.find('td',class_ ="align-l pad-0-10").text
                      home_team = soup_for_game.find('td',class_ ="pad-0-5 align-l").text
                      runs_each_inning = soup_for_game.find_all('td',class_ ="pad-0-10")
  
                      stats[f"{dotw[i]}_tot"] += 1
  
                      if away_team in teams_last_opp and home_team in teams_last_opp:
                          if teams_last_opp[away_team][0] == home_team and teams_last_opp[home_team][0] == away_team:
                              teams_last_opp[away_team][1] += 1
                              teams_last_opp[home_team][1] += 1
                          else:
                              teams_last_opp[away_team] = [home_team] + [1]
                              teams_last_opp[home_team] = [away_team] + [1]
                      else:
                          teams_last_opp[away_team] = [home_team] + [1]
                          teams_last_opp[home_team] = [away_team] + [1]
  
                      gots = teams_last_opp[home_team][1]
  
                      try:
                          stats[f'{gots}_tot'] += 1
                      except:
                          print(teams_last_opp[away_team],teams_last_opp[home_team],day)
  
  
                      if runs_each_inning:
                          runs_each_inning = [elem.text for elem in runs_each_inning]
                          away_team_runs = int(runs_each_inning[1])
                          home_team_runs = int(runs_each_inning[int((len(runs_each_inning)/2) + 1)])
  
                          if away_team_runs + home_team_runs == 0:
                              stats[dotw[i]] += 1
                              stats[f'{gots}'] += 1
                    
  print(stats)
