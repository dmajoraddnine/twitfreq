import sys, urllib.request, urllib.parse, json, re, operator

if len(sys.argv) < 2:
	#sys.exit('Usage: \'python %s [--includeRetweets] [--includeReplies] [twitterHandle]\'' % sys.argv[0]) (deal with this later)
	sys.exit( 'Usage: \'python %s [twitterHandle]\'' % sys.argv[0] )
else:
	handle = sys.argv[1]

#tokenizes a tweet and adds the words to a hashtable (dict), then returns the lower tweet ID between the sentinel and the current tweet ID
def processTweet( tweet, hash, lowestID ):
	cleanText = re.sub( '[!?,.-/=+&]', '', tweet['text'] ) #strip punctuation that would interfere with hashing
	tokens = cleanText.split()
	for t in tokens:
		try:
			hash[t] = hash[t] + 1
		except KeyError:
			hash[t] = 1
	return ( min( lowestID, tweet['id'] ) )

wordHash = {}
tweetsGotten = 0
outputFile = open( 'twitfreq-output-%s.txt' % handle, 'w' )

while tweetsGotten < 1000:
	print( 'Getting new tweets...(%d gotten so far)' % tweetsGotten )
	
	#build the GET parameters
	paramDict = { 'screen_name':handle, 'count':200, 'trim_user':'true' }
	try: #only need max_id if loop has run at least once already
		paramDict['max_id'] = lowestTweetId
	except NameError:
		pass
	
	#perform the request
	params = urllib.parse.urlencode( paramDict )
	try:
		response = urllib.request.urlopen( 'http://api.twitter.com/1/statuses/user_timeline.json?%s' % params )
	except IOError as error:
		print( 'HTTP Error!\n Code=%d\nMessage=%s\nHeaders=%s' % ( error.code, error.msg, error.hdrs ) )
		sys.exit()
	headers = dict( response.info() )
	print( 'Request successful! Length=%s, API Requests Remaining=%s' % ( headers['Content-Length'], headers['X-RateLimit-Remaining'] ) )
	try:
		content = response.read()
		utfContent = content.decode( 'utf8' )
		data = json.loads( utfContent )
	except:
		sys.exit( 'Uh oh!  Error parsing JSON.\ncontent=%s\nutfContent=%s\ndata=%s' % ( content, utfContent, data ) )
	
	#process tweets -- tokenize then hash
	for tweet in data:
		try:
			if( tweet['id'] != lowestTweetId ): #don't process the same tweet twice. see: https://dev.twitter.com/docs/working-with-timelines
				lowestTweetId = processTweet( tweet, wordHash, lowestTweetId )
				tweetsGotten += 1
		except NameError:
			lowestTweetId = processTweet( tweet, wordHash, tweet['id'] )
			tweetsGotten += 1
			
#sort the dict and output results
for w in ( sorted( wordHash.items(), key=operator.itemgetter( 1 ), reverse=True ) ):
	try:
		outputFile.write( '%s\n' % w[0] )
	except UnicodeEncodeError:
		outputFile.write( '%s\n' % w[0].encode( 'ascii', 'ignore' ) )
		
print( 'twitfreq.py -- output complete!' )