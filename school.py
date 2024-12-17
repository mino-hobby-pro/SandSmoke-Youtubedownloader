from flask import Flask, request, Response, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/unblock', methods=['POST'])
def unblock():
    url = request.form['url']
    try:
        response = requests.get(url)
        return Response(response.content, status=response.status_code, headers=dict(response.headers))
    except requests.exceptions.RequestException as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
