# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Sample application that demonstrates various aspects of App Engine's request
handling.
"""

import tweepy
import json
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from oauth2client.client import GoogleCredentials
import time




credentials = GoogleCredentials.get_application_default()
#from azure.servicebus import ServiceBusService
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


#hub_name = "ca674-python-tweet-eh"
#key_name = "ca674-python-tweet-pol"
#key_value = "B4vIImObKeeaqiMOhzz+FfpYI2qvZrrdHt/km7+4ueo="
#namespace = "ca674-python-tweet-nsp"

ctoken =  "jm700V8SAXaOpCmjjxQmOnJVK"
csecret = "Tl5fw1kVBRsr8zI30TmIrWAab4cQa3EFcwSk2uecC0YzASWThI"
key = "393388532-d2pcrtlglde6VrA2UT60SC0gDfncpWaqAwtofALL"
secret = "hg4lzzkgCevT2Wcf3s6Q9wNg65Z4dkhPyDbF7hqWqmNil"

keywords = ["bitcoin", "ripple", "litecoin", "ethereum"]

sbs = ServiceBusService(service_namespace=namespace, shared_access_key_name=key_name, shared_access_key_value=key_value)

auth = tweepy.OAuthHandler(ctoken, csecret)
auth.set_access_token(key, secret)
api = tweepy.API(auth)
senti = SentimentIntensityAnalyzer()

class MyStreamListener(tweepy.StreamListener):
    def on_connect(self):
        print('Connected')

    def on_data(self, data):
        tweet_data = json.loads(data)
        client = language.LanguageServiceClient()
        
   ###############sentiment
# The text to analyze     
        text = tweet_data["text"]
        text = text.encode("utf-8")
        document = types.Document(
    	content=text,
    	type=enums.Document.Type.PLAIN_TEXT)
    	gsentiment = client.analyze_sentiment(document=document).document_sentiment
    	#print('Text: {}'.format(text))
    	gscore = gsentiment.score
#    	print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
###############sentiment
        tweet_data['google_sentiment'] = gscore 
		

        snt = senti.polarity_scores(tweet_data["text"])                 # calculate sentiment of tweet
        sent_scr = str(snt['compound'])                                 # value for sentiment
        tweet_data['sentiment'] = sent_scr                              # add sentiment to tweet json
        tweet_data = json.dumps(tweet_data)
        
        
        #sbs.send_event(hub_name, tweet_data)
        print(tweet_data)
        

    def on_warning(self, notice):
        print('disconnection warning')
        return False

    def on_error(self, status_code):
        if status_code == 420:
            return False


stream_listener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=stream_listener)
myStream.filter(languages=["en"],track=keywords)
