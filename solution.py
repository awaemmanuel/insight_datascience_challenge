#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unicodedata as ud, re, string, sys, os, simplejson
from itertools import islice, chain
from textblob import TextBlob

'''
    Helper class to highlight clean text 
'''
class color(object):
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


############## HELPER FUNCTIONS ####################
    
'''
    Function to convert string internally to unicode
'''
def to_unicode(unicode_or_str):
    if isinstance(unicode_or_str, str):
        value = unicode_or_str.decode('utf-8')
    else:
        value = unicode_or_str
    return value

'''
    Function to convert unicode back to string for output
'''

def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('utf-8')
    else:
        value = unicode_or_str
    return value

'''
    Function that strips unicode with REGEX
'''

def strip_unicode(text):
    #REGEX for tweet unicode removal
    str_text = to_str(text)
    str_text =  re.sub(r'(\\u[0-9A-Fa-f]+)', '', str_text)
    return to_unicode(str_text)


'''
    Function returns TRUE if pattern exists in text
'''

def contains_pattern(text, pattern):
    return True if (re.search(pattern, text)) else False
    
    
'''
    Function that checks if text is empty
'''

def is_empty(text):
    return not text.strip()


'''
    Function that checks if text contains only punctuations
'''

def is_not_only_punc(text):
    pattern = re.compile("[{}]".format(re.escape(string.punctuation)))
    text_list = text.split()
    return True if [char for char in text_list if not pattern.match(char)] else False
    
    
'''
   Extract hashtags from text if any
   Normalize for unicode and possibility of mulitple #s
'''

def get_hashtags(text):
    #Fetch and clean hashtags from tweet
    #text = unicode(text)
    tags = list(set([re.sub(r"#+", "#", k) for k in set([re.sub(r"(\W+)$", "", j, flags = re.UNICODE) for j in set([i for i in text.split() if i.startswith("#")])])]))
    
    return [tag for tag in tags]


############## PROCESS FLOW FUNCTIONS ####################

'''
    Generate tweets text and timestamp 
    
    Yields a single tweet timestamp and text on at a time using a generator,
    which must be properly handled by the generator caller.
'''

def extract_tweet_text_and_timestamp(input_file):
    
    # Open input file, generate text and timestamp
    try:
        with open(input_file) as twitter_input:
            for line in twitter_input:
                if not line: # To filter out keep-alive new lines
                    continue
                single_tweet = simplejson.loads(line)
                
                if 'text' in single_tweet:
                    
                    text = single_tweet['text']
                    time_stamp = single_tweet['created_at']
                    lang = single_tweet["lang"]
                    
                    if single_tweet["lang"] != 'en' and single_tweet["lang"] != 'und':
                        tblob = TextBlob(text)
                        frm_ln = lang
                        print "Conversion from : ", frm_ln
                        # Translation of tweets from native lang to 'en'
                        tweet_text = tblob.translate(from_lang=frm_ln, to="en")
                        con_text = str(tweet_text)
                        with open('sample.json', 'a') as f:
                            simplejson.dump("{} ==> {}".format(frm_ln, con_text), f)
                    elif single_tweet["lang"] != 'und':
                        with open('sample.json', 'a') as f:
                            con_text = to_str(text)
                            simplejson.dump("{} ==> {}".format(lang, con_text), f)
                    yield text, time_stamp
    
    except IOError:
        sys.stderr.write("[extract_tweet_text_and_timestamp] - Error: Could not open {}".format(input_file))
        sys.exit(-1)


'''
    clean_tweet remove unicode and track number of these tweets
    :type str: text
    :rtype str
'''
def clean_string(text):
    
    if not text: return ""
    
    text_has_unicode = False
    
        
    # Convert text to raw literals to avoid regex issues.
    text = text.replace("\\", "\\\\")
    text = to_unicode(text)
    
    # Unicode pattern
    unicode_pattern = re.compile(u'(\\u[0-9A-Fa-f]+)')
    #print "Contains ==> ", contains_pattern(text, unicode_pattern)
    
    
    # Keep track of texts with unicode and then remove the unicode chars
    if contains_pattern(text, unicode_pattern):
        text_has_unicode = True
        text = ud.normalize('NFKD', text).encode('ascii','ignore')
        #text = re.sub(unicode_pattern, '', text)
        #text = strip_unicode(text)

    # Remove escape characters. This is faster than using re.compile(r'\s+') class
    text = ' '.join(text.strip().split())
    text = text.replace("\\", "")
    
    # Return clean/normalized text and also if a unicode character was found.
    return to_str(text), text_has_unicode


'''
    Function that processes a text message and writes to a text file in required output
'''

def process_tweets(input_file, output_file):       
    
    # check if file exists on filesystem
    if not input_file or not os.path.isfile(input_file):    
        return
    
    # Global variable initializations
    num_tweets_with_unicode = 0
    has_unicode = False
    #results = []
    
#    for idx, text in enumerate(islice(extract_tweet_text_and_timestamp(input_file), 20)):
#        results.append(text[0])
#    
#    return results

    # Extract tweet text and timestamp with generator
    for text_and_time in extract_tweet_text_and_timestamp(input_file):
        text = text_and_time[0]
        time_stamp = text_and_time[1]
        
        # Clean out text
        clean_text, has_unicode = clean_string(text)
        clean_text = clean_text.strip()
        #clean_text = clean_text.encode('utf-8')
        
        if (has_unicode):
            num_tweets_with_unicode += 1
        
        #print "TEXT AFTER STRIP ==> ", clean_text, has_unicode, type(clean_text)
        
        # Sanity Check on timestamp
        clean_time, _ = clean_string(time_stamp)
        
        #print "TEXT AFTER STRIP ==> ", clean_time, _ , type(clean_time)
        
        #sys.exit(-1)
        
        # Retrieve hashtags if any in tweet
        if r'#' in clean_text:
            tags = get_hashtags(clean_text)
        
        # Write to output file
        try:
            with open(output_file, 'a') as f:
                if not is_empty(clean_text) and is_not_only_punc(clean_text):
                    f.write("{} ({})\n".format(clean_text, clean_time))
        except IOError:
            sys.stderr.write("[process_tweets] - Error: Could not open {}".format(output_file))
            sys.exit(-1)
    
    # Write number of tweet with unicode to file
    try:
        with open(output_file, 'a') as f:
            f.write("{} tweets contained unicode.\n".format(num_tweets_with_unicode))
    except IOError:
        sys.stderr.write("[process_tweets] - Error: Could not open {}".format(output_file))
        sys.exit(-1)
        
if __name__ == '__main__':
    
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    input_file = file_dir + '/data-gen/tweets.txt'
    output_file = file_dir + '/data-gen/output.txt'
    
    process_tweets(input_file, output_file)
    
    print "Done. OK!"
#    print repr(t)