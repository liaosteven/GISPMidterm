from urllib.request import urlopen
from bs4 import BeautifulSoup
import scrape_functions
import csv
import sys 

def allSeasonsScrape(csv_file, startyr, endyr):
	""" Does a seasonScrape for all years from startyr to endyr (inclusive).
	Takes in a csv file where the data wlil be stored """
	pre_url = "http://www.pro-football-reference.com/years/"
	post_url = "/games.htm"

	with open(csv_file, "a", newline="") as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow(['year', 'awayteam', 'away carries', 'away yards', 'away tds','hometeam', 'home carries', 'home yards', 'home tds', 'field'])
		for i in range(startyr, endyr+1):
			print(i)
			sys.stdout.flush() # make sure number is printed out in real time
			season_url = pre_url +str(i)+post_url
			seasonScrape(season_url, wr, i)

def seasonScrape(season_url, wr, year):
	""" Takes in a URL to a weekly schedule of an entire NFL season in 
	Pro-football-reference. Goes through all the boxscores for every game, and writes them to a CSV 
	file. WR is the csv.writer that is connected to the file"""

	html = urlopen(season_url)
	soup = BeautifulSoup(html, "lxml")

	# boxscores is a list of a tags of form:
	# <a href="/boxscores/198009070min.html">boxscore</a>
	boxscores = soup.find_all("a", string = "boxscore")
	link_start = "http://www.pro-football-reference.com"
	for bs in boxscores:
		remaining_link = bs.get('href')
		away_team = bs.parent.prev_sibling

		### COMMENTED OUT PORTION - Allows us to scrape data from certain weeks onwards ###
		
		# # date_team is of format "198009080min.html"
		# date_team = remaining_link.split("/")[2]
		# date = int(date_team[0:9]) # 198009080

		# if date > 200110140:
		# full_link is now our full url
		full_link = link_start+remaining_link
		return_list = boxScore(full_link, year, hometeam, awayteam)
		wr.writerow(return_list)
	
	soup.decompose()

def boxScore(full_link, year, hometeam, awayteam):

	output = [year]
        page = urlopen(full_link)
        subSoup = BeautifulSoup(page)
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
        # find strings of grass
        ifGrass = subSoup.find('grass')
        # if there are any strings, the fieldType is grass, otherwise, it's turf
        if not ifGrass==null:
                fieldType = grass
        else:
                fieldType = turf
        # add field type to output list
        output = output + [fieldType] 
        return output 
        
        
        


	
