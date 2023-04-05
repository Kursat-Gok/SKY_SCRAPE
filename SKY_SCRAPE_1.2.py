#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 09:44:41 2023

@author: Kursat
"""

"""NOTE: Some Twitter accounts will have privacy settings that do not
        allow them to be scraped by open-source tools. In these cases,
        accounts may be very active but this program will not pick up any
        tweets from their profile, going through "20 empty pages" and then
        marking the account as "authentic." The other case is a KeyError: 'text'
        exception that will be raised. If the program comes up with either of these 
        situations then you need to visit the Twitter account
        manually and analyze the tweets the hard way. Do not assume the
        account is inactive. Accounts that are valued by information
        operation managers will likely have privacy and anti-scraping
        settings enabled. "20 empty pages" or KeyError: 'text' should be a 
        signal to investigate further."""

from tqdm import tqdm
import sys
import snscrape.modules.twitter as sntwitter
import datetime
import time
import mplcursors
from matplotlib.widgets import Cursor
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from datetime import timedelta, datetime
import re
import os
from collections import Counter
from textblob import TextBlob
import numpy as np
from matplotlib_venn import venn2, venn3
import networkx as nx
import warnings

# Main Functions

def execute_choice_1(username, num_tweets):
    
    df_tweets = scrape_recent_tweets_choice_1(username, num_tweets)
    
    print_recent_tweets(df_tweets, username, num_tweets)
    
    repeated_tweets = find_repeated_tweets(df_tweets)
    
    get_repeated_tweets_info(df_tweets, repeated_tweets)
    
    stats = compute_tweet_stats(df_tweets)
    
    print_tweet_stats(stats, num_tweets, username)
    
    evaluate_for_phishing_behavior(username, df_tweets)
    
    detect_spam_behavior(username, df_tweets)
    
    if evaluate_for_inauthentic_behavior(df_tweets, username) == True:
        
        return inauthentic_behavior(username, df_tweets)
    
    if evaluate_for_phishing_behavior(username, df_tweets) == True:
       
        return inauthentic_behavior(username, df_tweets)
    
    if detect_spam_behavior(username, df_tweets) == True:
        
        print("-" * 50)
        print(f"{username} is spamming messages within very short timeframes.")
        
        return inauthentic_behavior(username, df_tweets)
    
    else:
        
        return authentic_behavior(username, df_tweets)

def execute_choice_2(username, num_tweets):
    
    df = scrape_recent_tweets_choice_2(username, num_tweets)
   
    plot_weekly_activity(username, num_tweets)
   
    compute_and_print_tweet_stats_choice_2(df)

def execute_choice_3():
   
    print("-" * 50)
    
    hashtag = input("Enter a hashtag: ")
    
    account_usernames = get_related_accounts(hashtag)
    
    create_usernames_file(hashtag, account_usernames)

# Collection
def scrape_recent_tweets_choice_1(username, num_tweets):
    """
    Scrape the most recent num_tweets tweets for the specified username
    and return them as a pandas DataFrame.
    """
    query = f"from:{username} since_id:0"
    tweets = []
    for i, tweet in enumerate(tqdm(sntwitter.TwitterSearchScraper(query).get_items(), total=num_tweets)):
        if i >= num_tweets:
            break
        tweets.append({
            "text": tweet.content,
            "datetime": tweet.date.strftime("%Y-%m-%d %H:%M:%S")
        })
    df_tweets = pd.DataFrame(tweets)
    return df_tweets

def scrape_recent_tweets_choice_2(username, num_tweets):
    """
    Scrape the most recent num_tweets tweets for the specified username
    and return them as a pandas DataFrame.
    """
    tweets = []
    for i, tweet in enumerate(tqdm(sntwitter.TwitterSearchScraper(f"from:{username}").get_items(), total=num_tweets)):
        if i >= int(num_tweets):
            break
        tweets.append([tweet.date, tweet.content])
        
    df_tweets = pd.DataFrame(tweets, columns=['date', 'content'])
    return df_tweets

def get_top_hashtag(username, num_tweets):
    """
    Returns the top hashtag used by the given Twitter user in their most recent tweets.
    """
    df_tweets = scrape_recent_tweets_choice_1(username, num_tweets)
    hashtags = []
    for tweet in tqdm(df_tweets['text'], desc=f'Scraping {username}', total=num_tweets):
        hashtags_in_tweet = re.findall(r"#(\w+)", tweet)
        hashtags.extend(hashtags_in_tweet)
    top_hashtag = pd.Series(hashtags).value_counts().nlargest(1).index[0]
    return top_hashtag

def get_related_accounts(hashtag):
    # Search for other accounts that have tweeted using the hashtag
    search_query = f"#{hashtag}"
    account_usernames = set()
    for i, tweet in enumerate(tqdm(sntwitter.TwitterSearchScraper(search_query).get_items(), desc=f"Scraping tweets with #{hashtag}", unit=" tweet", position=0)):
        if i >= 100:
            break
        account_usernames.add(tweet.user.username)   
    # Print the account usernames
    print(f"Top unique accounts that have also tweeted #{hashtag}:")
    print("-" * 50)
    for i, v in enumerate(account_usernames):
        print(f"{i + 1}. {v}")
    return account_usernames

# Repetitive Tweet Analysis

def find_repeated_tweets(df_tweets):
    repeated_tweets_df = df_tweets[df_tweets.duplicated(subset=["text"], keep=False)]
    if repeated_tweets_df.empty:
        repeated_tweets = []
    else:
        repeated_tweets = repeated_tweets_df["text"].unique().tolist()
    return repeated_tweets

def get_repeated_tweets_info(df_tweets, repeated_tweets):
    repeated_tweets_info = {}
    for tweet_text in repeated_tweets:
        repeated_tweet_df = df_tweets[df_tweets['text'] == tweet_text]
        repeated_tweet_info = {
            'datetime_list': repeated_tweet_df['datetime'].tolist()
            }
        repeated_tweets_info[tweet_text] = repeated_tweet_info
        return repeated_tweets_info

def detect_spam_behavior(username, df_tweets):
    tweet_count = 0
    for i in range(len(df_tweets)-1):
        current_time = datetime.strptime(df_tweets.iloc[i]['datetime'], "%Y-%m-%d %H:%M:%S")
        next_time = datetime.strptime(df_tweets.iloc[i+1]['datetime'], "%Y-%m-%d %H:%M:%S")
        time_diff = next_time - current_time

        if abs(time_diff) <= timedelta(seconds=30):
            tweet_count += 1

            if tweet_count >= 5:
                return True
        else:
            tweet_count = 0

    return False

def evaluate_for_inauthentic_behavior(df_tweets, username):
    repeated_tweets = find_repeated_tweets(df_tweets)
    repeated_tweets_info = get_repeated_tweets_info(df_tweets, repeated_tweets)
    if len(repeated_tweets) > 0:
        print("-" * 50)
        print(f"Repeated tweets indicative of inauthentic behavior found in {username}'s tweets:")
        print(repeated_tweets)
        print(repeated_tweets_info)
        print("-" * 50)
        return True
    else:
        return False

def evaluate_for_phishing_behavior(username, df_tweets):
    if check_for_phishing_behavior(df_tweets, username, num_tweets) == True:
        return True
    else:
        return False

def authentic_behavior(username, df_tweets):
    print("-" * 50)
    print(f"{username} does not appear to be an inauthentic account.")
    print("-" * 50)
    # You can write more code here to export the username and its metadata to a file

def inauthentic_behavior(username, df_tweets):
    print("-" * 50)
    print(f"{username} is likely an inauthentic account.")
    print("-" * 50)
    # You can write more code here to export the username and its metadata to a file

# Analysis
def check_for_phishing_behavior(df: pd.DataFrame, username: str, num_tweets: int) -> str:
    url_count = sum(df['text'].str.contains('http') | df['text'].str.contains('t.co/'))
    percent_with_url = (url_count / len(df)) * 100
    
    if percent_with_url > 50:
        print("-" * 50)
        print(f"WARNING: Account is either a meme account or sending phishing links. More than half of {username}'s recent {num_tweets} tweets contain a link to an image or an external source.")
        print("-" * 50)
        return True
    return False

# Statistics
def compute_tweet_stats(df_tweets):
    df_tweets = scrape_recent_tweets_choice_1(username, num_tweets)
    stats = {}
    # Average length of tweets
    avg_tweet_len = df_tweets['text'].str.len().mean()
    stats['avg_tweet_len'] = avg_tweet_len

    # Percentage of tweets that mention other users
    mention_count = sum(df_tweets['text'].str.contains('@'))
    percent_with_mention = (mention_count / len(df_tweets)) * 100
    stats['percent_with_mention'] = percent_with_mention 
    
    # Percentage of tweets that contain hashtags
    hashtag_count = sum(df_tweets['text'].str.contains('#'))
    percent_with_hashtag = (hashtag_count / len(df_tweets)) * 100
    stats['percent_with_hashtag'] = percent_with_hashtag
    
    # Average number of retweets per tweet
    avg_retweets = df_tweets['text'].str.extract('([Rr][Tt])').count()[0] / len(df_tweets)
    stats['avg_retweets'] = avg_retweets
    
    # Get the hashtags for each tweet
    hashtags = []
    for tweet in df_tweets['text']:
        hashtags_in_tweet = re.findall(r"#(\w+)", tweet)
        hashtags.extend(hashtags_in_tweet)

    # Get the top 10 hashtags
    top_hashtags = pd.Series(hashtags).value_counts().nlargest(10)
    stats['top_hashtags'] = top_hashtags
    
    mentions1 = []
    for tweet in df_tweets['text']:
        mentions1.extend(re.findall(r'@\w+', tweet))
    top_users = pd.Series(mentions1).value_counts().nlargest(10)
    stats['top_users'] = top_users
    
    return stats

def compute_and_print_tweet_stats_choice_2(df):
    # Calculate the average number of tweets per day
    avg_tweets_per_day = len(df) / len(df['date'].dt.date.unique())
        
    # Calculate the percentage of tweets that contain hashtags
    hashtag_tweets = df[df['content'].str.contains('#')]
    percentage_hashtag_tweets = (len(hashtag_tweets) / len(df)) * 100
        
    # Calculate the percentage of tweets that contain URLs
    url_tweets = df[df['content'].str.contains('http')]
    percentage_url_tweets = (len(url_tweets) / len(df)) * 100
        
    # Calculate the percentage of tweets that contain mentions
    mention_tweets = df[df['content'].str.contains('@')]
    percentage_mention_tweets = (len(mention_tweets) / len(df)) * 100
        
    # Calculate the percentage of tweets that are retweets
    retweet_tweets = df[df['content'].str.startswith('RT ')]
    percentage_retweet_tweets = (len(retweet_tweets) / len(df)) * 100
        
    # Calculate the percentage of tweets that are replies
    reply_tweets = df[df['content'].str.startswith('@')]
    percentage_reply_tweets = (len(reply_tweets) / len(df)) * 100
        
    # Top 10 users mentioned in the scraped tweets
    mentions = df['content'].str.findall(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)').explode().value_counts()[:10]
    
    # Top 10 hashtags used in the scraped tweets
    hashtags = df['content'].str.findall(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))#([A-Za-z0-9_]+)').explode().value_counts()[:10]
        
    # Ask the user for their desired keywords
    keywords = input("Enter your desired political keywords separated by a space (not case-sensitive but enter appropriate foreign-language spelling (for example, erdoğan != erdogan): ")
        
    # Split the user's input into a list of keywords
    keywords_list = keywords.split()
        
    # Construct the regex pattern for the keywords
    pattern = r'\b(?:{})\b'.format('|'.join(keywords_list))
        
    # Frequency of mentions of specific political figures or issues
    political_figures = df['content'].str.findall(pattern, flags=re.IGNORECASE).explode().value_counts()

    # Sentiment analysis of the scraped tweets
    polarity_scores = df['content'].apply(lambda x: TextBlob(x).sentiment.polarity)
    sentiment = 'positive' if polarity_scores.mean() > 0 else ('negative' if polarity_scores.mean() < 0 else 'neutral')
    print("-" * 50)
    print("STATISTICS")
    print("-" * 50)
    print(f"Overall sentiment of {username}'s tweets: {sentiment}")
    print(f"Average number of tweets per day: {avg_tweets_per_day:.2f}")
    print(f"Percentage of {username}'s tweets with hashtags: {percentage_hashtag_tweets:.2f}%")
    print(f"Percentage of {username}'s tweets with URLs: {percentage_url_tweets:.2f}%")
    print(f"Percentage of {username}'s tweets with mentions: {percentage_mention_tweets:.2f}%")
    print(f"Percentage of {username}'s tweets that are retweets: {percentage_retweet_tweets:.2f}%")
    print(f"Percentage of {username}'s  tweets that are replies: {percentage_reply_tweets:.2f}%")
    print("-" * 50)
    print(f"Top 10 users mentioned in {username}'s tweets:\n{mentions}")
    print("-" * 50)
    print(f"Top 10 hashtags used in {username}'s tweets:\n{hashtags}")
    print("-" * 50)
    print(f"Frequency of mentions of specific political figures or issues:\n{political_figures}")
    print("-" * 50)
    return {
        'avg_tweets_per_day': avg_tweets_per_day,
        'percentage_hashtag_tweets': percentage_hashtag_tweets,
        'percentage_url_tweets': percentage_url_tweets,
        'percentage_mention_tweets': percentage_mention_tweets,
        'percentage_retweet_tweets': percentage_retweet_tweets,
        'percentage_reply_tweets': percentage_reply_tweets,
        'top_mentions': mentions,
        'top_hashtags': hashtags,
        'political_figures': political_figures,
        'sentiment': sentiment
    }

def plot_weekly_activity(username, num_tweets):
    """
    Scrape the most recent num_tweets tweets for the specified username, 
    plot the weekly activity, and return the resulting scatter plot.
    """
    # Scrape most recent X tweets
    with tqdm(total=int(num_tweets)) as pbar:
        tweets = []
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f"from:{username}").get_items()):
            if i >= int(num_tweets):
                break
            tweets.append([tweet.date, tweet.content])
            pbar.update(1)

    # Convert tweets to pandas DataFrame
    df = pd.DataFrame(tweets, columns=['date', 'content'])

    # Add new columns for day of week and hour of day
    df['day_of_week'] = df['date'].dt.day_name()
    df['hour_of_day'] = df['date'].dt.hour

    # Group tweets by day of week and hour of day and count number of tweets
    grouped_df = df.groupby(['day_of_week', 'hour_of_day']).count().reset_index()

    # Set up plot
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)

    # Create scatter plot with sizes of markers indicating number of tweets
    sizes = grouped_df['content']*10
    scatter = ax.scatter(grouped_df['hour_of_day'], grouped_df['day_of_week'], 
                          s=sizes, alpha=0.5)

    # Set x-axis label and tick labels
    ax.set_xlabel('Hour of Day (Local Time for Account)')
    ax.set_xticks(range(24))
    ax.set_xticklabels(['12am', '1am', '2am', '3am', '4am', '5am', '6am', '7am', '8am', '9am', '10am', '11am', '12pm',
                        '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm', '9pm', '10pm', '11pm'])

    # Set y-axis label and tick labels
    ax.set_ylabel('Day of the Week')
    ax.set_yticks(range(7))
    ax.set_yticklabels(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    # Set title
    ax.set_title(f"{username}'s Weekly Twitter Activity")

    # Create legend
    handles, labels = scatter.legend_elements(prop='sizes', alpha=0.6)
    labels = [str(int(float(label.replace('$\\mathdefault{','').replace("}$",''))/10)) for label in labels]
    legend = ax.legend(handles, labels, title='Number of Tweets', loc='center left', 
                       bbox_to_anchor=(1, 0.5), fontsize='medium')

    # Adjust plot layout to make room for legend
    plt.subplots_adjust(right=0.8)

    # Add tooltip hover functionality
    mplcursors.cursor(scatter, hover=True).connect("add", lambda sel: sel.annotation.set_text(f"{sizes[sel.target.index]/10} tweets"))

    # Show plot
    plt.show()

# User Interface
def welcome_UI():
    print(" ")
    print("Thank you for using SKY_SCRAPE (▰˘◡˘▰). Created by ChatGPT and Kursat Gok.")
    print(" ")
def program_guidelines():
    """
    Prints the program guidelines and instructions.
    """
    print("This program has five parts.")
    print(" ")
    print("Entering '1' will:")
    print("— analyze a twitter account you input,")
    print("— display an amount of tweets you input,") 
    print("— analyze that number of tweets for inauthentic behavior,") 
    print("— tell you if the account is inauthentic or authentic,")
    print("– provide you with relevant account statistics,") 
    print("— prompt you with the option to display up to 100 other unique accounts that are interacting with the hashtags your account is tweeting.")
    print("— and then provide you with the top account contributing to that hashtag other than the original account and prompt you to rerun this part of the program with the new top account.")
    print(" ")
    print("Entering '2' will:") 
    print("— analyze a twitter account you input,")
    print("— easily analyze 5 times more tweets than option 1,")
    print("— visualize that number of tweets over a week and display them in a scatterplot-heatmap for you,")
    print("— prompt you for any political keywords you want to scrape the ingested tweets for,")
    print("— display a variety of relevant statistics,")
    print("— and then tell you how many of the analyzed tweets have the political keywords you entered.")
    print(" ")
    print("Entering '3' will:")
    print("— prompt you for a hashtag of your choosing to scrape up to 100 linked twitter accounts,")
    print("— save those usernames to a .text file named Usernames linked to #YourHashtag.txt. in a folder named 'Twitter IO Analysis'.")
    print(" ")
    print("Entering '4' will:")
    print("— work through the 'Twitter IO Analysis' folder and establish social nodes between active accounts linked to your queried hashtags. If prompted further, will graphically visualize a social network for you. If prompted even further, will perform deep social network analysis and provide you insight into your analyzed accounts using Katz centrality.")
    print(" ")
    print("Entering '5' will:")
    print("— give you a cup of coffee and a cigarette.")
    print(" ")
    print("Entering 'h' will:")
    print("— print this help screen.")
    print(" ")
    print("Entering 'x' will:")
    print("— terminate the program.")
    print(" ")
    print("If you're not sure where to get started, try this: 1) go on Twitter and find an account you think is suspicious, spamming a lot, or acting bot-like. Run this program, hit '1' or '2'', and paste that account's username when prompted. Then see where your investigation takes you!")
    print(" ")

def get_choice():
    while True:
        choice = input("Enter 1, 2, 3, 4, or 5 to run different parts of the program, h for help, or x to quit: ")
        if choice in ['1', '2', '3', '4', '5', 'h', 'x']:
            return choice
        else:
            print("Invalid input. Please enter 1, 2, 3, 4, 5, h, or x.")

def get_user_input_choice_1():
    username = input("Enter a Twitter username (no @ symbol or quotations, just the username): ")
    num_tweets = int(input("How many tweets would you like to display (enter a whole number, 100 is good, more will take longer): "))
    return username, num_tweets

def get_user_input_choice_2():
    username = input("Enter a Twitter username (no @ symbol or quotations, just the username): ")
    num_tweets = int(input("How many tweets would you like to graphically display? Enter a whole number, 500 is good, more will take longer: "))
    print("*" * 50)
    print("Please be patient... it may take a minute to visualize your data.")
    print("*" * 50)
    return username, num_tweets

def print_recent_tweets(df_tweets, username, num_tweets):
    """
    Print the most recent num_tweets tweets for the specified username
    in either a detailed or compact view, depending on user input.
    """
    print("-" * 50)
    print(f"Most recent {num_tweets} tweets from {username}:")
    print("-" * 50)
    
    while True:
        view = input("Enter 'd' for detailed view (if you prefer to examine the contents of the tweets), 'c' for compact view (if you prefer to examine the timeline of the tweets), or 'n' to skip the tweets and only view the summarizing analysis: ")
        if view.lower() == 'd':
            for tweet, date in zip(df_tweets['text'], df_tweets['datetime']):
                print(tweet)
                print(date)
                print()
            break
        elif view.lower() == 'c':
            print(df_tweets)
            break
        elif view.lower() == 'n':
            break
        else:
            print("Invalid input. Please enter 'd', 'c', or 'n'.")
    print("-" * 50)

def print_tweet_stats(stats, num_tweets, username):
    print("-" * 50)
    print(f"Statistics on last {num_tweets} tweets from {username}")
    print("-" * 50)
    print(f"Average length of {username}'s tweets (in characters): {round(stats['avg_tweet_len'], 2)}")
    print(f"Percentage of {username}'s tweets that mention other users: {round(stats['percent_with_mention'], 2)}%")
    print(f"Percentage of {username}'s tweets that contain hashtags: {round(stats['percent_with_hashtag'], 2)}%")
    print(f"Average number of retweets per tweet: {round(stats['avg_retweets'], 2)}")
    print("Top 10 hashtags:")
    print(stats['top_hashtags'])
    print("-" * 50)
    print(f"Top 10 users mentioned in {username}'s past {num_tweets} tweets:")
    print("-" * 50)
    print(stats['top_users'])

def prompt_user_hashtag_research(account_usernames, username, top_hashtag):
    response = input("Do you want to enter a new username? (y/n):") 
    print("- " * 50)
    if response.lower() != 'y':
        return False
    else:
        print("Hint: (☞ﾟ∀ﾟ)☞ try analyzing an account in the list of recent unique accounts associated with the inputted user's top hashtag.")
        print("- " * 50)
        return True

def prompt_user_rerun():
    response = input("Do you want to run the program again? (y/n): ")
    if response.lower() != 'y':
        sys.exit(0)
    else:
        return True

def account_privacy_error():
    print("Whoops!")
    raise Exception("(╯°□°)╯︵ ┻━┻ This account either no longer exists, you entered it incorrectly, or the account's privacy setting are set to restricted/other anti-scraping measures have been taken to secure its tweets. Please manually visit and analyze the account on Twitter.")

# Other functions
def create_usernames_file(hashtag, account_usernames):
    # Get the path to the desktop
    desktop_path = os.path.expanduser("~/Desktop")

    # Create a full path to the "Twitter IO Analysis" folder on the desktop
    save_file_path = os.path.join(desktop_path, "Twitter_IO_Analysis")

    # Check if the "Python Stuff" folder already exists, and create it if it doesn't
    if not os.path.exists(save_file_path):
        os.makedirs(save_file_path)

    # Create a text file named "example.txt" in the "Twitter_IO_Analysis" folder
    file_name = f"Usernames linked to #{hashtag}.txt"
    file_path = os.path.join(save_file_path, file_name)

    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("\n".join(account_usernames))
            print(f"File '{file_name}' created on your desktop inside of a folder named Twitter IO Analysis.")
    else:
        print(f"File '{file_name}' saved successfully where it normally lives.")

# Choice 4 Functions Below

def get_usernames_from_file(file_path, encoding='cp1254'):
    """
    This function takes the path to a text file containing Twitter account usernames
    and returns a list of the usernames.
    """
    with open(file_path, 'r', encoding=encoding) as f:
        account_usernames = f.read().splitlines()
    return account_usernames

def print_filenames_in_folder():
    # Get the path to the desktop
    desktop_path = os.path.expanduser("~/Desktop")

    # Create a full path to the "Twitter_IO_Analysis" folder on the desktop
    analysis_folder_path = os.path.join(desktop_path, "Twitter_IO_Analysis")

    # Print the file names in the "Twitter_IO_Analysis" folder on the desktop
    print("-" * 50)
    print(f"Files in '{analysis_folder_path}':")
    for filename in os.listdir(analysis_folder_path):
        try:
            filename_decoded = filename.encode('cp1254').decode('utf-8', errors='ignore')
            print(f"  {filename_decoded}")
        except UnicodeEncodeError:
            print(f"  Error reading filename '{filename}': UnicodeEncodeError")
    print("-" * 50)

def manually_compare_usernames_in_files():
    hashtag1 = input("Enter the hashtag associated with the first file of usernames you want to compare:")
    file_name1 = f"Usernames linked to #{hashtag1}.txt"
    hashtag2 = input("Enter the hashtag associated with the second file of usernames you want to compare:")
    file_name2 = f"Usernames linked to #{hashtag2}.txt"

    # Get the path to the desktop
    desktop_path = os.path.expanduser("~/Desktop")

    # Create full paths to the two usernames files in the "Twitter_IO_Analysis" folder on the desktop
    usernames_file_path1 = os.path.join(desktop_path, "Twitter_IO_Analysis", file_name1)
    usernames_file_path2 = os.path.join(desktop_path, "Twitter_IO_Analysis", file_name2)

    # Check if the usernames files exist, and get the usernames if they do
    if os.path.exists(usernames_file_path1) and os.path.exists(usernames_file_path2):
        with open(usernames_file_path1) as f:
            usernames1 = set([line.strip() for line in f])
        with open(usernames_file_path2) as f:
            usernames2 = set([line.strip() for line in f])

        overlapping_usernames = usernames1.intersection(usernames2)

        if overlapping_usernames:
            print(f"Overlapping usernames between '{file_name1}' and '{file_name2}':")
            for username in overlapping_usernames:
                print(username)
        else:
            print("-" * 50)
            print(f"There are no overlapping usernames between '{file_name1}' and '{file_name2}'.")
            print("-" * 50)
    else:
        if not os.path.exists(usernames_file_path1):
            print(f"Usernames file '{file_name1}' does not exist at '{usernames_file_path1}'.")
        if not os.path.exists(usernames_file_path2):
            print(f"Usernames file '{file_name2}' does not exist at '{usernames_file_path2}'.")

def auto_compare_usernames_in_files():
    # Get the path to the desktop
    desktop_path = os.path.expanduser("~/Desktop")

    # Create a full path to the "Twitter_IO_Analysis" folder on the desktop
    analysis_folder_path = os.path.join(desktop_path, "Twitter_IO_Analysis")

    # Get the list of file names in the "Twitter_IO_Analysis" folder on the desktop
    file_names = os.listdir(analysis_folder_path)

    # Get the full paths to the usernames files in the "Twitter_IO_Analysis" folder on the desktop
    usernames_file_paths = [os.path.join(analysis_folder_path, file_name) for file_name in file_names]
    
    # Define the dictionary
    overlapping_usernames_dict = {}
    
    # Define a function to log the overlapping usernames and assign them a point of +1
    def log_overlapping_usernames(overlapping_usernames, comparison_str):
        print(f"Overlapping usernames between {comparison_str}:")
        print("-" * 50)
        for username in overlapping_usernames:
            print(username)
            # assign a point of +1 for each overlapping username
            if username in overlapping_usernames_dict:
                overlapping_usernames_dict[username] += 1
            else:
                overlapping_usernames_dict[username] = 1
        print("-" * 50)

    # Check if each pair of usernames files exist, and get the usernames if they do
    for i in tqdm(range(len(usernames_file_paths))):
        for j in range(i+1, len(usernames_file_paths)):
            usernames_file_path1 = usernames_file_paths[i]
            usernames_file_path2 = usernames_file_paths[j]
            file_name1 = os.path.basename(usernames_file_path1)
            file_name2 = os.path.basename(usernames_file_path2)

            if os.path.exists(usernames_file_path1) and os.path.exists(usernames_file_path2):
                try:
                    usernames1 = set(get_usernames_from_file(usernames_file_path1, encoding='cp1254'))
                    usernames2 = set(get_usernames_from_file(usernames_file_path2, encoding='cp1254'))
                except UnicodeDecodeError:
                    print(f"Error: Unable to read file '{file_name1}' or '{file_name2}' due to unsupported characters in file name.")
                    print("Please rename the file(s) and try again.")
                    continue

                overlapping_usernames = usernames1.intersection(usernames2)

                if overlapping_usernames:
                    # Call the new function to log the overlapping usernames and assign them points
                    comparison_str = f"'{file_name1}' and '{file_name2}'"
                    log_overlapping_usernames(overlapping_usernames, comparison_str)
            else:
                if not os.path.exists(usernames_file_path1):
                    print(f"Usernames file '{file_name1}' does not exist at '{usernames_file_path1}'.")
                if not os.path.exists(usernames_file_path2):
                    print(f"Usernames file '{file_name2}' does not exist at '{usernames_file_path2}'.")
    return overlapping_usernames_dict
    
def check_for_inauthentic_behavior(overlapping_usernames_dict):
    print("- - " * 20)
    print("Usernames with recent activity linked to more than 5 different hashtags:")
    print("- - " * 20)
    sorted_dict = dict(sorted(overlapping_usernames_dict.items(), key=lambda item: item[1], reverse=True))
    selected_usernames = []
    for username, count in sorted_dict.items():
        if count > 5:
            print(f"{username}: {count}")
            selected_usernames.append(username)
    print("- - " * 20)
    return selected_usernames

def scrape_and_list_common_mentions(selected_usernames, num_tweets):
    df = pd.DataFrame(columns=['user', 'date', 'content'])
    mentions_dict = {}
    for username in selected_usernames:
        query = f'from:{username}'
        tweets = sntwitter.TwitterSearchScraper(query).get_items()
        for i, tweet in enumerate(tqdm(tweets, desc=f'Scraping {username}', total=num_tweets)):
            if i >= num_tweets:
                break
            content = tweet.content
            date = tweet.date
            df = df.append({'user': username, 'date': date, 'content': content}, ignore_index=True)

    # Find the top 10 mentions for each user and store them in a dictionary
    for username in selected_usernames:
        mentions = []
        df_user = df[df['user'] == username]
        for content in df_user['content']:
            mentions += re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)', content)
        top_mentions = [mention for mention, count in Counter(mentions).most_common(10)]
        mentions_dict[username] = top_mentions

    return mentions_dict

def print_mentions(mentions_dict):
    for key, value in mentions_dict.items():
        print("Suspect user:", key)
        print("\t", "Top 10 @'d accounts")
        for i, mention in enumerate(value):
            print(f"\t{i+1}. {mention}")

def find_social_network(mentions_dict):
    social_network = []
    for user, mentions in mentions_dict.items():
        if user == 'RTErdogan':
            continue
        for mention in mentions:
            if mention == 'RTErdogan':
                continue
            if mention in mentions_dict:
                if user not in social_network:
                    social_network.append(user)
                if mention not in social_network:
                    social_network.append(mention)
    return social_network

def print_top_mentions(social_network, mentions_dict):
    choice = input("Would you like to view the top 10 @'d accounts for the users in the social network list? (y/n): ")
    if choice.lower() == "y":
        for username in social_network:
            top_mentions = mentions_dict.get(username)
            if top_mentions:
                print(f"Top 10 mentions for {username}:")
                for i, mention in enumerate(top_mentions[:10], 1):
                    print(f"{i}. {mention}")
            else:
                print(f"No mentions found for {username}.")
    choice2 = input("Would you like to save the @'s (excluding @RTErdogan) associated with the social network list to a .text file for future analysis? (y/n): ")
    if choice2.lower() == "y":
        # Save top 10 mentions to file
        desktop_path = os.path.expanduser("~/Desktop")
        save_file_path = os.path.join(desktop_path, "Twitter_IO_Analysis")
        if not os.path.exists(save_file_path):
            os.makedirs(save_file_path)
        file_name = file_name = f"Top 10 mentions for {social_network[0:3]}, and others...txt"
        file_path = os.path.join(save_file_path, file_name)
        with open(file_path, "w") as f:
            for username in social_network:
                top_mentions = mentions_dict.get(username)
                if top_mentions:
                    for i, mention in enumerate(top_mentions[:10], 1):
                        if mention != "RTErdogan":
                            f.write(f"{mention}\n")
                else:
                    f.write(f"No mentions found for {username}.\n")
        print(f"Top 10 mentions saved to file '{file_name}' on your desktop inside of a folder named Twitter IO Analysis.")
    choice3 = input("Would you like to save just the @'s  associated with the social network list to a .text file for future analysis? (y/n): ")
    if choice3.lower() == "y":
        # Save just the usernames in the social_network list to a new file
        desktop_path = os.path.expanduser("~/Desktop")
        save_file_path = os.path.join(desktop_path, "Twitter_IO_Analysis")
        if not os.path.exists(save_file_path):
            os.makedirs(save_file_path)
        file_name = f"{social_network[0:3]}, and others.txt"
        file_path = os.path.join(save_file_path, file_name)
        with open(file_path, "w") as f:
            for username in social_network:
                f.write(f"{username}\n")
        print(f"Social network saved to file '{file_name}' on your desktop inside of a folder named Twitter IO Analysis.")
        
def plot_usernames_count(overlapping_usernames_dict):
    sorted_dict = dict(sorted(overlapping_usernames_dict.items(), key=lambda item: item[1], reverse=True))
    selected_usernames = []
    for username, count in sorted_dict.items():
        if count > 5:
            selected_usernames.append(username)

    x_vals = []
    y_vals = []
    num_skipped = 0
    prev_val = None
    for val, count in sorted_dict.items():
        if count > 5:
            x_vals.append(val)
            y_vals.append(count)
        elif prev_val is not None and count == prev_val:
            num_skipped += 1
        else:
            if num_skipped > 0:
                x_vals[-1] += f"\nand {num_skipped} others"
                num_skipped = 0
            x_vals.append(val)
            y_vals.append(count)
            prev_val = count

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x_vals, y_vals, width=0.6, align='center', edgecolor='black', linewidth=0.5, color='gray', alpha=0.8)
    ax.set_xlabel("Twitter Accounts", fontsize=10)
    ax.set_ylabel("Recent Activity with Analyzed Hashtags", fontsize=10)
    ax.set_xticklabels(x_vals, rotation=90, fontsize=8, va='top', ha='center')
    ax.set_title("Twitter Accounts with Significant Activity Behind Analyzed Hashtags", fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.subplots_adjust(bottom=0.2)
    for i, v in enumerate(y_vals):
        ax.text(i, v + 1, str(v), ha='center', fontsize=8, fontweight='bold')
    plt.show()

# Social Network Visualization
def network_analysis_graph(mentions_dict, threshold=0.04, alpha=0.5, beta=0.5):
    
    """Incorporates a weighted combination of eigenvector centrality 
        and in-betweenness centrality to visualize the social network.
        The function takes two additional parameters beyond the usernames
        and the threshold for visualizing nodes in the network: alpha and beta, 
        which control the weighting of in-betweenness centrality and eigenvector 
        centrality, respectively. The combined centrality is calculated as 
        alpha * betweenness + beta * eigenvector. The top nodes are then selected 
        based on this combined centrality value."""
    
    # Get user input for excluded usernames
    exclude_usernames = input("Enter usernames you want to exclude separated by commas (leave blank for none): ").split(",")
    exclude_usernames = [username.strip() for username in exclude_usernames if username.strip()]
    
    # Create graph and add edges for mentions
    G = nx.Graph()
    for account, interacted_accounts in mentions_dict.items():
        for mentioned_account in interacted_accounts:
            if account not in exclude_usernames and mentioned_account not in exclude_usernames:
                G.add_edge(account, mentioned_account)

    # Calculate betweenness centrality and eigenvector centrality, and filter out small nodes
    betweenness = nx.betweenness_centrality(G)
    eigenvector = nx.eigenvector_centrality(G)
    nodes_above_threshold = [n for n in G.nodes() if betweenness.get(n, 0) > threshold and n not in exclude_usernames]

    # Set positions for nodes and handle errors
    try:
        positions = nx.kamada_kawai_layout(G)
    except nx.NetworkXError:
        positions = nx.random_layout(G)

    # Calculate combined centrality
    combined_centrality = {}
    for node in nodes_above_threshold:
        combined_centrality[node] = alpha * betweenness[node] + beta * eigenvector[node]

    # Draw nodes and edges
    node_sizes_filtered = [combined_centrality[n] * 3000 for n in nodes_above_threshold]
    plt.figure(figsize=(10, 10))
    nx.draw_networkx_nodes(G, positions, nodelist=nodes_above_threshold, node_color='r', node_size=node_sizes_filtered)
    nx.draw_networkx_edges(G, positions, edge_color='grey', width=0.5)

    # Add labels for significant nodes
    pos_labels = {}
    for k, v in positions.items():
        if k in nodes_above_threshold:
            pos_labels[k] = v

    try:
        nx.draw_networkx_labels(G, pos_labels, font_size=20, font_weight='normal', font_family='georgia')
    except KeyError:
        pass

    # Add labels for top nodes
    top_nodes = set(sorted(combined_centrality, key=combined_centrality.get, reverse=True)[:int(len(nodes_above_threshold)*0.5)])
    for node in top_nodes:
        if node in pos_labels:
            x, y = pos_labels[node]
            node_size = node_sizes_filtered[nodes_above_threshold.index(node)]
            fontsize = node_size/50
            if fontsize < 10:
                fontsize = 10
            plt.text(x, y, node, fontsize=fontsize, ha='center', va='center', color='black', fontweight='bold')

    # Remove axis
    plt.axis('off')

    # Add dynamic legend key
    social_network = find_social_network(mentions_dict)
    legend_labels = [f"{i+1}. {label.replace('_', ' ')}" for i, label in enumerate(social_network)]
    legend_handles = [mpatches.Patch(label=label, fill=False, edgecolor='none') for label in legend_labels]
    plt.legend(handles=legend_handles, loc='upper left', title='High Linkage', 
               title_fontsize=12, fontsize=8)
    
    # Add title to the graph
    plt.suptitle('Social Network Visualization', fontsize=14, y=0.95)

    # Show plot
    plt.show()

def create_network_diagram(usernames_obj):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes to the graph for each username and its top mentions
    for username in usernames_obj.usernames:
        G.add_node(username)
        if username in usernames_obj.top_mentions:
            for mention in usernames_obj.top_mentions[username]:
                mention_cleaned = mention.replace("@", "")
                G.add_node(mention_cleaned)

    # Add edges to the graph between the usernames and their top mentions
    for username in usernames_obj.usernames:
        if username in usernames_obj.top_mentions:
            for mention in usernames_obj.top_mentions[username]:
                # Remove "@" character from beginning of node labels
                username_cleaned = username.replace("@", "")
                mention_cleaned = mention.replace("@", "")
                G.add_edge(username_cleaned, mention_cleaned)

    # Calculate Katz centrality
    katz_centrality = nx.katz_centrality(G)

    # Set node positions using the spring layout algorithm
    pos = nx.spring_layout(G)

    # Draw the nodes and edges on the graph, with node color based on katz centrality values
    node_colors = list(katz_centrality.values())
    median = sorted(node_colors)[len(node_colors) // 2]
    fig, ax = plt.subplots(figsize=(20, 20))
    nodes = nx.draw_networkx_nodes(G, pos, node_size=300, node_color=node_colors, cmap=plt.cm.Blues, alpha=0.8)
    labels = nx.draw_networkx_labels(G, pos, font_size=12, font_family="Arial", font_color='black', alpha=0.7)

    # Add cursor
    cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

    # Draw the edges
    nx.draw_networkx_edges(G, pos, width=2, edge_color="gray", alpha=0.4, arrowsize=30)

    # Add color bar for node colors
    sm = plt.cm.ScalarMappable(cmap=plt.cm.Blues, norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors)))
    sm.set_array([])
    cbar = plt.colorbar(sm)
    cbar.ax.set_title('Katz Centrality')

    # Set the figure size and show the diagram
    plt.axis("off")
    plt.show()

def save_usernames(usernames_list):
    usernames = Usernames()
    usernames.add_usernames(usernames_list)
    return usernames

def iterate_usernames(username_obj):
    for username in username_obj.usernames:
        username_obj.get_top_mentions(username)

#Coffee Bar
def coffee_order():
    print(" ")
    print("Welcome to the café!")
    print(" ")
    order = input("""What would you like to order?

