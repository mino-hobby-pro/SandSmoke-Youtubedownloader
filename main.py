import os
import requests
from flask import Flask, jsonify, Response, request
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app, support_credentials=True)

# CORS Proxy URL
corbsProxUrl = "https://api.allorigins.win/raw?url="

# Vars
currentDomain = ""
siteUrl = "http://127.0.0.1:5000/"

# Function to modify URLs in HTML content
def modifyUrls(content, baseUrl):
    try:
        content = content.decode("utf-8")
        soup = BeautifulSoup(content, 'html.parser')

        for element in soup.find_all(href=True):
            oldUrl = element['href']
            absoluteUrl = urljoin(currentDomain, element['href'])
            element['href'] = absoluteUrl

        for element in soup.find_all(src=True):
            oldUrl = element['src']
            absoluteUrl = urljoin(currentDomain, element['src'])
            element['src'] = absoluteUrl

        return str(soup)
    except Exception as e:
        return Response("Error processing the HTML content", status=500)

@app.route('/')
def home():
    return "Home page, add /h/google.com or /h/https://google.com to the end of the link above to open google."

@app.route('/h/<path:url>')
@cross_origin(supports_credentials=True)
def root(url):
    global currentDomain
    try:
        fullUrl = f"https://{url}" if not url.startswith('http') else url
        r = requests.get(fullUrl)
        currentDomain = fullUrl

        content = r.content
        modifiedContent = modifyUrls(content, siteUrl + "h/")
        response = Response(response=modifiedContent, status=r.status_code)
        response.headers["Content-Type"] = r.headers['Content-Type']
        return response
    except Exception as e:
        return Response("Error fetching the requested URL", status=500)

@app.errorhandler(404)
def invalidRoute(e):
    global currentDomain
    if currentDomain and not currentDomain.endswith("/"):
        currentDomain += "/"
    try:
        url = f'{siteUrl}h/{currentDomain}{request.url.replace(siteUrl, "")}/'
        r = requests.get(url)
        content = r.content
        modifiedContent = modifyUrls(content, siteUrl + "h/")
        response = Response(response=modifiedContent, status=r.status_code)
        response.headers["Content-Type"] = r.headers['Content-Type']
        return response
    except Exception as e:
        return Response("Error in handling 404", status=500)

if __name__ == '__main__':
    app.run()
