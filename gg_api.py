'''Version 0.5'''
import json
import re
from data_structs import Event, Award, Nominee

#from datetime import datetime #for debugging only as of now
#from langdetect import detect

#name of ceremony
NAME = "the Golden Globes"

# Year of the Golden Globes ceremony being analyzed
YEAR = "2013"

#Global Variable for entire EVENT
event = None

# Global variable to store processed tweets
final_tweets = []
# Global variable for hardcoded award names
# This list is used by get_nominees(), get_winner(), and get_presenters() functions
# as the keys for their returned dictionaries
# Students should populate this list with the actual award categories for their year, to avoid cascading errors on outputs that depend on correctly extracting award names (e.g., nominees, presenters, winner)

AWARD_NAMES = [
    "best screenplay - motion picture",
    "best director - motion picture",
    "best performance by an actress in a television series - comedy or musical",
    "best foreign language film",
    "best performance by an actor in a supporting role in a motion picture",
    "best performance by an actress in a supporting role in a series, mini-series or motion picture made for television",
    "best motion picture - comedy or musical",
    "best performance by an actress in a motion picture - comedy or musical",
    "best mini-series or motion picture made for television",
    "best original score - motion picture",
    "best performance by an actress in a television series - drama",
    "best performance by an actress in a motion picture - drama",
    "cecil b. demille award",
    "best performance by an actor in a motion picture - comedy or musical",
    "best motion picture - drama",
    "best performance by an actor in a supporting role in a series, mini-series or motion picture made for television",
    "best performance by an actress in a supporting role in a motion picture",
    "best television series - drama",
    "best performance by an actor in a mini-series or motion picture made for television",
    "best performance by an actress in a mini-series or motion picture made for television",
    "best animated feature film",
    "best original song - motion picture",
    "best performance by an actor in a motion picture - drama",
    "best television series - comedy or musical",
    "best performance by an actor in a television series - drama",
    "best performance by an actor in a television series - comedy or musical"
]

def get_hosts(year):
    '''Returns the host(s) of the Golden Globes ceremony for the given year.
    
    Args:
        year (str): The year of the Golden Globes ceremony (e.g., "2013")
    
    Returns:
        list: A list of strings containing the host names. 
              Example: ["Seth Meyers"] or ["Tina Fey", "Amy Poehler"]
    
    Note:
        - Do NOT change the name of this function or what it returns
        - The function should return a list even if there's only one host
    '''
    # Your code here
    return hosts

def get_awards(year):
    '''Returns the list of award categories for the Golden Globes ceremony.
    
    Args:
        year (str): The year of the Golden Globes ceremony (e.g., "2013")
    
    Returns:
        list: A list of strings containing award category names.
              Example: ["Best Motion Picture - Drama", "Best Motion Picture - Musical or Comedy", 
                       "Best Performance by an Actor in a Motion Picture - Drama"]
    
    Note:
        - Do NOT change the name of this function or what it returns
        - Award names should be extracted from tweets, not hardcoded
        - The only hardcoded part allowed is the word "Best"
    '''
    # Your code here
    return awards

def get_nominees(year):
    '''Returns the nominees for each award category.
    
    Args:
        year (str): The year of the Golden Globes ceremony (e.g., "2013")
    
    Returns:
        dict: A dictionary where keys are award category names and values are 
              lists of nominee strings.
              Example: {
                  "Best Motion Picture - Drama": [
                      "Three Billboards Outside Ebbing, Missouri",
                      "Call Me by Your Name", 
                      "Dunkirk",
                      "The Post",
                      "The Shape of Water"
                  ],
                  "Best Motion Picture - Musical or Comedy": [
                      "Lady Bird",
                      "The Disaster Artist",
                      "Get Out",
                      "The Greatest Showman",
                      "I, Tonya"
                  ]
              }
    
    Note:
        - Do NOT change the name of this function or what it returns
        - Use the hardcoded award names as keys (from the global AWARD_NAMES list)
        - Each value should be a list of strings, even if there's only one nominee
    '''
    # Your code here
    return nominees

def get_winner(year):
    '''Returns the winner for each award category.
    
    Args:
        year (str): The year of the Golden Globes ceremony (e.g., "2013")
    
    Returns:
        dict: A dictionary where keys are award category names and values are 
              single winner strings.
              Example: {
                  "Best Motion Picture - Drama": "Three Billboards Outside Ebbing, Missouri",
                  "Best Motion Picture - Musical or Comedy": "Lady Bird",
                  "Best Performance by an Actor in a Motion Picture - Drama": "Gary Oldman"
              }
    
    Note:
        - Do NOT change the name of this function or what it returns
        - Use the hardcoded award names as keys (from the global AWARD_NAMES list)
        - Each value should be a single string (the winner's name)
    '''
    #for award in AWARD_NAMES:
    return winners