(a) Regular cup of dark roast
(b) a cigarette

Please enter the letter of your choice: """)
    
    if order.lower() == "a":
        return cup_of_coffee()
    elif order.lower() == "b":
        return cigarette()
    else:
        return "I'm sorry, I don't understand that order. Please try again."

def cup_of_coffee():
    print(" ")
    print("   )( ")
    print(" :----:")
    print("C|====|")
    print(" |    |")
    print(" `----'")
    print(" ")
    print("Here's a fresh cup of dark roast. You deserve it.")
    print(" ")
    return None
def cigarette():
    print(" ")
    print("                )")
    print("               (")
    print(" _ ___________ )")
    print("[_[___________#")
    print(" ")
    print("Here's a cigarette. You deserve it.")
    print(" ")

### End of functions list ###

# Classes

class Usernames:
    def __init__(self):
        self.usernames = set()
        self.tweets = {}
        self.top_mentions = {}

    def add_usernames(self, new_usernames):
        self.usernames.update(set(new_usernames))
    
    def scrape_twitter_data(self):
        for username in tqdm(self.usernames, desc="Scraping Twitter data"):
            tweets_list = []
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f"from:{username}").get_items()):
                if i >= 1000:
                    break
                tweets_list.append([tweet.date, tweet.content])
            if len(tweets_list) > 0:
                self.tweets[username] = pd.DataFrame(tweets_list, columns=["datetime", "content"])
    
    def get_top_mentions(self, username):
        # Find all mentions (@) in tweets and store them in a list
        mentions = []
        for tweet in self.tweets[username]["content"]:
            mention_list = re.findall(r"@\w+", tweet)
            mentions.extend(mention_list)
    
        # Count the frequency of each mention and store the top 10 most frequent
        top_mentions = Counter(mentions).most_common(10)
        top_mentions = [mention[0] for mention in top_mentions]
    
        # Store the top 10 mentions for the username
        self.top_mentions[username] = top_mentions

# Start of main script

# Filter out FutureWarning and DeprecatedFeatureWarning
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="Selection.target.index is deprecated and will be removed in the future")

welcome_UI()

while True:
    
    choice = get_choice()

    if choice == "1":
        
        try:
           
            # Prompt user for first input
            username, num_tweets = get_user_input_choice_1()
            
            # Run main 1
            execute_choice_1(username, num_tweets)
            
            # Prompt user for hashtag search
            do_hashtag_search = input("Do you want to scrape accounts linked to the most tweeted hashtag in this user's tweets? (y/n): ")
            
            if do_hashtag_search.lower() == 'y':
                
                # Print the accounts associated with the top hashtag
                top_hashtag = get_top_hashtag(username, num_tweets)
                
                account_usernames = list(get_related_accounts(top_hashtag))
                
                print("Do you want to save this list of usernames associated with this hashtag for future analysis?")
                
                prompt = input("(y/n): ")
                
                if prompt.lower() == 'y':
                    
                    create_usernames_file(top_hashtag, account_usernames)
                
                else:
                    
                    pass
                
                while prompt_user_hashtag_research(account_usernames, username, top_hashtag):
                    
                    username, num_tweets = get_user_input_choice_1()
                    
                    execute_choice_1(username, num_tweets)
                    
                prompt_user_rerun()
                
            else:
                
                prompt_user_rerun()
                
        except KeyError:
            
            account_privacy_error()            

            prompt_user_rerun()

    elif choice == "2":
        
        try:
           
            # Prompt user for first input
            username, num_tweets = get_user_input_choice_2()
            
            # Run main 2
            execute_choice_2(username, num_tweets)
            
        except AttributeError:
            
            account_privacy_error()
            
            prompt_user_rerun()
            
    elif choice == '3':
       
        # Run Main 3
        execute_choice_3()

        prompt_user_rerun()
    
    elif choice == '4':
        
        # Define hashtags and file names
        print_filenames_in_folder()
        
        compare_mode = input("Enter 'm' to manually compare files, or 'a' (recommended method) to automatically compare every combination of each file: ")
        
        if compare_mode.lower() == 'm':
        
            manually_compare_usernames_in_files()
        
        elif compare_mode.lower() == 'a':
            
            overlapping_usernames_dict = auto_compare_usernames_in_files()
            
            # add classes here
            
            selected_usernames = check_for_inauthentic_behavior(overlapping_usernames_dict)
            
            plot_usernames_count(overlapping_usernames_dict)
            
            print(" ")
            print("-"*50)
            print("The next part of the program will determine interactions between the top accounts and compare their top 10 @'d accounts. If you just wanted a list of top accounts boosting hashtags, press 'x' to exit.")
            print("-"*50)
            print(" ")
            
            while True:
                
                num_tweets_input = input("Enter a number of tweets (at least 50, less than 200 to take less time) to analyze for each selected user, where the output will be their top 10 mentions (enter 'x' to quit): ")
                
                if num_tweets_input.lower() == "x":
                    
                    sys.exit()
                
                try:
                    num_tweets = int(num_tweets_input)
                    
                    break
                
                except ValueError:
                    
                    print("Invalid input. Please enter a whole number or 'exit' to quit.")
            
            mentions_dict = scrape_and_list_common_mentions(selected_usernames, num_tweets)
            
            print_mentions(mentions_dict)
            
            network_analysis_graph(mentions_dict)
            
            social_network = find_social_network(mentions_dict)
            
            print("Social network determined between users: ", social_network)
            
            # print_top_mentions(social_network, mentions_dict)
            
            network_obj = Usernames()
            
            network_obj.add_usernames(set(social_network))
            
            print(" ")
            go_deeper = input("Do you want to go ~ D E E P E R ~ ? (y/n): ")
                        
            if go_deeper.lower() == 'y':
                
                print("Say no more. This may take a minute... (-■_■)")
                
                print(" ")
                print("Scraping recent 1,000 tweets from each account in the social network, determining their top 10 mentions, and visualizing their connections using Katz centrality.")
                print(" ")
                print("What is Katz centrality? I'm glad you asked.")
                print("According to ChatGPT: 'Katz centrality is based on the idea that nodes are important if they are connected to other important nodes. It assigns a score to each node based on the sum of the scores of its neighbors, with higher weights given to more proximal nodes and lower weights given to more distant nodes. The algorithm works by solving a system of linear equations to calculate the centrality scores of all nodes.'")
                print(" ")
                network_obj.scrape_twitter_data()
                            
                iterate_usernames(network_obj)
                
                create_network_diagram(network_obj)
                
            else:
                
                prompt_user_rerun()
    
        elif compare_mode.lower() == 'x':
        
            break
        
        else:
        
            print("Invalid input. Please enter 'm' or 'a', or enter 'x' to exit the program.")
        
        prompt_user_rerun()
    
    elif choice == '5':

        coffee_order()
    
    elif choice == 'h':
        
        program_guidelines()
    
    elif choice == 'x':
        
        print(" ")
        print("Exiting program... Hope to see you soon!")
        print(" ")
        
        break

    else:
        
        print("Invalid input. Please enter 1, 2, 3, 4, 5, 'h', or 'x' to quit.")