#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unicodedata as ud, re, string, sys, os, simplejson
from itertools import islice, chain

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
    #str_text = ud.normalize('NFKD', text).encode('ascii','ignore') # Incase we want to 
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
    tags = list(set([re.sub(r"#+", "#", k) for k in set([re.sub(r"(\W+)$", "", j, flags = re.UNICODE) for j in set([i for i in text.split() if i.startswith("#")])])]))
    
    return [tag for tag in tags]


'''
    Function that guarantees we process only basic latin characters
'''

def remove_non_basic_latin_chars(text):
    # Process only basic latin characters else continue
    return ''.join([c for c in text if ord(c) in xrange(32, 128)])


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
    
    if not text: return ("", False)
        
    text_has_unicode = False
    
    # Convert text to raw literals and unicode to avoid regex  and internal processing issues.
    text = text.replace("\\", "\\\\")
    text = to_unicode(text)
    
    # Unicode pattern
    unicode_pattern = re.compile(u'(\\u[0-9A-Fa-f]+)')
    
    # Keep track of texts with unicode and then remove the unicode chars
    if contains_pattern(text, unicode_pattern):
        text_has_unicode = True
        text = strip_unicode(text)

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

    # Extract tweet text and timestamp with generator
    for text_and_time in extract_tweet_text_and_timestamp(input_file):
        text = text_and_time[0]
        time_stamp = text_and_time[1]
        
        # Proceed only with non basic latin characters
        text = remove_non_basic_latin_chars(text)
        
        # tweet was composed of non basic latin chars
        if not text:
            continue
            
        # Clean out text
        clean_text, has_unicode = clean_string(text)
        clean_text = clean_text.strip()
          
        # Sanity Check on timestamp
        clean_time, _ = clean_string(time_stamp)
        
        if (has_unicode):
            num_tweets_with_unicode += 1
    
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

        
class InsightChallengeSolution(object):
    
    def __init__(self, input_filename, output_filename):
        self.input_file = input_filename
        self.output_file = output_filename
        self.num_tweets_with_unicode = 0
        self.has_unicode = False
        self.hashtag_graph = {}
        
################# SCRIPT EXECUTION #######################
if __name__ == '__main__':
    
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    input_file = file_dir + '/data-gen/tweets.txt'
    output_file = file_dir + '/data-gen/output.txt'
    
    process_tweets(input_file, output_file)
    
    print "Done. OK!"