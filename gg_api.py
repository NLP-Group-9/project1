'''Version 0.5'''
import json
import re
from data_structs import Event, Award, Nominee
from collections import Counter
import spacy
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#from datetime import datetime #for debugging only as of now
#from langdetect import detect
prepositions = ['the', 'a', 'an', 'of', 'at', 'in', 'on', 'for', 'to']

#name of ceremony
NAME = "The Golden Globes"
EVENT_NAME_LIST = [word.lower() for word in NAME.split() if word.lower() not in prepositions] #string list of event w/o prepositions

#number constants
NUM_HOSTS = 2
NUM_AWARDS = 26
NUM_BEST_DRESSED = 3
NUM_WORST_DRESSED = 3

# Year of the Golden Globes ceremony being analyzed
YEAR = "2013"

# Global variable to store the processed tweets
final_tweets = []

# Global variable to store the Event object
event = Event(name=NAME, year=YEAR, hosts=[], awards=[])

# Global variable for hardcoded award names
# This list is used by get_nominees(), get_winner(), and get_presenters() functions
# as the keys for their returned dictionaries
# Students should populate this list with the actual award categories for their year, to avoid cascading errors on outputs that depend on correctly extracting award names (e.g., nominees, presenters, winner)

#Correct Award Names
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

# Hardcoded winners for testing purposes to test get_winner_sentiment
OFFICIAL_WINNERS_2013 = {
    "best screenplay - motion picture": "django unchained",
    "best director - motion picture": "ben affleck",
    "best performance by an actress in a television series - comedy or musical": "lena dunham",
    "best foreign language film": "amour",
    "best performance by an actor in a supporting role in a motion picture": "christoph waltz",
    "best performance by an actress in a supporting role in a series, mini-series or motion picture made for television": "maggie smith",
    "best motion picture - comedy or musical": "les miserables",
    "best performance by an actress in a motion picture - comedy or musical": "jennifer lawrence",
    "best mini-series or motion picture made for television": "game change",
    "best original score - motion picture": "life of pi",
    "best performance by an actress in a television series - drama": "claire danes",
    "best performance by an actress in a motion picture - drama": "jessica chastain",
    "cecil b. demille award": "jodie foster",
    "best performance by an actor in a motion picture - comedy or musical": "hugh jackman",
    "best motion picture - drama": "argo",
    "best performance by an actor in a supporting role in a series, mini-series or motion picture made for television": "ed harris",
    "best performance by an actress in a supporting role in a motion picture": "anne hathaway",
    "best television series - drama": "homeland",
    "best performance by an actor in a mini-series or motion picture made for television": "kevin costner",
    "best performance by an actress in a mini-series or motion picture made for television": "julianne moore",
    "best animated feature film": "brave",
    "best original song - motion picture": "skyfall",
    "best performance by an actor in a motion picture - drama": "daniel day-lewis",
    "best television series - comedy or musical": "girls",
    "best performance by an actor in a television series - drama": "damian lewis",
    "best performance by an actor in a television series - comedy or musical": "don cheadle"
}

NOM_KEYWORDS = tuple(k.lower() for k in (
    'nominee', 'nominees', 'nominated', 'nomination', 'nominations',
    'noms', 'nom ', '#nominee', '#nominees', '#noms', 'up for',
    'contender', 'in the running', 'nominated for', 'is nominated',
    'was nominated', 'are nominated'
))
WIN_CUES = (
    ' wins ', ' win ', ' won ', ' winner', ' goes to ', ' awarded to ',
    'takes home', 'takes the', 'accepts the', 'accepting the',
    'picks up', 'snags the', 'claims the', 'collects the', 'earns the',
    'goes home with'
)
PRESENTER_CUES = (
    ' presenting ', ' presenter', ' presenters', ' presents ', ' presented by '
)
STOP_TERMS = {
    'golden globes', 'golden globe', 'goldenglobes', 'gg',
    'http', 'https', 't.co', 'best motion picture', 'best animated feature film'
}
FILLER = {
    'by', 'an', 'of', 'the', 'a', 'in', 'or', 'for', 'made',
    'best', 'award', 'category'
}
GENERIC_SINGLE = {
    'rt', 'tv', 'film', 'movie', 'picture', 'drama', 'comedy', 'musical',
    'director', 'actress', 'actor', 'performance', 'foreign', 'language',
    'song', 'score', 'nominee', 'nominees', 'nomination', 'oscars', 'oscar',
    'kudos', 'congrats', 'this', 'that', 'you', 'they', 'them', 'and', 'the',
    'love', 'all', 'outstanding animation', 'best', 'picture', 'series'
}
GENERIC_PHRASES = {
    'best actor', 'best actress', 'best picture', 'best performance',
    'best director', 'best song', 'best score', 'best original song',
    'best original score', 'best foreign language film',
    'best motion picture', 'best television series'
}
DISQUALIFY_SUBSTRINGS = {
    'best actress', 'best actor', 'best director', 'best tv', 'best picture',
    'best performance', 'best motion picture', 'best foreign language',
    'presenter', 'presenting', 'host', 'hosting', 'oscars', 'oscar',
    'golden globe', 'golden globes', 'rt', 'tv series', 'tv show',
    'best original score', 'best original song', 'best song', 'http'
}


