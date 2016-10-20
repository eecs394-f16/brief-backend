from flask import Flask
from flask import jsonify
from bs4 import BeautifulSoup
import requests
import feedparser
import os
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

def to_f(k):
    return int(float(k) * float(9)/5 - 459.67)

@cross_origin()
@app.route("/weather")
def weather():
    r = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"q":"Evanston","APPID":"2632210dcc93cc19c2ee8b5fb2b59af9"})
    result = r.json()
    weather = {"main":result["main"],"weather":result["weather"]}
    weather["main"]["temp"] = to_f(weather["main"]["temp"])
    weather["main"]["temp_max"] = to_f(weather["main"]["temp_max"])
    weather["main"]["temp_min"] = to_f(weather["main"]["temp_min"])
    return jsonify(weather)

@cross_origin()
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

@cross_origin()
@app.route("/events")
def events():
    r = requests.get("http://planitpurple.northwestern.edu/#search=/2/1+3+2+9+11+5+10+6+4+8+7/1+3+4+5/")
    soup = BeautifulSoup(r.text, 'html.parser')
    events = soup.select(".events")[0]
    events = events.find_all("li")

    events_json = []
    for event in events:
    	link = event.find("a")
    	url = link['href']
    	e = {}
    	e['title'] = link.get_text().strip()
    	e['url'] = "http://planitpurple.northwestern.edu" + url
    	e['time'] = event.select(".event_time")[0].get_text().strip()
    	e['category'] = event.select(".event_category")[0].get_text().strip()
    	e['location'] = event.select(".event_location")[0].get_text().replace("- ", "").strip()
    	events_json.append(e)

    return jsonify({"entries":events_json})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
