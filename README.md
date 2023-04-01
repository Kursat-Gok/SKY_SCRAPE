# SKY_SCRAPE
A multi-purpose program built around the powerful Twitter scraper Snscrape

Literally anyone can use this Twitter scraper. It does not require Twitter API authentication or even a Twitter account.

My technical goal for this project was to master the art of interrogating ChatGPT until it spat out relatively scalable, 
easy-to-use code for information operations analysis. I am new to programming and this project is far from perfect, I welcome any and all feedback.

The program has five main functions:

1) by pressing '1' in the main menu the user is prompted to input a Twitter account they might be curious about. Based on the inputted account's
recent activity, the program looks at the contens and timeline of their tweets to determine inauthentic behavior and is biased towards not identifying
accounts as inauthentic. I designed the functions to minimize false positives by adding high thresholds for identifying inauthentic behavior. It is important
to note that any assessments on inauthenticity should be taken with a grain of salt and you should always do your homework while investigating specific accounts.
Do not assume the program correctly labelled the account. Make all assessments in a broader context.

2) by pressing '2' the user can visualize the weekly behavior of the inputted account in a graph — seeing for themselves if the long-term behavior of the
account in question is inhuman (i.e. tweeting 300 times in one hour) or does indeed look like a regular person's Twitter activity (spread throughout the
week and rarely/never at 6am/7am). After visualizing the weekly behavior of the account, the user is prompted with input for political keywords they would
like to scrape the contents of the accounts' tweets for. This function aims to provide the user with insight into the purpose behind the account in question.

3) by pressing '3' the user is prompted to research a hashtag for a list of usernames tied to the hashtag. This program is ESSENTAIL for prepraring for part 4
of the program. Option 3 assumes the user has observed interesting hashtags from previously inputted accounts in parts 1 and 2. The program scrapes the
most recent, up to 100 unique Twitter accounts that have contributed to the hashtag being searched (the program will not count an account twice for
a hashtag by ignoring duplicate tweets with the same hashtag). Then the list of usernames is saved to the user's desktop in a folder named Twitter IO analysis into 
a text file for the specific queried hashtag. Querying the same hashtag will overwrite the same file but not if the hashtag is different. This allows the
user to save space in the folder by only having the most recent lists of usernames for a hashtag as the old usernames are overwritten over time. If you want
to keep a record of previous lists of usernames associated with an ongoing hashtag be sure to move the files to a new folder. The user will be done
with this section when they are satisfied with the amount of hashtags they have scraped for contributing accounts and saved to their desktop — ideally 20+.
More is always better if you have the time and the scope of your investigation warrants it.

4) by pressing '4' the user has the option to go through the list of usernames linked to hashtags, scraping the listed accounts of an 
inputted number of recent tweets for their top 10 @’d mentions, comparing the frequency of mentions between all of the accounts, 
providing the user with the option to exclude certain outlier nodes that may be in the top 10 mentions (such as political leaders, celebrities, etc.),
and then mapping suspected inauthentic accounts’ relationships with each other using a function ChatGPT wrote for mapping social networks 
using the NetworkX Python module through a 50/50 weighted combination of in-betweenness and eigenvector centrality 
(the weighted combination is easily readjustable). Finally, the user is provided with a Kamada-Kawai Layout or Random Layout 
based on how successful the program was in mapping the inputted social nodes.

5) by pressing '5' the user goes to a small cafe that prints ASCII art for a cup of coffee or a cigarette.
