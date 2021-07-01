from __future__ import unicode_literals
from flask import Flask, flash, redirect, render_template, request, session, abort
from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen
import re
import requests
from requests_html import HTMLSession  
from unidecode import unidecode
import os
from os.path import exists

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
    <link rel="stylesheet" type="text/css" href="../static/css/img.css">
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.13.1/css/all.min.css">
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

    try:
        ren = session.get(vidembed_url, allow_redirects=False)
        ren.html.render(timeout=20)
        soup = BeautifulSoup(ren.html.html, 'html.parser')
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

        mp4_exists = 'link' in locals() or 'link' in globals()

        if mp4_exists is True:
            dest_folder = 'static/mov/'
            mp4 = '{}.mp4'.format(var)
            file_path = os.path.join(dest_folder, mp4)
            if os.path.exists(file_path):
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
                </video>
                """.format(var)

            else:
                r = requests.get(link, stream=True)
                if r.ok:
                    print("saving to", os.path.abspath(file_path))
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024 * 8):
                            if chunk:
                                f.write(chunk)
                                f.flush()
                                os.fsync(f.fileno())

                else:  # HTTP status code 4XX/5XX
                    print("Download Failed: Status Code {}\n{}".format(r.status_code, r.text))
                    return """
                    <html>
                    <head>
                    <title>Willy's Movies!</title>
                    </head>
                    <body>
                    <h2>Willy's Illegal Movies</h2>
                    <hr>
                    <font color=red>
                    <h1>Download Failed: Status Code {0}\n{1}</h1>
                    """.format(r.status_code, r.text)

        elif mp4_exists is False:
            print('mp4_exists is False')
            for download in soup.select('div.dowload:nth-child(2) > a:nth-child(1)'):
                link = download['href']
                print(link)

            r = requests.get(link)
            soup = BeautifulSoup(r.content, 'html.parser')
            onclick = soup.find(lambda tag:tag.name=='a' and 'Original' in tag.text)
            if onclick is None:
                print('onclick is false')
                onclick = soup.find(lambda tag:tag.name=='a' and 'Normal quality' in tag.text)
                items = re.findall("'([a-zA-Z0-9,\s,-]*)'", (onclick['onclick'] if onclick else ''))

            id_dl = items[0]
            mode_dl = items[1]
            hash_dl = items[2]

            hash_url = 'https://sbplay.org/dl?op=download_orig&id={0}&mode={1}&hash={2}'.format(id_dl, mode_dl, hash_dl)
            print(hash_url)
            r = requests.get(hash_url)
            soup = BeautifulSoup(r.content, 'html.parser')
            mp4 = soup.find(lambda tag:tag.name=='a' and 'Direct Download' in tag.text)
            print(mp4)


            return """
            <html>
            <head>
            <title>Willy's Movies!</title>
            </head>
            <body>
            <h2>Willy's Illegal Movies</h2>
            <hr>
            <video controls>
                <source src="{}" type="video/mp4">
            </video>
            """.format(mp4)
        else:
            return 'broke'

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
        </video>
        """.format(var)
    except:
        print('Error')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
