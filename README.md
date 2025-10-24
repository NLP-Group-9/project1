#Project 1
python ver. 3.11.9
Github link: https://github.com/NLP-Group-9/project1

## Dependencies
This project requires the following Python packages:

- spacy
- vaderSentiment

Install them with:
pip install -r requirements.txt

Also install the following spacy model:
python -m spacy download en_core_web_sm

## Steps to run
1) Run gg_api.py with:
>python gg_api.py
This step runs the pre_ceremony() preprocessing function as well as all the get methods. Results are printed to terminal

2) Alternatively, you can import and call the specific get functions in other code files. However, you must call pre_ceremony() first before calling any of the get functions. This is an issue when running the autograder.py since it doesn't run pre_ceremony()


## Design Implementation
Here is a brief overview on how we implemented the get methods to find the appropriate answers. We also provide the extra get methods that are not part of the initial project requirements here as well.

1) get_awards

We filter out tweets that don't have win keywords = ["wins", "goes to", etc] as well as the keyword = "best". We also filter out tweets with trouble some keywords = ["for", "at", etc]. From that set of filtered tweets, we do a regex match on the best keyword as well as the win keywords in pre or post order. For example, we match on "best [AWARD_NAME] goes to" and "[___ wins best [AWARD_NAME]". We keep the top 26 most frequent award names and return that award name list.

Result: autograder gave {'2013': {'awards': {'completeness': 0.15454545454545454,
                     'spelling': 0.8162515828433672}}}

Our own checks however showed that we were able to get ~60% close matches with the ground truth award names due to minor changes in how the award name is structured and abbreviated.

2) get_hosts

We filter out tweets that don't mention host keywords = ["hosted by", "host", "hosts", etc]. From that set of filtered tweets, we then use the spaCy named recognition model to detect and extract any names (with len(name) >= 2, to accommodate for First, Middle, Last Names) in those tweets. From there we keep the top 2 most frequent host names.

Result: autograder and our own checks indicate 100% match.

3) get_best_dressed

We filter out tweets that don't mention host keywords = ["best_dressed"]. From that set of filtered tweets, we then use the spaCy named recognition model to detect and extract any names (with len(name) >= 2, to accommodate for First, Middle, Last Names) in those tweets. From there we keep the top 3 best dressed people.

Result: no autograder to run against

4) get_worst_dressed

We filter out tweets that don't mention host keywords = ["worst_dressed"]. From that set of filtered tweets, we then use the spaCy named recognition model to detect and extract any names (with len(name) >= 2, to accommodate for First, Middle, Last Names) in those tweets. From there we keep the top 3 worst dressed people.

Result: no autograder to run against

5) get_winner_sentiments

We filter out tweets that don't mention the winner names, as well win keywords. From there, we loop through all the winner names and filter tweets that only mention the winner names, getting an aggregate sentiment score from the VADER sentiment analysis library. Then for each winner, we'd have the sentiments to them winning that particular award.

Result: no autograder to run against





