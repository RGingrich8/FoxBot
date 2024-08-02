'''
- FBot.py
- Referenced: https://bigishdata.com/2016/09/27/getting-song-lyrics-from-geniuss-api-scraping/
'''


# Imports
import os, discord, requests
from dotenv import load_dotenv
#from rauth import OAuth2Service, OAuth2Session
from bs4 import BeautifulSoup
#from sanction import Client as SClient


# Initialize
load_dotenv()


# Constants
BOT_TOKEN = os.getenv('TOKEN')
GENI_ID = os.getenv('GENIUS_ID')
GENI_SECRET = os.getenv('GENIUS_SECRET')
GENI_CLIENT_ONLY = os.getenv('GENIUS_CLIENT')
GENI_BEARER = os.getenv('GENIUS_BEARER')
HEADERS = {'Authorization': 'Bearer ' + GENI_BEARER}
#BOT_MODS = os.getenv('BOT_MODS')  # Format: user#0000 - problem is that this grabs it as a string, also cannot import special characters
BOT_MODS = [""]
OPTIONS_GEN = ["FB Help - display a list of all commands", "FBQ [Mod Only] - kill the bot"]	# Hidden list of options
OPTIONS_SONG = ["FB View All - view all previously recorded song data", "FB New - enter new song data (Artist - Song)", "FBLN - enter new song data (Artist, Song, Lyrics - all on seperate lines)", "FBW [Mod Only] - wipe all recorded song data"]
OPTIONS_BDAY = ["No commands yet"]
OPTIONS_MOD = []



# Log into Discord
client = discord.Client()


# Confirm login
@client.event
async def on_ready():
	print("Logged in.")



# Catch messages sent by users
@client.event
async def on_message(message):

	user_inp = message.content.upper() # For consistency
	bot_out = message.channel
	user = str(message.author)

	# TURN THIS INTO A SWITCH STATEMENT
	if (message.author == client.user): # Stop bot from replying to itself
		return
	# Must be rebuilt because of the Discord API update. Make all changes HERE


'''
Converts the input
msg: the user's input
chan: the channel in which the user's input is grabbed from
'''
async def convert(msg, chan):
	y = 0
	x = 0
	curr_list = [] 	# Store letters thus far
	
	while (x < len(msg)):
		
		curr_list.append(msg[x])

		if (msg[x] == "\n"):
			y += 1
			if (y <= 1):
				curr_list = [] 			# Wipe current list being built up	
			elif (y == 2 and len(curr_list) > 0):
				artist = make_list(curr_list)
				artist_f = ""
				for elem in artist:
					artist_f += elem + " "
				curr_list = [] 			#Reset
			elif (y == 3 and len(curr_list) > 0):
				song = make_list(curr_list)
				song_f = ""
				for elem in song:
					song_f += elem + " "
				curr_list = [] # Reset
			#elif (y > 3):
			#	curr_list.append(" ")
	

		if (x == len(msg) - 1): 				# Hit end of the input
			if (y < 3 or len(curr_list) < 1): 	# Improper format received, lyrics missing, etc
				await chan.send("Improper format.")
			else:
				await get_song_info(chan, artist_f, song_f, curr_list) # Then print and store since it is all valid
		x += 1
		


