'''Version 0.5'''
import json
import re
from data_structs import Event, Award, Nominee
from collections import Counter
import spacy
import time

#from datetime import datetime #for debugging only as of now
#from langdetect import detect
prepositions = ['the', 'a', 'an', 'of', 'at', 'in', 'on', 'for', 'to']

#name of ceremony
NAME = "The Golden Globes"
EVENT_NAME_LIST = [word.lower() for word in NAME.split() if word.lower() not in prepositions] #string list of event w/o prepositions

#number of hosts
NUM_HOSTS = 2
NUM_AWARDS = 26
NUM_BEST_DRESSED = 5

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
    keywords_to_throw = []
    filtered_tweets = []

    for tweet in final_tweets:
        if any(keyword in tweet.lower() for keyword in keywords):
            if not any(bad_keyword in tweet.lower() for bad_keyword in keywords_to_throw):
                filtered_tweets.append(tweet)
    print(rf"# of Tweets with best dressed keywords: {len(filtered_tweets)} tweets")

    best_dressed_names = []

    for tweet in filtered_tweets:
        doc = nlp(tweet)
        for ent in doc.ents:
            if ent.label_ == "PERSON":         #only get the Person labels
                name = ent.text.strip()
                word_count = len(name.split())
                if 2 <= word_count <= 3:      #keep names with 2 to 3 words (First, Middle, Last Names)
                    best_dressed_names.append(name)

    best_dressed_counts = Counter(best_dressed_names)

    #extract only top NUM_BEST_DRESSED names
    best_dressed = [name for name, count in best_dressed_counts.most_common(NUM_BEST_DRESSED)]

    return best_dressed

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
    for i, tweet in enumerate(award_tweets, start=1):
        #print(f"{i}. {tweet}")
        #print()
        pass

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
    
    print(f"\nTop awards found:")
    for i, (award, count) in enumerate(award_counts.most_common(100), 1):
        print(f"{i}. {award}: {count}")

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
    '''Returns the winner for each award category (generalized across years).'''
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("spacy model not downloaded, run: python -m spacy download en_core_web_sm")
        return {award: "" for award in AWARD_NAMES}

    # --- local helpers (kept inside to avoid global clutter) ---
    WIN_CUES = (' wins ', ' won ', ' goes to ', ' went to ', ' awarded to ', ' award goes to ')
    STOP_TERMS = {
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
        if 'original score' in a:   return True
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
        cue_hit = any(c.strip() in tl for c in WIN_CUES)
        return token_hit and ctx_hit and cue_hit

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

    def first_after_cue_segment(text: str) -> str | None:
        tl = text.lower()
        for cue in WIN_CUES:
            i = tl.find(cue)
            if i != -1:
                seg = text[i + len(cue):]
                cut = re.split(r'[.!?\n]| via | http', seg, maxsplit=1)
                return cut[0][:160]
        return None

    def pick_from_segment(seg: str, want_person: bool) -> str | None:
        # Prefer quoted WORK
        if not want_person:
            m = re.search(r'["“]([^"”]{3,80})["”]', seg)
            if m:
                val = clean_candidate(m.group(1).strip())
                if val and len(val.split()) >= 2:
                    return val
        doc = nlp(seg)
        if want_person:
            ents = [e.text for e in doc.ents if e.label_ == 'PERSON' and len(e.text.split()) >= 2]
        else:
            ents = [e.text for e in doc.ents if e.label_ in {'WORK_OF_ART','EVENT','ORG'}]
            if not ents:
                # fallback: multi-word TitleCase
                m2 = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,6})\b', seg)
                if m2:
                    ents = [m2.group(1)]
        for raw in ents:
            c = clean_candidate(raw or '')
            if not c:
                continue
            if not want_person and len(c.split()) < 2:
                continue
            return c
        return None

    # main selection
    win_tweets = [tw for tw in final_tweets if any(c.strip() in tw.lower() for c in WIN_CUES)]
    print(rf"# of Tweets with winner cues: {len(win_tweets)}")

    # optional: use nominees as precision filter
    try:
        nominees_by_award = get_nominees(year)
    except Exception:
        nominees_by_award = {award: [] for award in AWARD_NAMES}

    winners = {award: "" for award in AWARD_NAMES}
    counts = {award: Counter() for award in AWARD_NAMES}

    for award in AWARD_NAMES:
        want_person = expect_person(award)
        toks = award_tokens(award)
        ctx = award_context_words(award)
        nominee_set = set(x.lower() for x in nominees_by_award.get(award, []) if x)

        for tw in win_tweets:
            tl = tw.lower()
            if not mentions_award(tl, toks, ctx):
                continue
            seg = first_after_cue_segment(tw)
            if not seg:
                continue
            cand = pick_from_segment(seg, want_person)
            if not cand:
                continue

            # base vote
            base = 1
            # precision bump if candidate is among nominees (when we have them)
            if nominee_set and cand.lower() in nominee_set:
                base += 1
            # extra bump if tweet includes a context term for the award
            if any(k in tl for k in ctx):
                base += 1

            counts[award][cand] += base

        winners[award] = counts[award].most_common(1)[0][0] if counts[award] else ""

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
        # using spacy for Recognizing First Names and Last Names
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("spacy model not downloaded, run: python -m spacy download en_core_web_sm")
        return []
    
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
    presenters = {}

    #for each award name make a list of words that would refer to it 
    for award in AWARD_NAMES:
        presenters[award] = []
        #make a list of keywords for each award name
        award_lower = award.lower()
        award_keywords = [w for w in award_lower.split() \
                          if w not in {'by', 'an', 'of', '-', 'the', 'a', 'in', 'or'}]
        #add some common alternates/abbreviations
        if 'television' in award_keywords:
            award_keywords.append('tv')
        if 'series' in award_keywords:
            award_keywords.append('show')
        if ('motion' in award_keywords) and ('picture' in award_keywords):
            award_keywords.append('movie')
            award_keywords.append('film')

        for tweet in filtered_tweets:
            pass

    return(presenters)

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
    # Your code here
    pre_ceremony()

    #get hosts for event
    # hosts = get_hosts(YEAR)
    # print(rf"Hosts: {hosts}")

    #get awards
    # awards = get_awards(YEAR)
    # print(rf"Awards: {awards}")

    # nominees = get_nominees(YEAR)
    # print(nominees)
    # winner = get_winner(YEAR)
    # print(winner)

    #get best dressed
    best_dressed = get_best_dressed(YEAR)
    print(rf"Best Dressed: {best_dressed}")

    return

if __name__ == '__main__':
    #start timer
    start = time.time()

    main() #main run

    #end timer
    end = time.time()
    time = (end - start) / 60
    print(rf"Time taken to run: {time} minutes")