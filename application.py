from flask import Flask
from flask import render_template
from flask import request
from app.analyzer import function

app = Flask(__name__)
main_url = 'http://127.0.0.1:5000/'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['request']
    result, url = function(query)
    return render_template('result.html', result=result, url=url, back=main_url)


if __name__ == '__main__':
    app.run(debug=False)
