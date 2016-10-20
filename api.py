from flask import Flask
from flask import jsonify
from bs4 import BeautifulSoup
import requests
import feedparser
import os
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

app = Flask(__name__)

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@crossdomain(origin='*')
@app.route("/weather")
def weather():
    r = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"q":"Evanston","APPID":"2632210dcc93cc19c2ee8b5fb2b59af9"})
    result = r.json()

    return jsonify({"main":result["main"],"weather":result["weather"]})

@crossdomain(origin='*')
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

@crossdomain(origin='*')
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
