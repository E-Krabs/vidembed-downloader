from __future__ import unicode_literals
from flask import Flask, flash, redirect, render_template, request, session, abort
from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen
import re
import requests
from requests_html import HTMLSession  
from unidecode import unidecode
import shutil

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.htm')

@app.route('/hello', methods=['POST'])
def hello():
    title_ascii = request.form['title']
    title_uni = urllib.parse.quote(title_ascii) #convert ASCII to Unicode
    r = requests.get('https://vidembed.net/search.html?keyword={}'.format(title_uni))
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('div', class_='main-inner')
    print(title_uni)
    #print(s)

    return '''
    <html>
    <head>
    <title>Willy's Movies!</title>
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.13.1/css/all.min.css">
    <link rel="stylesheet" type="text/css" href="../static/css/main.css"
    </head>
    <body>
    <h2>Willy's Illegal Movies</h2>
    <hr>
    {}</p>
    </body>
    </html>

    '''.format(s)

session = HTMLSession()
session.browser
@app.route('/videos/<var>', methods=['GET'])
def find(var):
    vidembed_url = 'https://vidembed.net/videos/{}'.format(var)
    hdr = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }

    r = session.get(vidembed_url, allow_redirects=False)
    r.html.render(timeout=20)
    soup = BeautifulSoup(r.html.html, 'html.parser')
    iframe = soup.find('iframe').get('src')
    print(iframe)

    vidembed_id = iframe.strip('//vidembed.net/streaming.php?')
    print(vidembed_id)
    vidembed_download = 'https://vidembed.net/download?id{}'.format(vidembed_id)
    print(vidembed_download)

    r = requests.get(vidembed_download)
    soup = BeautifulSoup(r.content, 'html.parser')
    for download in soup.select('div.mirror_link:nth-child(5) > div:nth-child(3) > a:nth-child(1)'):
        link = download['href']
        print(link)

    name = '/static/mov/{}.mp4'.format(var)
    r = requests.get(link, headers=hdr)
    print("****Connected****")
    f = open(name,'wb');
    print('Downloading...')
    for chunk in r.iter_content(chunk_size=255): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    print('Finished!')
    f.close()

    original = 'C:/Scripts/Python/Flask/{}.mp4'.format(var)
    target = 'C:/Scripts/Python/Flask/static/mov/{}.mp4'.format(var)

    shutil.move(original,target)

    return """
    <html>
    <head>
    <title>Willy's Movies!</title>
    </head>
    <body>
    <h2>Willy's Illegal Movies</h2>
    <hr>
    <video controls>
        <source src="/static/mov/{}.mp4" type="video/mp4">
    """.format(var)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
