from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "ABRChitFund Application Running"


if __name__ == "__main__":
    app.run(debug=True)