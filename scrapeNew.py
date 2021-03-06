from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
import sys
import time 
import re

def allSeasonsScrape(csv_file, startyr, endyr):
	""" Does a seasonScrape for all years from startyr to endyr (inclusive).
	Takes in a csv file where the data will be stored """
	
	start_time = time.time()

	pre_url = "http://www.pro-football-reference.com/years/"
	post_url = "/games.htm"

	with open(csv_file, "a", newline="") as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		wr.writerow(['year', 'awayteam', 'away carries', 'away yards', 'away tds','hometeam', 'home carries', 'home yards', 'home tds', 'fieldSpecific', 'field'])
		for i in range(startyr, endyr+1):
			print(i)
			sys.stdout.flush() # make sure number is printed out in real time
			season_url = pre_url +str(i)+post_url
			seasonScrape(season_url, wr, i)

	print("--- %s seconds ---" % (time.time() - start_time))


####COMMENTED OUT OLD SEASONSCRAPE DEF
#def seasonScrapeOld(season_url, wr, year):
#	""" Takes in a URL to a weekly schedule of an entire NFL season in 
#	Pro-football-reference. Goes through all the boxscores for every game, and writes them to a CSV 
#	file. WR is the csv.writer that is connected to the file"""

	#html = urlopen(season_url)
	#soup = BeautifulSoup(html, "lxml")

	# boxscores is a list of a tags of form:
	# <a href="/boxscores/198009070min.html">boxscore</a>
	#boxscores = soup.find_all("a", string = "boxscore")
	#link_start = "http://www.pro-football-reference.com"
	#for bs in boxscores:
	#	remaining_link = bs.get('href')
	#	away_team = bs.parent.prev_sibling

		### COMMENTED OUT PORTION - Allows us to scrape data from certain weeks onwards ###
		
		# # date_team is of format "198009080min.html"
		# date_team = remaining_link.split("/")[2]
		# date = int(date_team[0:9]) # 198009080

		# if date > 200110140:
		# full_link is now our full url
	#	full_link = link_start+remaining_link
	#	return_list = boxScore(full_link, year, hometeam, awayteam)
	#	wr.writerow(return_list)
	
#	soup.decompose()
##COMMENTED OUT OLD SEASONSCRAPE DEF


def seasonScrape(season_url, wr, year):
	""" Takes in a URL to a weekly schedule of an entire NFL season in 
	Pro-football-reference. Goes through all the boxscores for every game, and writes them to a CSV 
	file. WR is the csv.writer that is connected to the file"""


	html = urlopen(season_url)
	soup = BeautifulSoup(html, "html.parser")

	table = soup.find("tbody")
	table_rows = table.find_all("tr")

	""" Loop through each row in the table"""
	for row in table_rows:


		# If it's not a header row or something
		if not row.has_attr('class'):

			if row.find('td', {'data-stat':'game_date'}).string != "Playoffs":

				winner = row.find_all('td', {'data-stat':'winner'})[0].string
				loser = row.find_all('td', {'data-stat':'loser'})[0].string
				location = row.find_all('td', {'data-stat':'game_location'})[0].string
		
				bs = row.find_all('a', string = "boxscore")
				remaining_link = bs[0]['href']


				if location == "@":
					hometeam = loser
					awayteam = winner
							
				else:
					hometeam = winner     
					awayteam = loser
					

				link_start = "http://www.pro-football-reference.com"
				full_link = link_start+remaining_link
				return_list = boxScore(full_link, year, hometeam, awayteam)

				wr.writerow(return_list)

	# Always decompose the soup (if you make it, remember to decompose / discard it as a general rule)
	soup.decompose()




def boxScore(full_link, year, hometeam, awayteam):

	output = [year]
	page = urlopen(full_link)
	subSoup = BeautifulSoup(page, 'html.parser')
	commentFinder = subSoup.find(id = 'all_team_stats')
	# accessing the comment with the data about rushing
	comment = commentFinder.find(class_='placeholder').next_sibling.next_sibling
	# making a soup of the comment
	soupcomment = BeautifulSoup(comment)
	#add away team to output list
	output = output + [awayteam]
	# finding the away's attempts, yards, and TDs, and make a list of that
	awayTeamList = soupcomment.find(string='Rush-Yds-TDs').parent.next_sibling.string.split('-')
	# add list to output
	output = output + awayTeamList
	# do same thing for home team
	output = output + [hometeam]
	homeTeamList = soupcomment.find(string='Rush-Yds-TDs').parent.next_sibling.next_sibling.string.split('-')
	output = output + homeTeamList
	soupcomment.decompose()
	
	# find if field type is grass

	# Find the table with field type
	allGameInfo = subSoup.find(id = 'all_game_info')

	# The comment that is the actual code
	gameInfoComment= allGameInfo.find(class_ = "placeholder").next_sibling.next_sibling
	subSubSoup = BeautifulSoup(gameInfoComment)

	surface = subSubSoup.find(string = 'Surface').parent.next_sibling.text
	ifGrass = subSubSoup.find(string= re.compile('^grass'))
	# if there are any strings, the fieldType is grass, otherwise, it's turf
	if ifGrass:
		fieldType = 'grass'
	else:
		fieldType = 'turf'
	# add field type to output list
	output = output + [surface, fieldType] 
	subSubSoup.decompose()
	subSoup.decompose()

	return output 

allSeasonsScrape('run_stats_fixed.csv', 2015, 2016)