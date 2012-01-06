#!/home/deconcep/env/bin/python
# coding=utf-8

import ConfigParser
import time
import twitter

# Requires a config file (config.cfg)that contains your
# access tokens from twitter. Looks like this:
# [tokens]
# consumer_key = <consumer key>
# consumer_secret = <consumer_secret>
# access_toekn_key = <access token key>
# access_token_secret = <access token secret>
#
Config = ConfigParser.ConfigParser()
Config.read('wormconfig.cfg')

CONSUMER_KEY = Config.get('tokens', 'consumer_key')
CONSUMER_SECRET = Config.get('tokens', 'consumer_secret')
ACCESS_TOKEN_KEY = Config.get('tokens', 'access_token_key')
ACCESS_TOKEN_SECRET = Config.get('tokens', 'access_token_secret')

api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)

# TODO: support multiple search terms (but also need to support multiple responses)
searches = ('"baited breath" -"RT" -cheese -mouse -mousetrap -mousetraps -bated -fish', )

def main():
  while True:
    for search in searches:
      try:
        statuses = api.GetSearch(search)
      except:
        # API errors happen sometimes
        time.sleep(60)
        continue
      print "search is %s" % search

      # Get my timeline to see who i've recently replied to (and don't reply to them again)
      public_timeline = api.GetUserTimeline('wormmouth')
      users_replied_to = [];

      for s in public_timeline:
        print s.GetInReplyToScreenName()
        users_replied_to.append(s.GetInReplyToScreenName())

      s = statuses[0]
      print "Is user replied to already?: %s " % (s.user.screen_name in users_replied_to)
      print
      if (not s.user.screen_name in users_replied_to):
        print
        print "Replying to: %s - %s" % (s.user.screen_name, s.text)
        postUpdate(reply_to_status_id=s.id, reply_to_username=s.user.screen_name)
        print "REPLIED! \n"
        print
      else:
        print '--------'

      updateHomepage(public_timeline)
    time.sleep(120)


def postUpdate(reply_to_status_id, reply_to_username):
  status = u'@%s I think you meant to say “bated breath”' % reply_to_username
  posted_status = api.PostUpdate(status, in_reply_to_status_id=reply_to_status_id)
  print posted_status.text
  print
  print '--------'


# Update the html page with the current front page of tweets:
# http://godsakes.geoffstearns.com/
def updateHomepage(statuses):
  status_template = '<blockquote class="twitter-tweet tw-align-center" data-in-reply-to="%(reply_to_id)s"><p>@<a href="https://twitter.com/%(screen_name)s">%(screen_name)s</a> %(tweet_text)s</p>&mdash; Worm Mouth (@WormMouth) <a href="https://twitter.com/wormmouth/status/%(tweet_id)s" data-datetime="%(tweet_datetime)s">%(tweet_date)s</a></blockquote>'
  statushtml = []
  for s in statuses:
    statushtml.append(status_template % { 'reply_to_id': s.GetInReplyToStatusId(), 'screen_name': s.user.screen_name, 'tweet_text': s.text, 'tweet_id': s.id, 'tweet_datetime': s.created_at, 'tweet_date': s.created_at })

  htmlFile = open('public/wormindex.html', 'w')
  html = """
  <!DOCTYPE html>
  <!-- Don't bother editing this, it's auto-generated. -->
  <html>
    <head>
      <title>Why would you put worms in your mouth?</title>
    </head>
    <body>
      %s
      <script src="//platform.twitter.com/widgets.js" charset="utf-8"></script>
    </body>
  </html>
  """ % (''.join(statushtml))
  #print html
  htmlFile.write(html.encode('utf-8'))
  htmlFile.close()

#postUpdate('tensafefrogs')
main()
