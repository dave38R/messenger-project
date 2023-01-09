# messenger-project
This is a repository dedicated to the analysis of messenger conversations, such as number of messages per person, use percentage of certain words or phrases etc...

# The different files :

## data_cleaning.py :
You should run the function save_participants_and_messages(folder_of_original_data) and it should create a new folder with 'cleaner' data because it will contain a participants folder and as many messages folder as you had in your original one.

## functions.py :
In this file, we define a class Chat which contains the participants of the chat in its attribute .participants and the messages (in the form of a pandas dataframe) in .messages. We defined a few methods usually consisting of show_something and it usually shows a matplotlib graph that we got using functions defined above, indeed methods usually use functions defined above the class. 

## sandbox.ipynb
This is the file in which we explore and organize the results. Whenever you add something to this file, try explaining what it does in a markdown cell above.

## dataframes.py
This file is bound to disappear, it was useful to me when I was engineering the data but not anymore. I would like to change to to test.py and start defining tests. 

# The different folders :
As of now we only have 2 conversations and this folder contains all the data from one of them. If you delete or modify files in one of these folders we can always get it back thanks to the ORIGINAL_DATA one.
## ORIGINAL_DATA
Do NOT touch this file, this is where all the original data is, we can reconstruct everything from this. 

## PTP
This file is the biggest one and it gets data from the longest period. It is a file of 5 people. 

## ZOO 
This is a conversation of 11 people over 2 years.