import re
import streamlit as st
import pandas as pd
import numpy as np



def startsWithDateTime(s):
    pattern = '^([0-2][0-9]|(3)[0-1])/(((0)[0-9])|((1)[0-2]))/(\d{2})'
    result = re.match(pattern, s)
    if result:
        return True
    return False

def startsWithAuthor(s):
    patterns = [
        '([\w]+):',                        # First Name
        '([\w]+[\s]+[\w]+):',              # First Name + Last Name
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',    # First Name + Middle Name + Last Name
        '([+]\d{2} \d{5} \d{5}):',         # Mobile Number (India)
        '([+]\d{2} \d{3} \d{3} \d{4}):',   # Mobile Number (US)
        '([+]\d{2} \d{4} \d{7})'           # Mobile Number (Europe)
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False

def getDataPoint(line):
    # line = 18/06/17, 22:47 - Loki: Why do you have 2 numbers, Banner?
    
    splitLine = line.split(' - ') # splitLine = ['18/06/17, 22:47', 'Loki: Why do you have 2 numbers, Banner?']
    
    dateTime = splitLine[0] # dateTime = '18/06/17, 22:47'
    
    date, time = dateTime.split(', ') # date = '18/06/17'; time = '22:47'
    
    message = ' '.join(splitLine[1:]) # message = 'Loki: Why do you have 2 numbers, Banner?'
    
    if startsWithAuthor(message): # True
        splitMessage = message.split(': ') # splitMessage = ['Loki', 'Why do you have 2 numbers, Banner?']
        author = splitMessage[0] # author = 'Loki'
        message = ' '.join(splitMessage[1:]) # message = 'Why do you have 2 numbers, Banner?'
    else:
        author = None
    return date, time, author, message

with st.form(key='my_form'):
    chat_file = st.file_uploader(label='Upload your chats .txt file')
    submit_button = st.form_submit_button(label='Submit')

@st.cache
def load_data():
    if chat_file is not None:
        parsedData = [] # List to keep track of data so it can be used by a Pandas dataframe
        messageBuffer = [] # Buffer to capture intermediate output for multi-line messages
        date, time, author = None, None, None # Intermediate variables to keep track of the current message being processed
        for line in chat_file:
            line = line.decode("utf-8").strip() # Guarding against erroneous leading and trailing whitespaces
            if startsWithDateTime(line): # If a line starts with a Date Time pattern, then this indicates the beginning of a new message
                if len(messageBuffer) > 0: # Check if the message buffer contains characters from previous iterations
                    parsedData.append([date, time, author, ' '.join(messageBuffer)]) # Save the tokens from the previous message in parsedData
                messageBuffer.clear() # Clear the message buffer so that it can be used for the next message
                date, time, author, message = getDataPoint(line) # Identify and extract tokens from the line
                messageBuffer.append(message) # Append message to buffer
            else:
                messageBuffer.append(line) # If a line doesn't start with a Date Time pattern, then it is part of a multi-line message. So, just append to buffer
        return parsedData
data = load_data()
if data:
    df = pd.DataFrame(data, columns=['Date', 'Time', 'Author', 'Message'])
    st.subheader("Total messages")
    st.write(len(df))

    author_value_counts = df['Author'].value_counts() # Number of messages per author
    top_10_author_value_counts = author_value_counts.head(10) # Number of messages per author for the top 10 most active authors
    st.subheader("No. of messages")
    st.bar_chart(top_10_author_value_counts)
    #top_10_author_value_counts.plot.barh() # Plot a bar chart using pandas built-in plotting apis

    media_messages_df = df[df['Message'] == '<Media omitted>']

    author_media_messages_value_counts = media_messages_df['Author'].value_counts()
    top_10_author_media_messages_value_counts = author_media_messages_value_counts.head(10)
    st.subheader("No. of media messages")
    st.write(len(media_messages_df))
    st.bar_chart(top_10_author_media_messages_value_counts)

    null_authors_df = df[df['Author'].isnull()]
    messages_df = df.drop(null_authors_df.index) # Drops all rows of the data frame containing messages from null authors
    messages_df = messages_df.drop(media_messages_df.index) # Drops all rows of the data frame containing media messages

    # adding letter and word count fields
    messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s : len(s))
    messages_df['Word_Count'] = messages_df['Message'].apply(lambda s : len(s.split(' ')))

    discrete_columns = ['Date', 'Time', 'Author', 'Message']
    messages_df[discrete_columns].describe()

    continuous_columns = ['Letter_Count', 'Word_Count']
    messages_df[continuous_columns].describe()

    total_word_count_grouped_by_author = messages_df[['Author', 'Word_Count']].groupby('Author').sum()
    sorted_total_word_count_grouped_by_author = total_word_count_grouped_by_author.sort_values('Word_Count', ascending=False)
    top_10_sorted_total_word_count_grouped_by_author = sorted_total_word_count_grouped_by_author.head(10)
    st.subheader("Word Count")
    st.bar_chart(top_10_sorted_total_word_count_grouped_by_author)

    def change_format(time):
        if time[1] == ':':
            time = '0' + time
        if time[-2:] == 'pm':
            if time[:2] == '12':
                return 12
            return int(time[:2]) + 12
        else:
            if time[:2] == '12':
                return 0 
            return int(time[:2])

    messages_df["24_Hour_Format"] = messages_df['Time'].apply(change_format)
    st.subheader("Day Activity")
    st.bar_chart(messages_df["24_Hour_Format"].value_counts())


