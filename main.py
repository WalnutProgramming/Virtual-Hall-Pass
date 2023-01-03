from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        username = request.form["nm"]
        return redirect(url_for("passInProgress", user=username))

    else:
        return render_template("index.html")


@app.route("/pass/<user>", methods=["GET", "POST"])
def passInProgress(user):
    return render_template("passInProgress.html")


@app.route("/classes")
def classes():
    return render_template("classes.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=81)
