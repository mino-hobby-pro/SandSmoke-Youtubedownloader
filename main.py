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
useProx = False
useCorbsProx = False

# Function to modify URLs in HTML content
def modifyUrls(content, baseUrl):
    try:
        try:
            content = content.decode("windows-1252")
        except UnicodeDecodeError:
            content = content.decode("utf-8")
        
        # Parse HTML content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Modify href attributes in all tags
        for element in soup.find_all(href=True):
            oldUrl = element['href']
            absoluteUrl = urljoin(currentDomain, element['href'])
            print("\nReplaced: ", oldUrl, " With: ", absoluteUrl, "\n")
            element['href'] = absoluteUrl

        # Modify src attributes in all tags
        for element in soup.find_all(src=True):
            oldUrl = element['src']
            absoluteUrl = urljoin(currentDomain, element['src'])
            print("\nReplaced: ", oldUrl, " With: ", absoluteUrl, "\n")
            element['src'] = absoluteUrl

        return str(soup)
    except Exception as e:
        print(f"Error modifying URLs: {e}")
        return Response("Error processing the HTML content", status=500)

def trimUrl(url):
    parts = url.split('/')
    if len(parts) > 3:
        trimmedUrl = '/'.join(parts[:3]) + '/'
    else:
        trimmedUrl = url
    return trimmedUrl

@app.route('/')
def home():
    return "Home page, add /h/google.com or /h/https://google.com to the end of the link above to open google."

@app.route('/h/<path:url>')
@cross_origin(supports_credentials=True)
def root(url):
    global currentDomain
    try:
        fullUrl = f"https://{url}" if not url.startswith('http') else url
        print(f"Fetching: {fullUrl}")

        r = requests.get(fullUrl)
        currentDomain = fullUrl

        content = r.content
        modifiedContent = modifyUrls(content, siteUrl + "h/")
        response = Response(response=modifiedContent, status=r.status_code)
        response.headers["Content-Type"] = r.headers['Content-Type']
        response.headers["Access-Control-Request-Method"] = "post"
        response.headers["Access-Control-Request-Headers"] = "X-Requested-With"

        return response
    
    except Exception as e:
        print(f"Error fetching [{url}]: {str(e)}")
        return Response("Error fetching the requested URL", status=500)

@app.route('/<u>', methods=['GET'])
@cross_origin(supports_credentials=True)
def search(u):
    global currentDomain
    args = request.args
    query = args.get("q")

    try:
        if query and (len(query) < 4 or not query.startswith("https")):
            url = f"https://www.google.com/search?q={query}"
            print(f"Searching: {url}")
        else:
            url = query

        r = requests.get(url)
        content = r.content
        modifiedContent = modifyUrls(content, siteUrl + "h/")
        response = Response(response=modifiedContent, status=r.status_code)
        response.headers["Content-Type"] = r.headers['Content-Type']
        response.headers["Access-Control-Request-Method"] = "post"
        response.headers["Access-Control-Request-Headers"] = "X-Requested-With"

        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return Response("Error processing the request", status=500)

@app.errorhandler(404)
def invalidRoute(e):
    global currentDomain
    if(currentDomain[len(currentDomain)-1] != "/"):
        currentDomain = currentDomain + "/"
    currentDomain = currentDomain.replace("https://", "").replace("http://", "")

    try:
        url = f'{siteUrl}h/{trimUrl(currentDomain)}{request.url.replace(siteUrl, "")}/'
        print(f"[404] New URL is: {url}\n
")
        r = requests.get(url)
        content = r.content
        modifiedContent = modifyUrls(content, siteUrl + "h/")
        response = Response(response=modifiedContent, status=r.status_code)
        response.headers["Content-Type"] = r.headers['Content-Type']
        response.headers["Access-Control-Request-Method"] = "post"
        response.headers["Access-Control-Request-Headers"] = "X-Requested-With"

        return response

    except Exception as e:
        print(f"Error in handling 404: {str(e)}")
        return Response("Error in handling 404", status=500)

if __name__ == '__main__':
    app.run()
