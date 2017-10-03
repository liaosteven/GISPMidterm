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
		for i in range(startyr, endyr+1):
			print(i)
			sys.stdout.flush() # make sure number is printed out in real time
			season_url = pre_url +str(i)+post_url
			seasonScrape(season_url, wr)

def seasonScrape(season_url, wr):
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

		### COMMENTED OUT PORTION - Allows us to scrape data from certain weeks onwards ###
		
		# # date_team is of format "198009080min.html"
		# date_team = remaining_link.split("/")[2]
		# date = int(date_team[0:9]) # 198009080

		# if date > 200110140:
		# full_link is now our full url
		full_link = link_start+remaining_link
		return_list = boxScore(full_link)
		wr.writerow(return_list)
	
	soup.decompose()

def boxscore():

	# test 