async def get_song_info(chan, artist, song, lyrics):
	
	lyric_list = make_list(lyrics) 								# Get the list of words
	word_count = [] 											# Keep track of the occurrence of each word [word, #, word, #, ...]
	
	x = 0
	while (x < len(lyric_list)):
		if (lyric_list[x].upper() not in word_count):
			word_count.append(lyric_list[x].upper()) 			# Add new word to list
			word_count.append(1) 								# One instance of the word found to the right
		else:
			y = 0
			while (y < len(word_count)):
				if (lyric_list[x].upper() == word_count[y].upper()):
					word_count[y + 1] += 1
					break
				y += 2 											# Don't have to iterate through the numbers, only words
		x += 1

	total_words = str(len(lyric_list))
	unique_words = str(int(len(word_count) / 2))
	un_percentage = str(int((len(word_count) / 2) / len(lyric_list) * 100)) + "%"

	added = "**" + artist + " - " + song + "**"
	added += "\nTotal number of words: " + total_words
	added += "\nNumber of unique words: " + unique_words
	added += "\nUniqueness percentage: " + un_percentage
	added += "\nMost common word(s): " + most_common(word_count)
	#added += "\nMost interesting word: " + FIND LIST OF UNCOMMON WORDS

	await chan.send(added) # Print out info calculated

	song_data = open("SongData.txt", "a")
	song_data.write(artist + " - " + song + "\nNumber of words: " + str(len(lyric_list)) + " -- Uniqueness percentage: " + un_percentage + "\nMost common word(s): " + most_common(word_count) + "\n------------------------------------\n")
	song_data.close()


'''
Create a list of words out of a list of single letters
'''
def make_list(lyrics):
	
	lyric_list = [] 															# Primary list, filled with single letters
	lyric_list_f = [] 															# Final list, filled with complete words
	end_word = [" ", ".", "!", "?", ":", ";", ",", "(", ")", "[", "]", "\n"]	# DO NOT ADD APOSTROPHES TO THIS LIST. May need to remove "\n"

	for x in lyrics: 															# Add each letter of the input word into the initial list
		lyric_list.append(x)
	
	word = "" 																	# Used to build words
	x = 0 																		# Initial index

	while (x < len(lyric_list)):
		if (lyric_list[x] in end_word or (x == len(lyric_list) - 1)): 			# Either the end of a word was found, or the end of the list was hit
			if (x == len(lyric_list) - 1 and lyric_list[x] not in end_word): 	# Add very last letter
				word += lyric_list[x]
			if (len(word) >= 1): 												# Ensure no blanks are added to the list
				lyric_list_f.append(word) 										# If not an empty word, add it to list
			word = "" 															# Reset the word
		else:
			word += lyric_list[x] 												# Add onto the current word
		x += 1

	return lyric_list_f															# Return final list with seperated words


'''
Send all stored song data to the channel
chan: the channel in which it was requested
'''
async def print_out(chan):
	song_data = open("SongData.txt", "r")
	added = ""
	for x in song_data:
		added += x
	song_data.close()
	if (len(added) != 0):
		await chan.send(added)
	else:
		await chan.send("No data was found.")


'''
Finds the most common word in a list organized as [word, #occur, word2, #occur2, etc]
'''
def most_common(lst):
	
	highest = lst[1] 										# First number
	word = str(lst[0]) 										# First word
	x = 3 													# No need to start at the first number
	while (x < len(lst)):
		if (lst[x] > highest): 								# If higher number found
			word = str(lst[x - 1]) 							# Then the most common word is found
			highest = lst[x] 								# New highest value
		elif (lst[x] == highest):
			word = str(word) + ", " + str(lst[x - 1])
		x += 2
	return (word + " (" + str(highest) + " times)")




