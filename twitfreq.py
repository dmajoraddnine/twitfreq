import sys, os, urllib.request, urllib.parse, json, re
from operator import itemgetter

if len(sys.argv) < 2:
	#sys.exit('Usage: \'python %s [--includeRetweets] [--includeReplies] [twitterHandle]\'' % sys.argv[0]) (deal with this later)
	sys.exit( 'Usage: \'python %s [twitterHandle]\'' % sys.argv[0] )
else:
	handle = sys.argv[1]

wordHash = {}
tweetsGotten = 0
outputFile = open( 'twitfreq-output-%s.txt' % handle, 'w' )

while tweetsGotten < 1000:
	if( tweetsGotten % 200 == 0 ):
		print( 'Getting new tweets...(%d gotten so far)' % tweetsGotten )
	
	paramDict = { 'screen_name':handle, 'count':200, 'trim_user':'true' }
	try: #only add max_id and since_id if loop has run at least once already
		#NOTE: subtracting 1 from oldest tweet ID only works because we are on 64-bit Python. see: https://dev.twitter.com/docs/working-with-timelines
		paramDict['since_id'] = newestTweetProcessed
		paramDict['max_id'] = ( oldestTweetProcessed - 1 )
	except NameError:
		pass
	params = urllib.parse.urlencode( paramDict )
	try:
		response = urllib.request.urlopen( 'http://api.twitter.com/1/statuses/user_timeline.json?%s' % params )
	except IOError as error:
		print( 'HTTP Error!\n Code=%d\nMessage=%s\nHeaders=%s' % ( error.code, error.msg, error.hdrs ) )
		sys.exit()
	try:
		content = response.read()
		utfContent = content.decode( 'utf8' )
		data = json.loads( utfContent )
	except:
		sys.exit( 'Uh oh!  Error loading content from twitter.  content=%s\nutfContent=%s\ndata=%s' % content, utfContent, data )
	
	#process tweets -- tokenize then hash
	for tweet in data:
		cleanText = re.sub( '[!?,.]', '', tweet['text'] ) #strip punctuation that would interfere with tokenization
		tokens = cleanText.split()
		for t in tokens:
			try:
				wordHash[t] = wordHash[t] + 1
			except KeyError: #key is not present
				wordHash[t] = 1
		
		#logistics
		tweetsGotten += 1
		try:
			newestTweetProcessed = max( newestTweetProcessed, tweet['id'] ) #recent tweets have HIGHER numbered IDs
		except NameError: #first run of loop
			newestTweetProcessed = tweet['id']
		try:
			oldestTweetProcessed = min( oldestTweetProcessed, tweet['id'] ) #older tweets have LOWER numbered IDs
		except NameError: #first run of loop
			oldestTweetProcessed = tweet['id']
			
#sort the dict and output results
for w in ( sorted( wordHash, key=itemgetter( 1 ), reverse=True ) ):
	outputFile.write( '%s\n' % w[0] )