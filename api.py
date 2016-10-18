from flask import Flask
from flask import jsonify
import requests
import feedparser
import os

app = Flask(__name__)

@app.route("/weather")
def weather():
    r = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"q":"Evanston","APPID":"2632210dcc93cc19c2ee8b5fb2b59af9"})
    result = r.json()

    return jsonify({"main":result["main"],"weather":result["weather"]})

@app.route("/news")
def news():
    d = feedparser.parse('https://dailynorthwestern.com/feed/rss/')
    entries = []
    count = 0
    for entry in d.entries:
    	e = {}
    	e["title"] = entry.title
    	e["link"] = entry.link
    	e["description"] = entry.description
    	e["published"] = entry.published
        entries.append(e)
        if count == 5:
            break
        count += 1
    return jsonify({"entries":entries})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