def normalize_candidate_text(text):
    if not isinstance(text, str):
        return ""
    cleaned = text.strip(" ,.:;!?'\"-").strip()
    cleaned = cleaned.replace('#', '').replace('@', '')
    return cleaned


def is_generic_candidate(text):
    candidate = normalize_candidate_text(text)
    if not candidate:
        return True
    lower = candidate.lower()
    normalized = re.sub(r'[^a-z0-9 ]+', '', lower).strip()
    if not normalized:
        return True
    if lower.startswith('rt ') or lower.startswith('@'):
        return True
    if lower.startswith('best '):
        return True
    if any(term in lower for term in STOP_TERMS):
        return True
    if any(term in lower for term in DISQUALIFY_SUBSTRINGS):
        return True
    if normalized in GENERIC_SINGLE:
        return True
    if normalized in GENERIC_PHRASES:
        return True
    if any(phrase in lower for phrase in GENERIC_PHRASES):
        return True
    if len(normalized) <= 3 and ' ' not in normalized:
        return True
    return False


def expect_person(award):
    a = award.lower()
    if 'cecil b. demille' in a:
        return True
    if any(term in a for term in ('screenplay', 'score', 'song', 'motion picture', 'film', 'television series', 'mini-series', 'mini series')):
        return False
    return True


def award_tokens(award):
    cleaned = award.lower().replace('-', ' ')
    words = [w for w in re.findall(r'[a-z]+', cleaned) if w not in FILLER]
    tokens = set(words)

    for size in (2, 3):
        for i in range(len(words) - size + 1):
            phrase = ' '.join(words[i:i+size])
            if phrase and not phrase.startswith('best '):
                tokens.add(phrase)

    if 'television' in words or 'tv' in words:
        tokens |= {'television', 'tv', 'television series', 'tv series'}
    if 'series' in words:
        tokens.add('show')
    if 'motion' in words and 'picture' in words:
        tokens |= {'motion picture', 'movie', 'film'}
    if 'mini' in words or 'miniseries' in words or ('series' in words and 'mini' in words):
        tokens |= {'mini series', 'mini-series', 'miniseries'}
    if 'comedy' in words and 'musical' in words:
        tokens.add('comedy or musical')

    return tokens, max(1, len(words))


def required_token_hits(word_count):
    if word_count <= 3:
        return 1
    if word_count <= 6:
        return 2
    return 3


def award_context(award):
    a = award.lower()
    ctx = set()
    if 'director' in a:
        ctx |= {'director', 'directing'}
    if 'screenplay' in a:
        ctx |= {'screenplay', 'writing', 'writer'}
    if 'song' in a:
        ctx |= {'song', 'original song', 'music'}
    if 'score' in a:
        ctx |= {'score', 'composer'}
    if 'foreign language' in a:
        ctx |= {'foreign', 'language'}
    if 'animated' in a:
        ctx.add('animated')
    if 'television series' in a:
        ctx |= {'series', 'tv', 'show'}
    if 'motion picture' in a:
        ctx |= {'film', 'movie'}
    return ctx


def award_signatures(award):
    a = award.lower()
    signatures = set()

    def add(term, *synonyms):
        signatures.add(term)
        for syn in synonyms:
            signatures.add(syn)

    if 'drama' in a:
        add('drama', 'dramatic')
    if 'comedy' in a:
        add('comedy')
    if 'musical' in a:
        add('musical')
    if 'supporting' in a:
        add('supporting')
    if 'mini-series' in a or 'mini series' in a or 'miniseries' in a:
        add('mini-series', 'miniseries')
    if 'television series' in a:
        add('television series', 'tv series', 'tv')
    if 'motion picture' in a:
        add('motion picture', 'film', 'movie')
    if 'screenplay' in a:
        add('screenplay', 'writing')
    if 'song' in a:
        add('song')
    if 'score' in a:
        add('score')
    if 'foreign language' in a:
        add('foreign language', 'foreign')
    if 'animated' in a:
        add('animated', 'animation')
    if 'actor' in a:
        add('actor')
    if 'actress' in a:
        add('actress')
    if 'director' in a:
        add('director')
    return signatures


def must_terms(award):
    need = []
    al = award.lower()
    if 'actor' in al:
        need.append('actor')
    if 'actress' in al:
        need.append('actress')
    return need


def award_match_score(text_lower, helper):
    tokens = helper["tokens"]
    contexts = helper["contexts"]
    required_terms = helper["requires"]
    min_hits = helper["min_hits"]
    signatures = helper["signature_terms"]

    if required_terms and not any(term in text_lower for term in required_terms):
        return 0

    token_hits = sum(1 for tok in tokens if tok and tok in text_lower)
    if token_hits < min_hits:
        return 0
    if contexts and not any(ctx in text_lower for ctx in contexts):
        return 0
    if signatures and not any(sig in text_lower for sig in signatures):
        return 0
    return token_hits + 0.5 * sum(1 for ctx in contexts if ctx in text_lower)


