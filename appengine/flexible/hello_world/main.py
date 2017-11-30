# Copyright 2015 Google Inc. All Rights Reserved.
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

# [START app]
import logging

from flask import Flask
import tweepy
import json
from azure.servicebus import ServiceBusService
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

hub_name = "ca674-python-tweet-eh"
key_name = "ca674-python-tweet-pol"
key_value = "B4vIImObKeeaqiMOhzz+FfpYI2qvZrrdHt/km7+4ueo="
namespace = "ca674-python-tweet-nsp"

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


app = Flask(__name__)


@app.route('/')
def twitter():
    """Return a friendly HTTP greeting."""
    class MyStreamListener(tweepy.StreamListener):
        def on_connect(self):
            print('Connected')

        def on_data(self, data):
            tweet_data = json.loads(data)
            snt = senti.polarity_scores(tweet_data["text"])                 # calculate sentiment of tweet
            sent_scr = str(snt['compound'])                                 # value for sentiment
            tweet_data['sentiment'] = sent_scr                              # add sentiment to tweet json
            tweet_data = json.dumps(tweet_data)
            sbs.send_event(hub_name, tweet_data)
            print(tweet_data)

        def on_warning(self, notice):
            print('disconnection warning')
            return False

        def on_error(self, status_code):
            if status_code == 420:
                return False
    
    stream_listener = MyStreamListener()
    myStream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    test = myStream.filter(track=keywords)
    return'script running'

#@app.route('/')
#def hello():
#    """Return a friendly HTTP greeting."""
#    return 'Twitter Running!'


    


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
    
# [END app]
