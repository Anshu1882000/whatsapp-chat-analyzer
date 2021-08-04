import streamlit as st
import pandas as pd
import numpy as np
import util



with st.form(key='my_form'):
    chat_file = st.file_uploader(label='Upload your chats .txt file.')
    link = 'https://faq.whatsapp.com/android/chats/how-to-save-your-chat-history/?lang=en'
    st.write('Click here to know how to exort whatsapp chats.')
    st.markdown(link, unsafe_allow_html=True)
    submit_button = st.form_submit_button(label='Submit')

@st.cache
def load_data():
    if chat_file is not None:
        parsedData = [] # List to keep track of data so it can be used by a Pandas dataframe
        messageBuffer = [] # Buffer to capture intermediate output for multi-line messages
        date, time, author = None, None, None # Intermediate variables to keep track of the current message being processed
        for line in chat_file:
            line = line.decode("utf-8").strip() # Guarding against erroneous leading and trailing whitespaces
            if util.startsWithDateTime(line): # If a line starts with a Date Time pattern, then this indicates the beginning of a new message
                if len(messageBuffer) > 0: # Check if the message buffer contains characters from previous iterations
                    parsedData.append([date, time, author, ' '.join(messageBuffer)]) # Save the tokens from the previous message in parsedData
                messageBuffer.clear() # Clear the message buffer so that it can be used for the next message
                date, time, author, message = util.getDataPoint(line) # Identify and extract tokens from the line
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

    

    messages_df["24_Hour_Format"] = messages_df['Time'].apply(util.change_format)
    st.subheader("Day Activity (No of messages recieved every hour of the day)")
    st.bar_chart(messages_df["24_Hour_Format"].value_counts())


