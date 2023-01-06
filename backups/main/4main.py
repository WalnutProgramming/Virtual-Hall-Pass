BackupTime = 'Wed Jan  4 21:57:30 2023'#Automatically generated backup time
from flask import Flask, redirect, url_for, render_template, request, make_response
from Token import TokenStore
import backup
#import backup  #Only import if you want to backup the file

app = Flask(__name__)

valid_logins = {"MisterMan": "HumanPersonPassword01"}  #Test Logins for now

tokens = TokenStore("store.txt")
tokens.read()  #Load token data from save file


def setcookie(html, name, value):
    # Make response with cookie
    resp = make_response(html)
    resp.set_cookie(name, value)
    return resp


def getcookie(request, name):
    cookie = request.cookies.get(name)
    return cookie


#---------------------------------------------------------------------------------------
#sign in page
@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in valid_logins:
            if password == valid_logins[username]:
                resp = redirect(url_for("dashboard", user=username))
                resp.set_cookie("User", username)
                resp.set_cookie("Token", tokens.generate_token())
                return resp
            else:
                return render_template("new_index.html")
        return render_template("new_index.html")

    else:
        cur_token = getcookie(request, "Token")
        if cur_token != "" and cur_token:
            if tokens.check(cur_token):
                return url_for("dashboard")
            else:
                if not tokens.remove_token(cur_token):
                    print(f"failed to remove token {cur_token}  !")
                return setcookie(render_template("new_index.html"), "Token",
                                 "")

        return render_template("new_index.html")


@app.route("/pass/<user>", methods=["GET", "POST"])
def passInProgress(user):
    return render_template("passInProgress.html")


#---------------------------------------------------------------------------------
#hallpass creation dashboard
@app.route("/dashboard, methods=['POST', 'GET']")
def dashboard():
    return render_template("dashboard.html")


@app.route("/classes")
def classes():
    return render_template("classes.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/backend")
def backend():
    return render_template("backend.html")


#we need to make better looking error pages
@app.errorhandler(500)
def Server_error(error):
    return "500: Server had an internal error", 500


@app.errorhandler(404)
def page_not_found(error):
    return "404: Page not found", 404


@app.errorhandler(405)
def Method_not_allowed(error):
    return "405: Method not allowed", 405


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=81)
