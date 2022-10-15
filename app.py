from flask import Flask, render_template
from flask_bootstrap import Bootstrap5

app = Flask(__name__)

bootstrap = Bootstrap5(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/browse')
def browse():
    return render_template('browse.html')



if __name__ == '__main__':
    app.run(debug=1)