def clean_candidate(text, want_person):
    if not text:
        return None
    candidate = normalize_candidate_text(text)
    words = candidate.split()
    lead_trash = {
        'are', 'is', 'was', 'were', 'be', 'being', 'been', 'nominees', 'nominee',
        'best', 'motion', 'picture', 'drama', 'comedy', 'musical', 'television',
        'series', 'actor', 'actress', 'original', 'song', 'score', 'foreign',
        'language', 'mini-series', 'mini', 'film', 'movie', 'tv', 'rt', 'presenter',
        'presenting', 'host', 'hosting'
    }
    while words and words[0].lower() in lead_trash:
        words = words[1:]
    candidate = ' '.join(words)
    if not candidate:
        return None
    if is_generic_candidate(candidate):
        return None
    if len(candidate) <= 2 or not any(ch.isalpha() for ch in candidate):
        return None
    if len(candidate.split()) == 1 and len(candidate) <= 3:
        return None
    if want_person:
        tokens = candidate.split()
        while tokens and tokens[-1].isupper() and len(tokens[-1]) > 3:
            tokens.pop()
        if len(tokens) < 2 or len(tokens) > 4:
            return None
        if not all(re.search(r"[a-zA-Z]", tok) for tok in tokens):
            return None
        candidate = ' '.join(tokens)
    else:
        if len(candidate.split()) > 6:
            return None
    return candidate


def candidate_has_context(segment_lower, candidate_lower, helper, keyword_triggers, window=60):
    idx = segment_lower.find(candidate_lower)
    if idx == -1:
        return False
    start = max(0, idx - window)
    end = min(len(segment_lower), idx + len(candidate_lower) + window)
    window_text = segment_lower[start:end]
    token_hits = sum(1 for tok in helper["tokens"] if tok in window_text)
    if token_hits < max(1, helper["min_hits"] - 1):
        return False
    if helper["contexts"] and not any(ctx in window_text for ctx in helper["contexts"]):
        return False
    if helper["requires"] and not any(req in window_text for req in helper["requires"]):
        return False
    if helper["signature_terms"] and not any(sig in window_text for sig in helper["signature_terms"]):
        return False
    if keyword_triggers and not any(keyword in window_text for keyword in keyword_triggers):
        return False
    return True


def build_award_helpers():
    helpers = {}
    for award in AWARD_NAMES:
        tok_info = award_tokens(award)
        min_hits = required_token_hits(tok_info[1])
        helpers[award] = {
            "tokens": tok_info[0],
            "contexts": award_context(award),
            "requires": must_terms(award),
            "want_person": expect_person(award),
            "min_hits": min_hits,
            "signature_terms": award_signatures(award)
        }
    return helpers


#sentence similarity scores
def similarity_score(s1, s2):
    words_1 = set(s1.split())
    words_2 = set(s2.split())

    intersection = words_1.intersection(words_2)
    union = words_1.union(words_2)

    score = len(intersection) / len(union) if union else 0
    return score

#group sentences that are similar based on thres
def similar_groups(sentences, dict_counts, thres = 0.95):
    groups = []
    used = []

    #For each sentence pair, get similarity score then group if above thres
    for i, sentence_1 in enumerate(sentences):
        if i in used:
            continue

        group = [sentence_1]
        used.append(i)

        for j, sentence_2 in enumerate(sentences[i+1:], start=i+1):
            if j in used:
                continue
                
            if similarity_score(sentence_1, sentence_2) >= thres:
                group.append(sentence_2)
                used.append(j)
        
        #select one candidate sentence to represent entire group according to max len
        candidate = max(group, key=len)
        total_count = sum(dict_counts[sentence] for sentence in group)
        groups.append((candidate, total_count))

    return groups


def get_best_dressed(year):
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
    # using spacy for Recognizing First Names and Last Names
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("spacy model not downloaded, run: python -m spacy download en_core_web_sm")
        return []
    
    #filter to tweets that only have host keywords
    keywords = ['best dressed']
    #keywords to throw out irrelevant tweets
    keywords_to_throw = ['rt']
    filtered_tweets = []

    for tweet in final_tweets:
        if any(keyword in tweet.lower() for keyword in keywords):
            if not any(bad_keyword in tweet.lower() for bad_keyword in keywords_to_throw):
                filtered_tweets.append(tweet)
    print(rf"# of Tweets with best dressed keywords: {len(filtered_tweets)} tweets")

    best_dressed_names = []

    #Test print for best dressed tweets
    # for i, tweet in enumerate(filtered_tweets, start=1):
    #     print(f"{i}. {tweet}")
    #     print()
    #     pass

    for tweet in filtered_tweets:
        doc = nlp(tweet)
        for ent in doc.ents:
            if ent.label_ == "PERSON":         #only get the Person labels
                name = ent.text.strip()
                word_count = len(name.split())
                if 2 <= word_count <= 3:      #keep names with 2 to 3 words (First, Middle, Last Names)
                    best_dressed_names.append(name)

    best_dressed_counts = Counter(best_dressed_names)

    #Filters out event name from the final answer like "Golden Globes"
    filtered_counts = {
        name: count for name, count in best_dressed_counts.items()
        if not any(event_word in name.lower() for event_word in EVENT_NAME_LIST)
    }

    #extract only top NUM_BEST_DRESSED names
    best_dressed = [name for name, count in Counter(filtered_counts).most_common(NUM_BEST_DRESSED)]

    return best_dressed

