import unicodedata as ud, re, string, os, simplejson
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


def contains_pattern(text, pattern):
    return True if (re.search(pattern, text)) else False
    

'''
    clean_tweet remove unicode and track number of these tweets
    :type str: text
    :rtype str
'''
def clean_string(text, num_tweets_with_unicode=0):
    
    if not text: return ""
    
    #global num_tweets_with_unicode
    
    # Convert text to raw literals to avoid regex issues.
    text = text.replace("\\", "\\\\")
    
    # Unicode pattern
    unicode_pattern = re.compile(r'(\\u[0-9A-Fa-f]+)')
    
    # Keep track of texts with unicode and then remove the unicode chars
    if contains_pattern(text, unicode_pattern):
        num_tweets_with_unicode += 1
        text = re.sub(unicode_pattern, '', text)
    
    return "Getting AFTER PATTERNS NOW"
    # Remove escape characters. This is faster than using re.compile(r'\s+') class
    text = ' '.join(text.strip().split())
    text = text.replace("\\", "")
    
    # Finally just normalize text by replacing non-ascii to similiar ascii characters as possible
    return ud.normalize('NFKD', unicode(text)).encode('ascii','ignore')

'''
    Function that checks if text is empty
'''

def is_empty(text):
    return not text.strip()


'''
    Function that checks if text contains only punctuations
'''

def is_only_punc(text):
    pattern = re.compile("[{}]".format(re.escape(string.punctuation)))
    text_list = text.split()
    return True if [char for char in text_list if pattern.match(char)] else False
    

    

'''
   Extract hashtags from text if any
   Normalize for unicode and possibility of mulitple #s
'''
def get_hashtags(text):
    #Fetch and clean hashtags from tweet
    text = unicode(text)
    tags = list(set([re.sub(r"#+", "#", k) for k in set([re.sub(r"(\W+)$", "", j, flags = re.UNICODE) for j in set([i for i in text.split() if i.startswith("#")])])]))
    
    return [tag for tag in tags]


'''
    Function that processes a text message and writes to a text file in required output
'''

def process_tweets(input_file, output_file):       
    # check if file exists on filesystem
    if not input_file or not os.path.isfile(input_file):    
        return
    
    # Global variable initializations
    num_tweets_with_unicode = 0

    # Extract tweet text and timestamp with generator
    for text_and_time in extract_tweet_text_and_timestamp(input_file):
        text = text_and_time[0]
        time_stamp = text_and_time[1]
        
        # Clean out text
        clean_text = clean_string(text, num_tweets_with_unicode)
        clean_text = clean_text.strip()
        clean_text = clean_text.encode('utf-8')
        
        # Sanity Check on timestamp
        clean_time = clean_string(time_stamp)
        
        
        # Retrieve hashtags if any in tweet
        if r'#' in clean_text:
            tags = get_hashtags(clean_text)
        
        # Write to output file
        try:
            with open(output_file, 'a') as f:
                if not is_empty(clean_text) and not is_only_punc(clean_text):
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
    input_file = file_dir + '/data-gen/tweets2.txt'
    output_file = file_dir + '/data-gen/output.txt'
    
    process_tweets(input_file, output_file)
    
    print "Done. OK!"
    