# messenger-project
This is a repository dedicated to the analysis of messenger conversations, such as number of messages per person, use percentage of certain words or phrases etc...

The different steps to use it are :
- download your conversation data from facebook (I won't go into details on how to do it here) 
- you should end up having many different folders corresponding to your different conversations, put the ones you would like to analyze in a folder called original_data
- rename those folders conversationname_original
- in the same folder as original_data, download the different python files from this repo (I haven't made a requirements.txt yet so don't forget to download the different tools like python, matplotlib, pandas etc...)
- adjust the data_cleaning.py file, and run it once (a few new folders should appear)
- I advise you to create a jupyter notebook, to import Chat from functions and have fun testing all the different methods of the class ! 

# The different files :

## data_cleaning.py :
You should run the function save_participants_and_messages(folder_of_original_data) and it should create a new folder with 'cleaner' data because it will contain a participants folder and as many messages folder as you had in your original one.

## functions.py :
In this file, we define a class Chat which contains the participants of the chat in its attribute .participants and the messages (in the form of a pandas dataframe) in .messages. We defined a few methods usually consisting of show_something and it usually shows a matplotlib graph that we got using functions defined above, indeed methods usually use functions defined above the class. 