def get_worst_dressed(year):
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
    # using spacy for Recognizing First Names and Last Names
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("spacy model not downloaded, run: python -m spacy download en_core_web_sm")
        return []
    
    #filter to tweets that only have host keywords
    keywords = ['worst dressed']
    #keywords to throw out irrelevant tweets
    keywords_to_throw = ['rt']
    filtered_tweets = []

    for tweet in final_tweets:
        if any(keyword in tweet.lower() for keyword in keywords):
            if not any(bad_keyword in tweet.lower() for bad_keyword in keywords_to_throw):
                filtered_tweets.append(tweet)
    print(rf"# of Tweets with worst dressed keywords: {len(filtered_tweets)} tweets")

    #Test print for worst dressed tweets
    # for i, tweet in enumerate(filtered_tweets, start=1):
    #     print(f"{i}. {tweet}")
    #     print()
    #     pass

    worst_dressed_names = []

    for tweet in filtered_tweets:
        doc = nlp(tweet)
        for ent in doc.ents:
            if ent.label_ == "PERSON":         #only get the Person labels
                name = ent.text.strip()
                word_count = len(name.split())
                if 2 <= word_count <= 3:      #keep names with 2 to 3 words (First, Middle, Last Names)
                    worst_dressed_names.append(name)

    worst_dressed_counts = Counter(worst_dressed_names)

    #Filters out event name from the final answer like "Golden Globes"
    filtered_counts = {
        name: count for name, count in worst_dressed_counts.items()
        if not any(event_word in name.lower() for event_word in EVENT_NAME_LIST)
    }

    #extract only top NUM_WORST_DRESSED names
    worst_dressed = [name for name, count in Counter(filtered_counts).most_common(NUM_WORST_DRESSED)]

    return worst_dressed

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
    # using spacy for Recognizing First Names and Last Names
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("spacy model not downloaded, run: python -m spacy download en_core_web_sm")
        return []
    
    #filter to tweets that only have host keywords
    keywords = ['hosting the', 'host the', 'hosts the', 'are hosting', 'co-host']
    #keywords to throw out irrelevant tweets
    keywords_to_throw = ['next year', 'should', 'could', 'next', 'future']
    filtered_tweets = []

    for tweet in final_tweets:
        if any(keyword in tweet.lower() for keyword in keywords):
            if not any(bad_keyword in tweet.lower() for bad_keyword in keywords_to_throw):
                filtered_tweets.append(tweet)
    print(rf"# of Tweets with host keywords: {len(filtered_tweets)} tweets")

    host_names = []

    for tweet in filtered_tweets:
        doc = nlp(tweet)
        for ent in doc.ents:
            if ent.label_ == "PERSON":         #only get the Person labels
                name = ent.text.strip()
                word_count = len(name.split())
                if 2 <= word_count <= 3:      #keep names with 2 to 3 words (First, Middle, Last Names)
                    host_names.append(name)

    host_counts = Counter(host_names)

    #extract only top NUM_HOSTS names
    hosts = [name for name, count in host_counts.most_common(NUM_HOSTS)]

    #update the EVENT global variable with the hosts
    event.hosts = hosts

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
    #pre_ceremony()
    # Your code here
    primary_keyword = 'best'
    pre_keywords = ['wins', 'won', 'winner', 'winning', 'awarded', 'is awarded to']
    post_keywords = ['goes to', 'went to']
    troublesome_keywords = ['for', 'at', 'at the', 'at ' + NAME, 'at ' + NAME.lower(), NAME.lower(), NAME, 'http'] + EVENT_NAME_LIST #we will filter these out
    secondary_keywords = pre_keywords + post_keywords

    # goes through each tweet to see if primary_keywords AND at least one of secondary keywords is present
    award_tweets = []
    for tweet in final_tweets:
        tweet_lower = tweet.lower()
        if primary_keyword in tweet_lower and any(keyword in tweet_lower for keyword in secondary_keywords):
            award_tweets.append(tweet)

    print(rf"Potential # of award name tweets: {len(award_tweets)}")

    # Print all filtered tweets
    # for i, tweet in enumerate(award_tweets, start=1):
    #     print(f"{i}. {tweet}")
    #     print()
    #     pass

    awards = []

    #Extract award names from filtered tweets
    for tweet in award_tweets:
        tweet_lower = tweet.lower()

        #analyze pre keywords, i.e [wins] Best Movie
        for pre_keyword in pre_keywords:
            if pre_keyword in tweet_lower:
                pre_idx = tweet_lower.find(pre_keyword)
                after_pre = tweet_lower[pre_idx + len(pre_keyword):].strip()
                
                if after_pre.startswith(primary_keyword):  # Check if starts with 'best'
                    pattern = rf'{primary_keyword}(?:\s+[a-z\-]+){{1,15}}'
                    matches = re.findall(pattern, after_pre)
                    awards.extend([m.strip() for m in matches])
        
        #analyze post keywords, i.e Best Movie [goes to]
        for post_keyword in post_keywords:
            if post_keyword in tweet_lower:
                post_idx = tweet_lower.find(post_keyword)
                before_post = tweet_lower[:post_idx].strip()
                
                pattern = rf'{primary_keyword}(?:\s+[a-z\-]+){{1,15}}'
                matches = re.findall(pattern, before_post)
                awards.extend([m.strip() for m in matches])
    
    filtered_awards = []
    #clean the awards from troublesome_keywords
    for award in awards:
        pattern = r'\s+(' + '|'.join(troublesome_keywords) + ')$'
        cleaned = re.sub(pattern, '', award)
        #remove for and trailing words after
        cleaned = re.sub(r'\s+for\s+(?:\w+\s*){1,10}$', '', cleaned)
        cleaned = ' '.join(cleaned.split())
        filtered_awards.append(cleaned)

    awards = filtered_awards

    award_counts = Counter(awards)

    #group similar award names
    award_names = list(award_counts.keys())
    grouped_awards = similar_groups(award_names, award_counts, thres=0.78)
    merged_counts = {award: count for award, count in grouped_awards}
    award_counts = Counter(merged_counts)

    #Filter to award names >= 4 words
    awards = [award for award, count in award_counts.most_common(100) if count > 1 and len(award.split()) >= 4]
    
    #Gets top NUM_AWARDS
    awards = awards[:NUM_AWARDS]
    
    # print(f"\nTop awards found:")
    # for i, (award, count) in enumerate(award_counts.most_common(100), 1):
    #     print(f"{i}. {award}: {count}")

    return awards

