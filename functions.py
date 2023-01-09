import json
import os
import pandas as pd
import matplotlib.pyplot as plt

#This function lists all the files in the directory it's currently in and removes all directories that don't end in .json from the list
#output : list of strings
def get_json_files(folder='.') -> list[str]: # Does not apply in the test folder 
    list_file_name = [folder + '\\' + name for name in os.listdir(folder)]
    remove_list = []
    for name in list_file_name:
        if not name.endswith('.json'):
            remove_list.append(name)
    for name in remove_list:
        list_file_name.remove(name)
    return(list_file_name)

#This function loads in all the data from the json files into one pandas dataframe
def conc_pd_dataframes(list_file_name):
    list_pd_dataframe = []
    for file_name in list_file_name :
        if "messages" in file_name:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                list_pd_dataframe.append(pd.DataFrame(data))
    return pd.concat(list_pd_dataframe, ignore_index=False).reset_index(drop=True)

#This function drops the uninsteresting columns
def filter_to_keep(df, to_keep:list[str]=['sender_name', 'datetime', 'content']) -> list:
    return df[to_keep]

#This function is to convert the ms timestamp to a human readable date
# It isn't used anymore because we clean the data in the data_cleaning.py file 
def format_time(df):
    #Here we translate this data (ms) into an actual date and add the paris timezone
    df['date'] = pd.to_datetime(df['timestamp_ms'], unit='ms', utc=True)
    #Here we change the timezone to Paris
    df['date'] = df['date'].dt.tz_convert('Europe/Paris')
    #Here we format the date to a more readable format
    df['date'] = df['date'].dt.strftime('%d %B, %Y - %H:%M:%S')
    #Here we drop the timestamp_ms column
    df = df.drop('timestamp_ms', axis=1)
    return df

#This function does all of the three functions cited above 
def concat_filter_formatT(folder='.'):
    return filter_to_keep(conc_pd_dataframes(get_json_files(folder)))

