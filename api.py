from flask import Flask
from flask import jsonify
import requests
import feedparser

app = Flask(__name__)

@app.route("/weather")
def weather():
    r = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"q":"Evanston","APPID":"2632210dcc93cc19c2ee8b5fb2b59af9"})
    result = r.json()

    return jsonify({"main":result["main"],"weather":result["weather"]})

@app.route("/news")
def news():
    d = feedparser.parse('http://dailynorthwestern.com/feed/')
    entries = []
    count = 0
    for entry in d.entries:
        entries.append({
            "title":entry.title,
            "link":entry.link,
            "description":entry.description,
            "published":entry.published
        })
        if count == 5:
            break
        count += 1
    return jsonify(entries)

if __name__ == "__main__":
    app.run()