def get_nominees(year):
    '''Returns the nominees for each award category (generalized across years).'''
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("spacy model not downloaded, run: python -m spacy download en_core_web_sm")
        return {award: [] for award in AWARD_NAMES}

    # --- local helpers (kept inside to avoid global clutter) ---
    NOM_CUES = ('nominee', 'nominees', 'nominated', 'nomination', 'noms')
    STOP_TERMS = {
        # event/org chatter & links (year-agnostic)
        'golden globes', 'goldenglobes', 'golden globe', 'globes', 'gg',
        'oscars', 'oscar', 'academy', 'academy awards', 'hfpa',
        't.co', 'http', 'https'
    }
    AWARD_FRAG = {
        'best','actor','actress','supporting','drama','comedy','musical','television','tv',
        'series','motion','picture','film','foreign','language','animated','original','score',
        'song','mini','miniseries','cecil','demille','award','director','screenplay'
    }

    def expect_person(award: str) -> bool:
        a = award.lower()
        if 'cecil b. demille' in a: return True
        if 'original score' in a:   return True  # often a composer (PERSON)
        return any(w in a for w in (
            'actor','actress','supporting','mini-series','television series','made for television'
        ))

    def award_tokens(award: str) -> set:
        toks = [w for w in award.lower().replace('-', ' ').split()
                if w not in {'by','an','of','the','a','in','or'}]
        if 'television' in toks: toks.append('tv')
        if 'series' in toks: toks.append('show')
        if 'motion' in toks and 'picture' in toks: toks += ['movie','film']
        return set(toks)

    def award_context_words(award: str) -> set:
        a = award.lower()
        ctx = set()
        if 'director' in a: ctx |= {'director','directing'}
        if 'screenplay' in a: ctx |= {'screenplay','writing','writer'}
        if 'song' in a: ctx |= {'song','original song','music'}
        if 'score' in a: ctx |= {'score','composer','music'}
        if 'animated' in a: ctx |= {'animated','animation'}
        if 'foreign language' in a: ctx |= {'foreign','language'}
        if 'television series' in a: ctx |= {'series','tv','show'}
        if 'motion picture' in a: ctx |= {'motion picture','film','movie'}
        return ctx

    def mentions_award(tw_lower: str, toks: set, ctx: set) -> bool:
        tl = tw_lower.replace('-', ' ').replace('&', 'and')
        token_hit = sum(1 for t in toks if t in tl) >= 2
        ctx_hit = any(c in tl for c in ctx) if ctx else True
        return token_hit and ctx_hit

    def clean_candidate(s: str) -> str | None:
        s = s.strip(" '.,:;!?")
        if not s:
            return None
        low = s.lower()
        if low.startswith('rt ') or s.startswith('@') or ' rt ' in low:
            return None
        if any(low == st or low.startswith(st) for st in STOP_TERMS):
            return None
        if all(w in AWARD_FRAG for w in low.split()):
            return None
        return s

    def extract_candidates(text: str, want_person: bool):
        # Prefer quoted titles for WORK
        quoted = [m.group(1).strip() for m in re.finditer(r'["“]([^"”]{3,80})["”]', text)]
        doc = nlp(text)

        if want_person:
            ents = [e.text for e in doc.ents if e.label_ == 'PERSON']
        else:
            ents = quoted + [e.text for e in doc.ents if e.label_ in {'WORK_OF_ART','EVENT','ORG'}]
            # fallback: multi-word TitleCase spans
            ents += [m.group(1) for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,6})\b', text)]

        out, seen = [], set()
        for raw in ents:
            c = clean_candidate(raw or '')
            if not c:
                continue
            # shape constraints
            if want_person and len(c.split()) < 2:
                continue  # require First Last
            if not want_person and len(c.split()) < 2:
                continue  # avoid single “The”, “You”, etc.
            low = c.lower()
            if low in seen:
                continue
            seen.add(low)
            out.append(c)
        return out

    # --- main logic ---
    nom_tweets = [tw for tw in final_tweets if any(c in tw.lower() for c in NOM_CUES)]
    print(rf"# of Tweets with nominee cues: {len(nom_tweets)}")

    nominees = {award: [] for award in AWARD_NAMES}
    counts = {award: Counter() for award in AWARD_NAMES}

    for award in AWARD_NAMES:
        want_person = expect_person(award)
        toks = award_tokens(award)
        ctx = award_context_words(award)

        for tw in nom_tweets:
            tl = tw.lower()
            if not mentions_award(tl, toks, ctx):
                continue
            cands = extract_candidates(tw, want_person)
            # list-like phrasing gets a small boost
            weight = 2 if ('nominee' in tl or 'nominees' in tl or ',' in tw or ' and ' in tw or ' & ' in tw) else 1
            for c in cands:
                counts[award][c] += weight

        # take the top 5 plausible nominees
        nominees[award] = [c for c, _ in counts[award].most_common(12)][:5]

    return nominees

