'''
- Author SvgFox
- Version 1.0
- Future plans: allow for sorting of saved data, add more error checking, add wpm average, store more data in txt file
'''

from os import path



'''
Flow of the code, controller
'''
def main():
	
	if (path.isfile("SongData.txt")): 															# If txt file is found...
		print("Pre-existing storage file found.\n") 											# ...do nothing
	else:
		song_data = open("SongData.txt", "w") 													# Create the txt file
		print("Storage file created.\n")
		song_data.close() 																		# Close until further use

	running = True																				# Keeps the program looping

	while running:

		options = ["HELP", "H", "INFO", "NEW ENTRY", "N", "VIEW ALL", "V", "QUIT", "Q", "W"]	# Hidden list of options
		options_display = ["NEW ENTRY (N)", "VIEW ALL (V)", "QUIT (Q)\n"]						# Visible list of options
	
		user_in = str(input("What would you like to do?\n'H' for list of options: ")).upper() 	# Grab input and convert to uppercase

		if (user_in not in options):															# Invalid input
			print("Not a valid option. Type 'H' for help.")
		elif (user_in == "HELP" or user_in == "H" or user_in == "INFO"):
			for x in options_display:
				print(">> " + x)
		elif (user_in == "NEW ENTRY" or user_in == "N"):
			song_name = str(input("Song name: "))
			artist_name = str(input("Artist name: "))
			song_lyrics = str(input("Copy and paste the lyrics here: ")).upper() 				# Uppercase for consistency 
			if (song_name != "" and artist_name != "" and len(song_lyrics) > 2): 				# Check for valid info entered
				count(song_lyrics, song_name, artist_name)
			else:
				print("\nEnter valid information.\n")
		elif (user_in == "VIEW ALL" or user_in == "V"):
			print_out()
		elif (user_in == "W"):
			song_data = open("SongData.txt", "w+") 												# Erase everything inside of the txt file
			song_data.close()
			print("File data erased.\n")
		else:
			print("Ending the program.")														# Q to quit
			running = False
	


'''
Counts up the words and stores stats in a given file
'''
def count(lyrics, song, artist):
	
	lyric_list = make_list(lyrics) 								# Get the list of words
	word_count = [] 											# Keep track of the occurrence of each word [word, #, word, #, ...]
	
	x = 0
	while (x < len(lyric_list)):
		if (lyric_list[x].upper() not in word_count.upper()):
			word_count.append(lyric_list[x]) 					# Add new word to list
			word_count.append(1) 								# One instance of the word found to the right
		else:
			y = 0
			while (y < len(word_count)):
				if (lyric_list[x].upper() == word_count[y].upper()):
					word_count[y + 1] += 1
					break
					#y = len(word_count) # Break out of the inner loop
				y += 2 											# Don't have to iterate through the numbers, only words
		x += 1

	total_words = str(len(lyric_list))
	unique_words = str(int(len(word_count) / 2))
	un_percentage = str(int((len(word_count) / 2) / len(lyric_list) * 100)) + "%"

	print("\nTotal number of words: " + total_words)
	print("Number of unique words: " + unique_words)
	print("Uniqueness percentage: " + un_percentage) 			# Unique words / total words
	print("Most common word(s): " + most_common(word_count) + "\n")

	song_data = open("SongData.txt", "a")
	song_data.write(artist + " - " + song + "\nNumber of words: " + str(len(lyric_list)) + " -- Uniqueness percentage: " + un_percentage + "\nMost common word(s): " + most_common(word_count) + "\n------------------------------------\n")
	song_data.close()



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
Create a list of words out of a list of single letters
'''
def make_list(lyrics):
	
	lyric_list = [] 															# Primary list, filled with single letters
	lyric_list_f = [] 															# Final list, filled with complete words
	end_word = [" ", ".", "!", "?", ":", ";", ",", "\n"] 						# DO NOT ADD APOSTROPHES TO THIS LIST, IDIOT. May need to remove "\n"

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
Print out the contents of the txt file
'''
def print_out():
	song_data = open("SongData.txt", "r")
	print("")
	for elem in song_data:
		print(elem)
	song_data.close()



# RUN
main()
