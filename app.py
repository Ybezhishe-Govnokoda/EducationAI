from flask import Flask, render_template
from databaser import Databaser


app = Flask(__name__)
db = Databaser()


@app.route("/")
def authorize():
    return render_template('autorization.html')


@app.route("/main")
def index():
    return render_template('index.html')


@app.route("/reg")
def register():
    return render_template('register.html')


@app.route("/test")
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)