def get_winner(year):
    '''Infers award winners from tweets using NLP and win-keyword heuristics.'''
    if not final_tweets:
        pre_ceremony()

    results_path = f"results_{year}.json"
    default_winners = {award: "" for award in AWARD_NAMES}

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("spacy model not downloaded, run: python -m spacy download en_core_web_sm")
        return default_winners

    if not final_tweets:
        return default_winners

    nominees_by_award = get_nominees(year)
    award_helpers = build_award_helpers()

    EXCLUDE_PHRASES = ('nominee', 'nominees', 'nominated', 'nomination', 'presenting', 'presents', 'host', 'hosting', 'red carpet')
    WIN_REGEX = re.compile(
        r'\b(?:wins?|won|winner|goes to|awarded to|takes home|takes the|picks up|snags the|claims the|earns the|goes home with|accepts the|accepting the)\b'
    )
    PATTERN_REGEXES = [
        re.compile(r'(?:wins?|won|takes home|takes the|picks up|snags the|claims the|collects the|earns the|accepts the|accepting the)\s+([^.!?\n]{3,80})', re.IGNORECASE),
        re.compile(r'(?:goes to|awarded to|goes home with)\s+([^.!?\n]{3,80})', re.IGNORECASE),
        re.compile(r'(?:winner is|winner:)\s+([^.!?\n]{3,80})', re.IGNORECASE)
    ]

    def find_segments(tweet):
        lower = tweet.lower()
        segments = []
        for match in re.finditer(r'\bbest\b', lower):
            start = max(0, match.start() - 60)
            end = min(len(tweet), match.end() + 220)
            window = tweet[start:end]
            window_lower = lower[start:end]
            if WIN_REGEX.search(window_lower):
                segments.append((window, window_lower))
        if not segments:
            for match in WIN_REGEX.finditer(lower):
                start = max(0, match.start() - 80)
                end = min(len(tweet), match.end() + 160)
                window = tweet[start:end]
                window_lower = lower[start:end]
                segments.append((window, window_lower))
        if not segments and WIN_REGEX.search(lower):
            segments.append((tweet, lower))
        return segments

    def pattern_candidates(segment):
        results = []
        for regex in PATTERN_REGEXES:
            for match in regex.finditer(segment):
                chunk = match.group(1).strip()
                chunk = re.split(r'(?:\s+for\s+|\s+at\s+|\s+-\s+)', chunk)[0]
                chunk = chunk.split(',')[0]
                chunk = chunk.strip(" .,:;!?")
                if chunk:
                    results.append(chunk)
        return results

    def extract_winner_candidates(segment, segment_lower, helper, nominees):
        candidates = []
        for nominee in nominees:
            if not nominee:
                continue
            if nominee.lower() in segment_lower:
                candidates.append(nominee)
        candidates.extend(pattern_candidates(segment))

        doc = nlp(segment)
        if helper["want_person"]:
            ents = [e.text for e in doc.ents if e.label_ == 'PERSON']
        else:
            ents = [e.text for e in doc.ents if e.label_ in {'WORK_OF_ART', 'EVENT', 'ORG'}]
        candidates.extend(ents)

        filtered = []
        seen = set()
        for raw in candidates:
            cleaned = clean_candidate(raw, helper["want_person"])
            if not cleaned:
                continue
            lowered = cleaned.lower()
            if lowered in seen:
                continue
            if not candidate_has_context(segment_lower, lowered, helper, WIN_CUES, window=90):
                continue
            seen.add(lowered)
            filtered.append(cleaned)
        return filtered

    winner_votes = {award: Counter() for award in AWARD_NAMES}

    for tweet in final_tweets:
        lower = tweet.lower()
        if not WIN_REGEX.search(lower):
            continue
        if any(bad in lower for bad in EXCLUDE_PHRASES):
            continue

        segments = find_segments(tweet)
        if not segments:
            continue

        weight = 1.0
        if lower.strip().startswith('rt '):
            weight -= 0.25
        if tweet.count('!') >= 2:
            weight += 0.1
        weight = max(0.2, weight)

        for segment, segment_lower in segments:
            award_scores = []
            for award, helper in award_helpers.items():
                score = award_match_score(segment_lower, helper)
                if score > 0:
                    award_scores.append((score, award, helper))
            if not award_scores:
                continue
            award_scores.sort(key=lambda x: x[0], reverse=True)
            top_score = award_scores[0][0]
            selected = []
            for score, award, helper in award_scores:
                if score < max(1.0, top_score - 0.8):
                    continue
                selected.append((award, helper))
                if len(selected) == 3:
                    break

            for award, helper in selected:
                nominees = nominees_by_award.get(award, [])
                candidates = extract_winner_candidates(segment, segment_lower, helper, nominees)
                seen = set()
                for cand in candidates:
                    key = cand.lower()
                    if key in seen:
                        continue
                    winner_votes[award][cand] += weight
                    seen.add(key)

    final_winners = {}
    for award in AWARD_NAMES:
        counts = winner_votes[award]
        if counts:
            final_winners[award] = counts.most_common(1)[0][0]
        else:
            final_winners[award] = ""

    return final_winners



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
       # using spacy for Recognizing First Names and Last Names
   try:
       nlp = spacy.load("en_core_web_sm")
   except OSError:
       print("spacy model not downloaded, run: python -m spacy download en_core_web_sm")
       return []
  
   all_nominees = get_nominees(year)
   all_winners = get_winner(year)
  
   #filter to tweets that only have host keywords
   keywords = ['presenting the', 'present the', 'presents the', 'are presenting', \
               'presenters', 'presents', 'presented by', 'presented', 'present']
   #keywords to throw out irrelevant tweets
   keywords_to_throw = ['next year', 'last year', 'should', 'could', 'next', 'future' \
                        'past', 'previous', 'last', 'former']
   filtered_tweets = []


   for tweet in final_tweets:
       if any(keyword in tweet.lower() for keyword in keywords):
           if not any(bad_keyword in tweet.lower() for bad_keyword in keywords_to_throw):
               filtered_tweets.append(tweet)


   print(rf"# of Tweets with presenter keywords: {len(filtered_tweets)} tweets")


   #actual award name: [presenter names]
   potential_presenters = {}
   presenters = {}


   #for each award name make a list of words that would refer to it
   for award in AWARD_NAMES:
       #nominees = all_nominees[award]
       winner = all_winners[award]


       potential_presenters[award] = []
       #make a list of keywords for each award name
       award_lower = award.lower()
       #filler words
       award_keywords = [w for w in award_lower.split() \
                         if w not in {'by', 'an', 'of', '-', 'the', 'a', 'in', 'or', \
                                      'performance', 'made', 'for'}]
       #add some common alternates/abbreviations
       if 'television' in award_keywords:
           award_keywords.append('tv')
       if 'series' in award_keywords:
           award_keywords.append('show')
       if ('motion' in award_keywords) and ('picture' in award_keywords):
           award_keywords.append('movie')
           award_keywords.append('film')


    
       for tweet in filtered_tweets:
           must_have = []
           if "actor" in award_lower:
               must_have.append("actor")
           if "actress" in award_lower:
               must_have.append("actress")
           tweet_lower = tweet.lower()
           #make sure gender of recipient matches award (if applicable)
           #this is because many awards are
           if must_have and not any(w in tweet_lower for w in must_have):
               continue
           #remove tweets containting "RT" (retweets)
           if 'rt ' in tweet_lower:
               continue
           tweet_len = len(tweet_lower)
           num_keywords_found = 0
           for word in award_keywords:
               if word in tweet_lower:
                   num_keywords_found += 1

           #if at least half the award keywords are found in tweet
           if num_keywords_found >= ((len(award_keywords) / 2)):

               doc = nlp(tweet)
               for ent in doc.ents:
                   if (ent.text.strip() != winner): #not in nominees) and (ent.text.strip() != winner):
                       if ent.label_ == "PERSON":         #only get the Person labels
                           name = ent.text.strip()
                           word_count = len(name.split())
                           if 2 <= word_count <= 3:      #keep names with 2 to 3 words (First, Middle, Last Names)
                               potential_presenters[award].append(name)


       #set presenters for award to most common 2 names found in potential presenters
       name_counts = Counter(potential_presenters[award])
       most_common_name = name_counts.most_common(2)
       presenters[award] = [name for name, _ in most_common_name]
      
       print(f"presenters found for {award}: {presenters[award]}\n")


   return(presenters)

