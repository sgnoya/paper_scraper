import requests
import tweepy


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
    auth = tweepy.OAuthHandler(key, secret)
    auth.set_access_token(token, tsecret)
    api = tweepy.API(auth)

    return api