'''
Uses the Genius API to look for the song page
After finding the page, it uses a scraper to store the lyrics
'''
async def genius(chan, artist, song):
	search_url = 'https://genius.com' 
	#artist = artist.lower()
	#song = song.lower()
	#artist = input("Artist: ")
	#song = input("Song: ")
	vis_art = artist.replace(" ", "%20") # For visual purposes only
	vis_song = song.replace(" ", "%20") # For visual purposes only
	search_term = search_url + '/search?q=' + vis_art + '%20' + vis_song # Visual purposes only
	search_term	= search_term.replace("%20%20%20", "%20")

	print("\nCommencing search: " + search_term) # Visual purposes only
	await chan.send("Created link: <" + search_term + ">") # Send message to channel so user can see
	base_url = 'http://api.genius.com' 
	#headers = {'Authorization': 'Bearer ' + GENI_BEARER} # Authentication method recommended by Genius
	search_url = base_url + '/search' # Used to get a result from Genius
	params = {'q': song} 
	search_result = requests.get(search_url, params = params, headers = HEADERS)
	print("Genius Status Code: " + str(search_result.status_code) + "\n") # 200 = access granted


	# Check if the returned status code works
	if (search_result.status_code == 401):
		print("Error: Unauthorized") # Can possibly be fixed by resubmitting 
	elif (search_result.status_code == 403): 
		print("Error: Forbidden") # Server received everything properly, still wanted to deny access
	elif (search_result.status_code == 404):
		print("Error: Page Not Found")
	elif (search_result.status_code == 200): # Access granted
		json = search_result.json() # All results returned are JSON
		match_song = None # Song yet to be found
		for match in json["response"]["hits"]: # Iterate through the results and look for a match
			if match["result"]["primary_artist"]["name"].lower() == artist.lower(): # Found a match, make sure both are in the same case (upper/lower)
				match_song = match # Found the song, store it
				break # Found a match, stop the loop
		print(match_song)
		if match_song != None: # Match found, move onto next step
			song_image = match_song["result"]["song_art_image_thumbnail_url"]
			await chan.send(song_image) # Post the song's cover
			song_artist = match_song["result"]["primary_artist"]["name"] # Official name for storing later 
			song_title = match_song["result"]["title"] # Official title for storing later
			song_api_path = match_song["result"]["api_path"] # Find the api (/12345) path of the song
			#try:
			store_lyrics = await scrape_lyrics(base_url + song_api_path) # Save the lyrics as a variable after scraping
			return song_artist, song_title, store_lyrics # Return official artist name, song title, and full lyrics
			#except:
			#	await chan.send("Error: something went wrong.")
		else: # No match
			print("Failed to find a match.")
	return "", "", ""

'''
All credit to https://bigishdata.com/2016/09/27/getting-song-lyrics-from-geniuss-api-scraping/
Scrapes the webpage for the lyrics only
path: the API song path 
return: the lyrics in string format
'''
async def scrape_lyrics(path):
	print(path)
	response = requests.get(path, headers = HEADERS)
	json = response.json()
	scrape = json["response"]["song"]["path"]
	page_url = "https://genius.com" + scrape
	page = requests.get(page_url)
	html = BeautifulSoup(page.text, "html.parser")
	[h.extract() for h in html('script')] # Remove script tags
	lyrics = html.find("div", class_="lyrics").get_text() # Find the lyrics within the lyrics div
	return lyrics # Return the lyrics


async def new_entry(msg):
	x = 0 # Counter for while loop
	switch = 0 # 0 = add to artist, 1 = add to song
	artist = ""
	song = ""
	while x < len(msg):
		check = str(msg[x])
		if check == "-": # Switch over to song name
			switch = 1
		else:
			if (switch == 0):
				artist += check
			else:
				song += check
		x += 1 # Increase counter
	
	while artist[0] == " ":
		artist = artist[1:]
	while artist[-1] == " ":
		artist = artist[:-1]
	while song[0] == " ":
		song = song[1:]
	while song[-1] == " ":
		song = song[:-1]
	y = 0
	#try:
		#artist = artist[0].upper() + artist[1:].lower() # Capitalize starting letter
		#while y < len(artist): # Auto capitalizes every first letter of every word (artist)
		#	if (artist[y] == " "):
		#		artist = artist[:y + 1] + artist[y + 1].upper() + artist[y + 2:]
		#		print(artist)
		#	y += 1

	#	song = song[0].upper() + song[1:].lower()
	#except:
	#	print("Error: could not change the capitalization of the input")
	#finally:
	#	print(artist, song)
	return artist, song


client.run(BOT_TOKEN) # Ensure that this stays at the bottom