def get_winner_sentiments(year):
    '''
    Returns the general sentiment to a winner winning an award
    
    Returns dictionary key = [award name, winner] and value = sentiment score
    return sentiment_dict = {[award name, winner]: sentiment score}
    '''

    #winner_dict = get_winner(year)
    winner_dict = OFFICIAL_WINNERS_2013 #using official winners for testing since get_winner doesn't have 100% accucracy yet
    sentiment_dict = {}

    #Init keys of sentiment_dict with keys = [award name, winner] and value (sentiment score) = 0
    for award in AWARD_NAMES:
        winner = winner_dict.get(award, "")
        sentiment_dict[(award, winner)] = 0.0


    win_keywords = ['wins', 'win', 'won', 'winner', 'winning', 'awarded', 'is awarded to', 'goes to', 'went to']
    winner_list = [winner for winner in winner_dict.values() if winner]

    #filter tweets that only mention winner name and win keywords
    filtered_tweets = []

    #filter tweets that mention any winner and any win keyword
    for tweet in final_tweets:
        tweet_lower = tweet.lower()
        if any(winner.lower() in tweet_lower for winner in winner_list):
            if any(win_keyword in tweet_lower for win_keyword in win_keywords):
                filtered_tweets.append(tweet)

    print(rf"Number of Tweets with winner and win keywords: {len(filtered_tweets)} tweets")

    #Print all filtered tweets for TESTING
    # for i, tweet in enumerate(filtered_tweets, start=1):
    #     print(f"{i}. {tweet}")
    #     print()
    #     pass

    #initialize vader sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    #go through each award, winner pair in sentiment_dict
    for (award, winner) in sentiment_dict.keys():
        total_sentiment = 0.0
        count = 0

        for tweet in filtered_tweets:
            tweet_lower = tweet.lower()
            if winner.lower() in tweet_lower:
                #sentiment from vader
                sentiment_score = analyzer.polarity_scores(tweet)['compound']
                total_sentiment += sentiment_score
                count += 1

        #average sentiment for that award, winner pair
        final_sentiment = total_sentiment / count if count > 0 else 0.0

        #Converts number final sentiment to a human readable string
        if final_sentiment >= 0.65:
            sentiment_dict[(award, winner)] = "POSITIVE"
        elif final_sentiment < 0.65 and final_sentiment > 0.45:
            sentiment_dict[(award, winner)] = "NEUTRAL"
        else:
            sentiment_dict[(award, winner)] = "NEGATIVE"
    return sentiment_dict

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
    global final_tweets

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

    #remove duplicate text tweets
    long_enough_tweets = list(set(long_enough_tweets))

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


    pre_ceremony()

    #get hosts for event
    hosts = get_hosts(YEAR)
    print(rf"Hosts: {hosts}")

    # #get awards
    awards = get_awards(YEAR)
    print(rf"Awards: {awards}")

    nominees = get_nominees(YEAR)
    print(nominees)

    winner = get_winner(YEAR)
    print(winner)

    presenters = get_presenters(YEAR)
    print(presenters)

    #presenters = get_presenters(YEAR)
    ##print(rf"Presenters: {presenters}")

    #get best dressed
    best_dressed = get_best_dressed(YEAR)
    print(rf"Best Dressed: {best_dressed}")

    #get best dressed
    worst_dressed = get_worst_dressed(YEAR)
    print(rf"Worst Dressed: {worst_dressed}")

    #print sentiment scores for winners
    # sentiment_scores = get_winner_sentiments(YEAR)
    # print(sentiment_scores)

    #json formatted
    results = {
        "ceremony": {
            "name": NAME,
            "year": YEAR
        },
        "hosts": hosts,
        "awards": awards,
        "award_data": {
            "nominees": nominees,
            "winners": winner,
            "presenters": presenters
        },
        "best_dressed": best_dressed,
        "worst_dressed": worst_dressed,
        "winner_sentiments": {
            f"{award} - {winner_name}": sentiment
            for (award, winner_name), sentiment in sentiment_scores.items()
        }
    }

    #print json results to terminal
    print("\n" + "="*80)
    print("FINAL RESULTS:")
    print("="*80)
    print(json.dumps(results, indent=2))
    print("="*80 + "\n")

    #Save JSON to result file
    output_filename = f"gg{YEAR}_results.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results successfully saved to {output_filename}")
    except Exception as e:
        print(f"Error saving results to file: {e}")

if __name__ == '__main__':
    #start timer
    start = time.time()

    main() #main run

    #end timer
    end = time.time()
    time = (end - start) / 60
    print(rf"Time taken to run: {time} minutes")
