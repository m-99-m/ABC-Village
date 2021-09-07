from flask import Flask, render_template, request
import requests
from flask import flash

def get_highest(username):
    url = "https://atcoder.jp/users/" + username + "/history/json"
    r_get = requests.get(url)
    js = r_get.json()
    rate = -1
    for item in js:
        rate = max(rate, item["NewRating"])
    return rate


def get_username(username):
    url = "https://atcoder.jp/users/" + username
    r_get = requests.get(url)
    txt = r_get.text
    pos = txt.find('<title>')
    if pos == -1:
        return username
    pos += 7
    username = ""
    while txt[pos] != ' ':
        username += txt[pos]
        pos += 1
    return username


def check_token(username, token):
    url = "https://atcoder.jp/users/" + username
    r_get = requests.get(url)
    txt = r_get.text
    if txt.find(token) != -1:
        return 1
    return 0
