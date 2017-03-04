from urllib2 import Request, urlopen
from time import sleep
import json

### Global Variables ###
_headers = {"User-agent" : "reddit_comment_fetcher by /u/rurik37"} # not sure if I need this
_host = 'http://www.reddit.com'

companyList = {}

nasdaqlisted = [line.rstrip('\n') for line in open('nasdaqlisted.txt')]
otherlisted = [line.rstrip('\n') for line in open('otherlisted.txt')]


del nasdaqlisted[0]
del otherlisted[0]

for i in nasdaqlisted:
    companyList[i.split('|')[0]] = 0

for i in otherlisted:
    companyList[i.split('|')[0]] = 0

def get_comments(URL,head,delay=2):
    '''Pretty generic call to urllib2.'''
    sleep(delay) # ensure we don't GET too frequently or the API will block us
    request = Request(URL, headers=head)
    try:
        response = urlopen(request)
        data = response.read()
    except:
        sleep(delay+5)
        response = urlopen(request)
        data = response.read()
    return data
   
def parse_json(json_data):
    '''Simple parser for getting reddit comments from JSON output. Returns tuple of JSON comments and list of IDs'''
    try:
        decoded = json.JSONDecoder().decode(json_data)
        comments = [x['data'] for x in decoded['data']['children'] ]
        ids = [comments[i]['name'] for i in range(len(comments))]
    except:
        return [], []
    return comments, ids
   
def scrape(targetUser, limit=0, pause=2): #, db='redditComments.db', storage='db'):    
    items = []
    userpageURL = _host + '/user/' + targetUser + '/comments/.json'       
    nPages=0 
    stop = False
    item_ids = []
#    tbl_comments = ConnectToDBCommentsTable(db)
    while not stop: # or len(items)<=50: # Need to figure out how to get past the 999 comments limit.
        if nPages > 0:
            last = items[-1]['name']
            paginationSuffix = '?count='+str(nPages*25)+'&after='+last #+'.json'
            print userpageURL + paginationSuffix    
        try:
            data = get_comments(userpageURL + paginationSuffix, _headers, pause)
        except:
            data = get_comments(userpageURL, _headers, pause)
        newItems, newIDs = parse_json(data)       
        if newItems == []:
            print "Reached limit of available comments"
            stop = True # this is redundant
            break
        try:
            for i, id in enumerate(newIDs):
                if id in item_ids:
                    print "Page is returning comments we've already seen. Ending scrape."
                    stop = True
                    break
                else:
                    items.append(newItems[i])
                    item_ids.append(id)
        except:
            items, item_ids = newItems, newIDs  
        nPages += 1
        print "Downloaded %d pages, %d comments. Oldest comment: %d \n" % (nPages, len(items), items[-1]['created'])  
        if limit > 0 and len(item_ids) >= limit:
            print "Exceeded download limit set by paramter 'limit'."
            items = items[0:limit]
            stop = True #redundant with 'break' command
            break        
    return items

# Probably should store comments as we get them. For now, let's just download them all and dump them into the DB all at once.   
def scrapeSub(targetSub, limit=0, pause=2): #, db='redditComments.db', storage='db'):    
    items = []
    userpageURL = _host + '/r/' + targetSub + '.json'       
    nPages=0 
    stop = False
    item_ids = []
#    tbl_comments = ConnectToDBCommentsTable(db)
    while not stop: # or len(items)<=50: # Need to figure out how to get past the 999 comments limit.
        if nPages > 0:
            last = items[-1]['name']
            paginationSuffix = '?count='+str(nPages*25)+'&after='+last #+'.json'
            print userpageURL + paginationSuffix    
        try:
            data = get_comments(userpageURL + paginationSuffix, _headers, pause)
        except:
            data = get_comments(userpageURL, _headers, pause)
        newItems, newIDs = parse_json(data)       
        if newItems == []:
            print "Reached limit of available comments"
            stop = True # this is redundant
            break
        try:
            for i, id in enumerate(newIDs):
                if id in item_ids:
                    print "Page is returning comments we've already seen. Ending scrape."
                    stop = True
                    break
                else:
                    items.append(newItems[i])
                    item_ids.append(id)
        except:
            items, item_ids = newItems, newIDs  
        nPages += 1
        print "Downloaded %d pages, %d comments. Oldest comment: %d \n" % (nPages, len(items), items[-1]['created'])  
        if limit > 0 and len(item_ids) >= limit:
            print "Exceeded download limit set by paramter 'limit'."
            items = items[0:limit]
            stop = True #redundant with 'break' command
            break        
    return items


"""test = scrape("killermonkey87")"""

testSub = scrapeSub("stocks")

for comment in testSub:
    """ We are getting the body of the commented posts and splitting them so they appear in list form """ 
    commentWordList = comment['selftext'].split(' ')
    for word in commentWordList:
        if word in companyList.keys():
            companyList[word] += 1

for company in companyList.keys():
    if(companyList[company] == 0):
        del companyList[company]

print companyList
    

""" print test[0]['body'] """
""" print testSub[0] """

""" print "selftext: " + testSub[0]['selftext'] """

"""
count = 0
for i in testSub:
    print "author: " + i['author']
"""