#This function is used to get the list of all participants
def get_participants(folder='.'):
    file = "participants.json"
    with open(folder + "\\" + file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        df_part = pd.DataFrame(data)
    return df_part

#This function returns a 2-tuple containing the result of the two functions above 
def get_parti_msgs(folder='.'):
    return get_participants(folder), concat_filter_formatT(folder)

#This function returns a pandas Series with the names and the total number of messages
def count_messages_per_person(df):
    count = df['sender_name'].value_counts().sort_values()
    count_df = pd.DataFrame({"sender_name": count.index, "message_count": count.values})
    return count_df

#This function counts how many times each participant has used a word
def count_word_occurrences(df, wordlist):
    # Convert all strings in the "content" column to lowercase
    msgs = df.copy()
    msgs["content"] = msgs["content"].str.lower()
    # Create a new column that indicates whether or not each row contains a word from the given list
    words = '|'.join(wordlist)
    # words = re.escape(words)
    msgs["contains_word"] = msgs["content"].str.contains(words)
    # Group the dataframe by the "from" column and sum the number of occurrences for each participant
    word_counts = msgs.groupby("sender_name")["contains_word"].sum().reset_index()
    # Rename the "contains_word" column to "num_occurrences"
    word_counts = word_counts.rename(columns={"contains_word": "words_occurrences"})
    # Sort the dataframe by the number of occurrences in descending order
    word_counts = word_counts.sort_values("words_occurrences", ascending=False)
    return word_counts

# A function that returns the average message length per person
def average_message_length(df):
    # Create a new column that contains the length of each message
    msgs = df.copy()
    msgs["message_length"] = msgs["content"].str.split(' ').str.len()
    # Group the dataframe by the "from" column and compute the mean message length for each participant
    avg_msg_length = msgs.groupby("sender_name")["message_length"].mean().reset_index()
    # Rename the "message_length" column to "avg_message_length"
    avg_msg_length = avg_msg_length.rename(columns={"message_length": "avg_message_length"})
    # Sort the dataframe by the average message length in descending order
    avg_msg_length = avg_msg_length.sort_values("avg_message_length", ascending=True)
    return avg_msg_length

# A function that returns the most used words of the whole conversation
def get_most_used_phrases(df, num_words=10, remove_short_words=True, remove_these_words=[]):
    # split the words in the "content" column and create a new column called "count"
    msgs = df.copy()
    msgs["count"] = df["content"].str.lower()
    # count the number of occurrences of each word and sort the results in descending order
    word_counts = msgs["count"].value_counts().sort_values(ascending=False)
    # create a new dataframe with the results
    msgs = word_counts.to_frame()
    # reset the index
    msgs.index.name = "phrases"
    msgs.reset_index(inplace=True)
    msgs.reset_index(inplace=True, drop=True)

    # define a function that will remove messages containing certain words
    def remove_word(word, df):
        for i in range(len(df.phrases)):
            if word in df.phrases[i]:
                df = df.drop(i)
                # print('line', i, 'dropped')
        df = df.reset_index(drop=True)
        return df
    
    # remove messages containing certain words
    msgs = remove_word('call', msgs)
    msgs = remove_word('call.', msgs)
    msgs = remove_word('named', msgs)
    msgs = remove_word('ended.', msgs)
    msgs = remove_word('poll ', msgs)
    msgs = remove_word('attachment', msgs)

    # remove short words
    if remove_short_words:
        msgs = msgs[msgs.phrases.str.len() > 3]
        msgs = msgs.reset_index(drop=True)

    # remove words from the list
    for word in remove_these_words:
        msgs = remove_word(word, msgs)
    
    # adjust the index column and sort the results in descending order
    msgs.index += 1
    return msgs[:num_words].sort_values(by='count', ascending=True)


# A function that retuns the number of messages sent per day
def messages_per_day(df):
    # Create a new column that contains the date of each message
    msgs = df.copy()
    msgs["datetime"] = msgs["datetime"].str.split(" - ").str[0]
    # Group the dataframe by the "date" column and count the number of messages for each date
    msgs_per_day = msgs.groupby("datetime")["content"].count().reset_index()
    # Changing datetime ojects from string to datetime
    msgs_per_day["datetime"] = pd.to_datetime(msgs_per_day["datetime"], format="%d %B, %Y")
    # Rename the "content" column to "num_messages"
    msgs_per_day = msgs_per_day.rename(columns={"content": "num_messages"})
    # Sort the dataframe by the date in ascending order
    msgs_per_day = msgs_per_day.sort_values("datetime", ascending=True)
    return msgs_per_day

# A function that returns the number of messages sent per day per person
def messages_per_day_per_person(df):
    # Create a new column that contains the date of each message
    msgs = df.copy()
    msgs["datetime"] = msgs["datetime"].str.split(" - ").str[0]
    # Group the dataframe by the "date" and "from" columns and count the number of messages for each date and participant
    msgs_per_day_per_person = msgs.groupby(["datetime", "sender_name"])["content"].count().reset_index()
    # Changing datetime ojects from string to datetime
    msgs_per_day_per_person["datetime"] = pd.to_datetime(msgs_per_day_per_person["datetime"], format="%d %B, %Y")
    # Rename the "content" column to "num_messages"
    msgs_per_day_per_person = msgs_per_day_per_person.rename(columns={"content": "num_messages"})
    # Sort the dataframe by the date in ascending order
    msgs_per_day_per_person = msgs_per_day_per_person.sort_values("datetime", ascending=True)
    # Create a pivot table with the date as the index, the participants as the columns and the number of messages as the values
    pivoted = msgs_per_day_per_person.pivot_table(
        index="datetime", columns="sender_name", values="num_messages", fill_value=0)
    return pivoted

def messages_per_month(df):
    # Create a new column that contains the month of each message
    msgs = df.copy()
    msgs["datetime"] = msgs["datetime"].str.split(" - ").str[0]
    msgs["datetime"] = pd.to_datetime(msgs["datetime"], format="%d %B, %Y")
    # Create new columns that contains the year and month of each message
    msgs["year"] = msgs["datetime"].dt.year
    msgs["month"] = msgs["datetime"].dt.month
    # Drop the "datetime" column
    msgs = msgs.drop(["datetime"], axis=1)
    # Group the dataframe by the "month" column and count the number of messages for each month
    msgs = msgs.groupby(["year", "month"])["content"].count().reset_index()
    # Rename the "content" column to "num_messages"
    msgs = msgs.rename(columns={"content": "num_messages"})
    # Create a new column that contains the year and month in the format "YYYY-MM"
    msgs['date'] = msgs.apply(lambda x: str(x['year']) + '-' + str(x['month']), axis=1)
    # Drop the "year" and "month" columns
    msgs = msgs.drop(["year", "month"], axis=1)
    # Sort the dataframe by the month in ascending order
    msgs = msgs.sort_values(["date"], ascending=True)
    return msgs

# A function that returns the number of messages sent per month per person
def messages_per_month_per_person(df):
    # Create a new column that contains the month of each message
    msgs = df.copy()
    msgs["datetime"] = msgs["datetime"].str.split(" - ").str[0]
    msgs["datetime"] = pd.to_datetime(msgs["datetime"], format="%d %B, %Y")
    msgs["month"] = msgs["datetime"].dt.month
    msgs["year"] = msgs["datetime"].dt.year
    # Group the dataframe by the "month" and "from" columns and count the number of messages for each month and participant
    msgs_per_month_per_person = msgs.groupby(["year", "month", "sender_name"])["content"].count().reset_index()
    # Rename the "content" column to "num_messages"
    msgs_per_month_per_person = msgs_per_month_per_person.rename(columns={"content": "num_messages"})
    # Sort the dataframe by the month in ascending order
    msgs_per_month_per_person = msgs_per_month_per_person.sort_values(["year", "month"], ascending=True)
    # Create a pivot table with the month as the index, the participants as the columns and the number of messages as the values
    pivoted = msgs_per_month_per_person.pivot_table(
        index=["year", "month"], columns="sender_name", values="num_messages", fill_value=0)
    return pivoted

# This function is used to plot the bar chart
def print_barh(people, values, title='', percentage=False, fsize=(20, 10)):
    fig, ax = plt.subplots(figsize=fsize)
    rects = ax.barh(people, values, color='orange')
    ax.set_title(title)
    rounded_values = [round(value, 2) for value in values]
    if percentage == True:
        rounded_values = [str(value) + '%' for value in rounded_values]
    ax.bar_label(rects, rounded_values, padding=-50, color='white')
    plt.show()

# A function that plots a series of values against a series of dates 
def print_line(x, y, title='', xlabel='', ylabel='', fsize=(20, 10)):
    fig, ax = plt.subplots(fsize)
    ax.plot(x, y, color='orange')
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.show()


class Chat:
    def __init__(self, folder='.'):
        self.participants, self.messages = get_parti_msgs(folder)
        self.count = count_messages_per_person(self.messages)
    
    def show_count(self):
        print_barh(self.count.sender_name, self.count.message_count, 'Nombre de messages par personne')

    def show_word_count(self, wordlist, the_title=None):
        if the_title is None:
            the_title = 'Pourcentage de messages contenant les mots: {} par personne'.format(", ".join(wordlist))
        word_counts = count_word_occurrences(self.messages, wordlist)
        word_count_percentage = pd.merge(word_counts, self.count, on="sender_name")
        word_count_percentage["words_occurrence_percentage"] = word_count_percentage["words_occurrences"] / word_count_percentage["message_count"] * 100
        word_count_percentage = word_count_percentage.sort_values("words_occurrence_percentage", ascending=True)
        print_barh(word_count_percentage.sender_name, word_count_percentage.words_occurrence_percentage, the_title, percentage=True)
 
    def show_avg_msg_length(self):
        avg_msg_length = average_message_length(self.messages)
        print_barh(avg_msg_length.sender_name, avg_msg_length.avg_message_length, 'Longueur de message moyen par personne')
    
    def show_most_used_phrases(self, num_words=10, remove_short_words=True, remove_these_words=[]):
        most_used_phrases = get_most_used_phrases(self.messages, num_words, remove_short_words, remove_these_words)
        print_barh(most_used_phrases["phrases"], most_used_phrases["count"], 'Messages les plus envoyés')

    def show_msgs_per_day(self):
        msgs_per_day = messages_per_day(self.messages)
        msgs_per_day.plot(x="datetime", y="num_messages", kind="line", legend=False, color="orange", title="Messages per day", figsize=(20, 10))

    def show_msgs_per_day_per_person(self):
        msgs_per_day_per_person = messages_per_day_per_person(self.messages)
        msgs_per_day_per_person.plot(kind='line', subplots=True, figsize=(20, 10))
        plt.show()

    def show_msgs_per_month(self):
        msgs_per_month = messages_per_month(self.messages)
        msgs_per_month.plot(x="date", y="num_messages", kind="line", figsize=(20, 10), legend=False, color="orange", title="Messages per month")
        plt.show()

    def show_msgs_per_month_per_person(self):
        msgs_per_month = messages_per_month_per_person(self.messages)
        msgs_per_month.plot(kind='line', subplots=True, figsize=(20, 10))
        plt.show()


if __name__ == '__main__':
    zoo = Chat('.\zoo')
    ptp = Chat('.\ptp')
    zoo.show_msgs_per_month_per_person()
    # ptp.show_msgs_per_day_per_person()