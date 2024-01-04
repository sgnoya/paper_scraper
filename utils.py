import requests
import tweepy


class TwitterAPI2:
    def __init__(self, key, secret, token, tsecret):
        self.client = tweepy.Client(
            consumer_key=key,
            consumer_secret=secret,
            access_token=token,
            access_token_secret=tsecret,
        )

    def update_status(self, msg):
        self.client.create_tweet(text=msg)


def discord(url, message):
    payload = {"content": message}
    with requests.Session() as s:
        s.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        return s.post(url, data=payload)


def init_twitterapi(key, secret, token, tsecret):
    """
    key = keys.twitter.app.apikey
    secret = keys.twitter.app.apisecret
    token = keys.twitter.app.token
    tokensecret = keys.twitter.app.tokensecret
    """

    return TwitterAPI2(key, secret, token, tsecret)
