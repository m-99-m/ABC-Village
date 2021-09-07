from flask import Flask, render_template, request
import requests

username = "m_99"
url = "https://atcoder.jp/users/" + username
r_get = requests.get(url)
txt = r_get.text
print(txt)