def get_presenters(year):
    '''Returns the presenters for each award category.
    
    Args:
        year (str): The year of the Golden Globes ceremony (e.g., "2013")
    
    Returns:
        dict: A dictionary where keys are award category names and values are 
              lists of presenter strings.
              Example: {
                  "Best Motion Picture - Drama": ["Barbra Streisand"],
                  "Best Motion Picture - Musical or Comedy": ["Alicia Vikander", "Michael Keaton"],
                  "Best Performance by an Actor in a Motion Picture - Drama": ["Emma Stone"]
              }
    
    Note:
        - Do NOT change the name of this function or what it returns
        - Use the hardcoded award names as keys (from the global AWARD_NAMES list)
        - Each value should be a list of strings, even if there's only one presenter
    '''
    # Your code here
    return presenters

def clean_tweet(tweet):
    #helper function, not built into project reqs.
    """removes emojii(s?), random characters, etc. (anything other than a-z, A-Z, 
    0-9, #, characters ,'"&()?.:= and spaces)
    """
    #re.sub(pattern, replacement, string) format-> replacement is nothing
    #\ means " is taken as regular character like any other
    cleaned = re.sub(r"[^a-zA-Z0-9\s#,'\"&?().:=]", "", tweet)
    return(cleaned)

def pre_ceremony():
    '''Pre-processes and loads data for the Golden Globes analysis.
    
    This function should be called before any other functions to:
    - Load and process the tweet data from gg2013.json
    - Download required models (e.g., spaCy models)
    - Perform any initial data cleaning or preprocessing
    - Store processed data in files or database for later use
    
    This is the first function the TA will run when grading.
    
    Note:
        - Do NOT change the name of this function or what it returns
        - This function should handle all one-time setup tasks
        - Print progress messages to help with debugging
    '''
    #load tweets (or try)
    try:
        with open("gg2013.json", "r", encoding="utf-8") as f:
            unfiltered_tweets = json.load(f)
        print(f"{len(unfiltered_tweets)} tweets loaded!")

    except FileNotFoundError:
        print("file not found")
        return
    
    except json.JSONDecodeError:
        print("could not parse tweet file")
        return
    
    #pre-process tweets

    #clean tweets
    print("cleaning tweets")
    clean_tweets = []
    for tweet_obj in unfiltered_tweets:
        tweet = tweet_obj.get("text", "")
        clean_tweets.append(clean_tweet(tweet))
    print("tweets cleaned")

    #drop short tweets (<20 chars) (what can you really say in 20 chars?)
    print("dropping tweets that are too short/meaningless")
    long_enough_tweets = []
    for tweet in clean_tweets:
        if len(tweet) < 20:
            continue
        long_enough_tweets.append(tweet)
    print("shortest tweets dropped")
    print(f"{len(long_enough_tweets)} tweets left")

    """
    #this is commented out for now unless i figure out a way to make it take less time or 
    #we decide to filter/preprocess more tweets out because english detection is currently
    #taking like 40 mins ): and also most seem to be in english (just from eyeballing)
    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    #drop non-english
    print("filtering english tweets only")
    english_tweets = []
    tweet_count = 0
    for tweet in long_enough_tweets:
        #try to detect a language (english) 
        try:
            if detect(tweet) == "en":
                english_tweets.append(tweet)
                tweet_count += 1
                if ((tweet_count % 1000) == 0):
                    print("1000 tweets appended")
                    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except: #no lang detected (too short, couldn't tell, etc)
            continue

    print("non-english tweets removed")
    print(f"{len(english_tweets)} tweets left")
    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    """

    #saves in global var for use in other functions
    final_tweets = long_enough_tweets

    print("Pre-ceremony processing complete.")

    #did opt to keep duplicates, how many ways are there to say "someone wins 
    #best actor" if a bunch of people tweet that they probably did win

    #save to json
    processed_filename = f"{YEAR}_processed_tweets.json"

    try:
        with open(processed_filename, "w", encoding="utf-8") as f:
            json.dump(long_enough_tweets, f, indent=2)
            #json.dump(english_tweets, f, indent=2)
    except Exception as e:
        print("error:", e)

    print(f"processed tweets saved to {processed_filename}")
    return

def main():
    '''Main function that orchestrates the Golden Globes analysis.
    
    This function should:
    - Call pre_ceremony() to set up the environment
    - Run the main analysis pipeline
    - Generate and save results in the required JSON format
    - Print progress messages and final results
    
    Usage:
        - Command line: python gg_api.py
        - Python interpreter: import gg_api; gg_api.main()
    
    This is the second function the TA will run when grading.
    
    Note:
        - Do NOT change the name of this function or what it returns
        - This function should coordinate all the analysis steps
        - Make sure to handle errors gracefully
    '''
    # Your code here
    pre_ceremony()

    # initialize global event variable
    event = Event(name=NAME, year=YEAR, hosts=[], awards=[])
    
    #get hosts for event
    hosts = get_hosts(YEAR)


    return

if __name__ == '__main__':
    main()