from flask import Flask, redirect, url_for, render_template, request, make_response
from Token import TokenStore
from replit import db
from User import User
from Pass import PassStore
import datetime
import Permissions
from uuid import uuid4, UUID
import replit
from Permissions import get_permissions
import enum
from io import StringIO
from contextlib import redirect_stdout
#from flask_sqlalchemy import SQLAlchemy  # start integrating sql soon!
import os
import time
import hashlib
from UserFeedback import IssueReporter
import backup  # also imports Todo

app = Flask(__name__)

beta_mode = False  # This is a handy variable we can reference for beta stuff. Like stuff that is pretty broken and might not work. It is a good idea to be able to toggle that stuff on and off!

# making some users with User.py
users = {}
example1 = User(first_name="Liam",
                last_name="Lock",
                schedule=[3, 2, 5, 1, 7],
                username="Liam",
                password="password",
                perms=get_permissions("user"))
example2 = User("William",
                "Spearman", [1, 2, 3, 4, 5, 6, 7, 8],
                username="William",
                password="Pass",
                perms=get_permissions("admin"))

# USERNAME SHOULD BE THE SAME AS THE FIRST_NAME DUE TO THE WAY I ACCIDENTALLY FORMATTED STUFF
# should we change the part where it says 'your powerschool username' to 'first name'?

names_to_ids = {
}  # WARNING!! If we create a new user every time the code is run, the uuids will be invalidated every time we create the same user again. This will cause the User cookie to store the fallback (the username) instead of the uuid, which is less secure.


def gen_ids(
):  # function because names may need to be regenerated if a new user is added
  global names_to_ids
  names_to_ids = {}
  for i in db:
    if i != "Pass":
      names_to_ids[(db[i]["username"], db[i]["password"]
                    )] = i  # Should be {("Liam", "password") : "uuid here")}}


gen_ids()
issue_report = IssueReporter("feedback.txt")
passes = PassStore()  # Pass storage, for more info use print(dir(passes))
tokens = TokenStore("store.txt", name="User tokens")  # User tokens
tokens.read()  # Load token data from save file

admin_token = TokenStore("store2.txt", name="Admin tokens")  # admin stokens
admin_token.read()


def setcookie(html, name, value):
  # Make response with cookie
  resp = make_response(html)
  resp.set_cookie(name, value)
  return resp


def getcookie(request, name):
  cookie = request.cookies.get(name)
  return cookie


# def create_pass(origin, destination, user):
#  passes.create_pass(origin, destination, user


def delete_all_keys():
  keys = db.keys()
  for key in keys:
    del db[key]


def using_pass(userid):  # check if user is using pass
  if not userid in db or userid not in db["Pass"]:
    return False  # User has no passes
  using = False
  for i in db["Pass"][userid]:
    if i["end_time"] == None:  # No ending time, pass didn't finish yet
      using = True

  return using


def clean_tokens(tokenss):  # Get rid of invalid tokens.
  print(f"[*] Cleaning tokens ({tokenss.viewname})")
  copy = tokenss.data.copy()
  for i in copy:
    if not tokenss.check(i, encrypt=False):
      if not tokenss.remove_token(i, encrypt=False):
        print(f"[!] Failed to remove token {i}!")
  tokenss.save()



def format_passes():#This will return dumped data if it fails
  passes.update_data()
  
  def get_str_time(timen, can=True):
    try:
      if can:
        return datetime.datetime.fromtimestamp(timen).strftime("%H:%M"), datetime.datetime.fromtimestamp(timen).strftime("%S")
      else:
        return datetime.datetime.fromtimestamp(timen).strftime("%H"), datetime.datetime.fromtimestamp(timen).strftime("%M")
    except:
      return "0 hours 0 mins"
  passtemp = db['Pass']
  html = f"""<html><link type="text/css" rel="stylesheet" href=" {url_for('static', filename='style.css')} "/>"""
  gen_ids()
  for i in passtemp:
    passess = {}
    passess = passtemp[i]
    user = "Unknown"
    for e in names_to_ids:
      if names_to_ids[e] == i:
        user = e[0]
      
    #user = db[i]["first_name"]
    html += f"<h2>{user}'s passes:</h2>"
    for n in passess.value:
      try:
       if type(n) == str:
        b = passess.value[n].value
       elif type(n) == dict:
         b = n
       elif type(n) == replit.database.database.ObservedDict:
         b = n.value
       html += f"<p>went from room {b['origin']} to {b['destination']}, at {get_str_time(b['start_time'])[0]} and came back at {get_str_time(b['end_time'])[0]}. Taking a total of {get_str_time(b['elapsed_time'], can=False)[0]} hour(s), {get_str_time(b['elapsed_time'], can=False)[1]} minute(s), and {get_str_time(b['elapsed_time'])[1]} second(s). Reason: {b['reason']}</p><br><br>"
      except Exception as e:
        try:
          b
        except:
          b="NOPNE"
        mainstr = f"VALUE:<br><br><br><br>{passess.value}<br><br><br><br>ORIGIN:<br><br><br><br>{passess}<br><br><br>N:<br><br><br>{n}<br><br><br><br>B:<br><br><br><br>{b}<br><br><br><br><br>Exception:<br><br><br><br><br>{str(e)}<br><br><br><br>ALL PASSES:<br><br><br><br>{passtemp}<br><br><br><br>"
        for i in passess.value:
          mainstr += f"{i}<br><br>{passess.value}<br><br><br>"
        return mainstr#debug
      
      
  html += "</html>"
  
  return html


def get_user_permissions(request):  # A quick way to get the perms of a user
  uuid = getcookie(request, "User")

  if uuid is None or uuid == "" or uuid not in db:
    print("[DEBUG] uuid is none (in get_user_permissions)")
    return Permissions.Permission()  # Just return the default user
  else:
    perms_dict = db[uuid]["perms"]
    if type(perms_dict) == replit.database.database.ObservedDict:
      perms_dict = perms_dict.value
    temp = Permissions.Permission()
    temp.load_dict(perms_dict)
    return temp


def clean_db(
  verbose=False
):  # Try to remove duplicate users with the same last and first names
  print("[*] Cleaning database")
  copy = {}
  found = []
  for i in db:
    copy[i] = dict(db[i])
  for i in copy:
    if not "first_name" in copy[i] or not "last_name" in copy[i]:
      continue
    if (copy[i]["first_name"], copy[i]["last_name"]) not in found:
      found.append((copy[i]["first_name"], copy[i]["last_name"]))
    else:
      try:
        del db[i]
        if verbose:
          print(
            f"[*] Removed supposed duplicate with first name '{copy[i]['first_name']}' and last name '{copy[i]['last_name']}'"
          )
      except:
        pass


clean_tokens(tokens)
clean_tokens(admin_token)
clean_db(verbose=True)

# Above function calls can slow down the program if the database or token stores are too large


@app.route("/viewpasses", methods=['POST', 'GET'])
def testpass():# To access the view passes page, you must have the can_view_passes perms (admin perms)
  tk = getcookie(request, "Token")
  if tk is None:
    tk = "None"
  try:
    if not tokens.check(tk) or getcookie(request, "User") not in db:
      return redirect(url_for("index"))
  except:
    pass
  if not get_user_permissions(request).can_view_passes:
    return redirect(url_for("dashboard"))
  return format_passes()


# ---------------------------------------------------------------------------------------
# sign in page
@app.route('/', methods=['POST', 'GET'])
def index():
  # setcookie(request, "Verif", "user")
  gen_ids()
  tk = getcookie(request, "Token")
  try:
    if tokens.check(tk) and getcookie(request, "User") in db:
      return redirect(url_for("dashboard"))
  except:
    pass
  if request.method == "POST":
    # get username/password from form data
    username = request.form["username"]
    password = request.form["password"]
    found_user_id = False
    # authenticate
    password = hashlib.md5(password.encode()).hexdigest()  # ENCRYPT
    # variable First skips the token check.
    # im pretty sure this is redundant because we arlready found the user
    resp = redirect(url_for("dashboard", first="True"))
    for i in names_to_ids:  # Get the uuid from the name (we need the uuid for auth)
      if i[0] == username and i[1] == password:
        gen_ids()
        resp.set_cookie("User", names_to_ids[i])
        resp.set_cookie("Token", tokens.generate_token())
        found_user_id = True
        return resp
    if not found_user_id:
      print(
        f"[!] {username} not located in {names_to_ids}, using the name as fallback"
      )
      resp.set_cookie("User", username)

    resp.set_cookie("Token", tokens.generate_token())
    return resp

  # if request.method is GET
  else:
    cur_token = getcookie(request, "Token")
    if cur_token != "" and cur_token:
      print("[DEBUG] ", str(type(cur_token)))
      print("\n\n")
      if tokens.check(cur_token):
        return render_template("index.html")
      else:
        # cur_token = hashlib.md5(cur_token.encode()).hexdigest()
        # token is encrypted when removing
        print("[DEBUG] this is cur_token 2" + cur_token)
        if not tokens.remove_token(cur_token):
          print(f"[!] failed to remove token {cur_token}  !")
        resp = redirect(url_for("index"))
        resp.set_cookie("Token", "")
        resp.set_cookie("User", "")

        return resp

  return render_template("index.html")


@app.route('/logout', methods=["GET"])
def logout():
  resp = redirect(url_for("index"))
  resp.set_cookie("Token", "")
  resp.set_cookie("User", "")
  if getcookie(
      request, "Verif"
  ) is not None:  # If it was never set, don't hint the user that there are admin tokens
    resp.set_cookie("Verif", "")
  return resp


# ---------------------------------------------------------------------------------
# hallpass creation dashboard
@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
  first = request.args.get("first")
  # Check for token
  if first:  # If true, skip the token check and let te cookie load
    return """<html><meta http-equiv="Refresh" content="0.5; url='/dashboard'" /></html>"""  # Let the cookie load before invalidating it
  if not get_user_permissions(
      request).can_view_user:  # Not allowed to view dashboard
    return redirect(url_for("index"))
  cur_token = getcookie(request, "Token")
  # None?^^
  # if a token exists you pass
  if cur_token != "" and cur_token:
    if tokens.check(cur_token):
      pass
    # if a token doesent exist create a token
    else:
      # cur_token = hashlib.md5(
      #  cur_token.encode()).hexdigest()
      if not tokens.remove_token(cur_token):
        print(f"[!] failed to remove token {cur_token}  !")
      resp = redirect(url_for("index"))
      resp.set_cookie("Token", "")
      resp.set_cookie("User", "")
      return resp

  else:
    return redirect(url_for("index"))

  user = getcookie(request, "User")  # User uuid (in db)
  uuid = user
  if user is None:
    user = "None"
  # if this is the uuid I dont think uuid in db
  if user not in db:
    if user in names_to_ids:
      user = names_to_ids[user]
    else:  # Remove User id cookie because user id is invalid
      print(f"[*] uuid: {user} is invalid")
      # cur_token = hashlib.md5(
      #  cur_token.encode()).hexdigest()
      if not tokens.remove_token(cur_token):
        print(f"[!] failed to remove token {cur_token}  !")
      resp = redirect(url_for("index"))
      resp.set_cookie("Token", "")
      resp.set_cookie("User", "")
      return resp
  user = db[user]["username"]
  # database is stored with uuids instead of only first name, so users can have the same first name, but a uniqe identifier
  if not user:  # No username cookie
    return redirect(url_for("index"))
  if request.method == "POST":
    if not get_user_permissions(request).can_use_pass:
      redirect(url_for("dashboard"))  # Not allowed to create passes
    room_number = request.form["room_number"]
    destination = request.form["destination"]
    reason = request.form["reason"]
    passes.create_pass(origin=room_number, destination=destination,
                       user=uuid, reason=reason)  # Use uuids for passes please
    return redirect(url_for("passInProgress"))
  return render_template("dashboard.html")


@app.route("/pass", methods=["GET", "POST"])
def passInProgress():
  uuid = getcookie(request, "User")
  print("[DEBUG] ", db[uuid])
  # user = db[uuid]["username"]
  user = uuid  # For passes, we now should use uuids
  #print("[DEBUG] ", passes.get_latest_pass(user=user))
  #print("\n\n")
  if request.method == "POST":
    #print("[DEBUG] ", user)
    passes.finish_pass(passes.get_latest_pass(user))
    return redirect(url_for("dashboard"))
  return render_template("passInProgress.html")


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
  #if not getcookie(request, "User"):  # Userid is required to submit issue
  #return redirect(url_for("index"))
  #uuid = getcookie(request, "User")
  #if not uuid in db:  # user does not exists
  #return redirect(url_for("index"))
  #perms = get_user_permissions(request)
  #if perms.can_submit_issues == False:
  # print(db[uuid]["perms"])
  # print(perms.can_submit_issues)
  #return redirect(url_for("index"))  # User not allowed to submit issues
  return render_template("ReportIssue.html")

@app.route("/loginFeedback", methods=["GET", "POST"])
def loginFeedback():
  return render_template("loginReportIssue.html")

@app.route("/issue", methods=["POST"])
def handle_issue():  # Record the issude
  #if not getcookie(request, "User"):  # Userid is required to submit issue
  #return redirect(url_for("index"))
  if not request.form.get("issue"):
    return redirect(url_for("index"))  # no issue was submited
  if not request.form.get("name"):
    return redirect(url_for("index"))  # no issue was submited
  #uuid = getcookie(request, "User")
  #if not uuid in db:
  #return redirect(url_for("index"))  # User does not exist
  #user = db[uuid]["username"]
  issue_report.write(request.form.get("name"), "UUID not availible",
                     request.form.get("issue"))
  return render_template("issueSubmited.html")


# WARNING! the below code is MESSY! I would not reccomend trying to edit the code, it is super easy to break stuff here


@app.route("/admin", methods=["GET", "POST"])
def admin():
  token = getcookie(request,
                    "Verif")  # Admin token (like user tokens but for admins)
  if token == None:
    token = "None"  # No token
  if admin_token.check(token):
    return render_template("admin/admin.html").replace("MESSAGE",
                                                       "")  # Admin dashboard
  return render_template("admin/index.html")  # Admin login


@app.route("/tokdump", methods=["GET"])
def dump_tok():  # Dump all the tokens and return them into a webpage
  token = getcookie(request, "Verif")
  if token == None:
    token = "None"
  if not admin_token.check(token):
    return redirect(url_for("admin"))  # Dashboard
  liz = ""  # Html version of tokens
  lizt = {}  # Tokens all together
  for i in tokens.data:
    lizt[i] = tokens.data[i]  # Add token to lizt
  lizt[""] = "ADMIN TOKENS:"  # Admin tokens
  for i in admin_token.data:
    lizt[i] = admin_token.data[i]  # add admin token to lizt
  for i in lizt:
    liz += f"<p><b>{i}:</b><br>{lizt[i]}</p><br>"  # convvert the tokens to html
  return f"""<html><body style="color : white; background : black">{liz}</body></html>"""  # return html


@app.route("/devdump", methods=["GET"])
def dump_db():  # Dump the entire database and return it as html
  token = getcookie(request, "Verif")
  if token == None:
    token = "None"
  if not admin_token.check(token):
    return redirect(url_for("admin"))  # Back to dashboard
  liz = ""  # html of db
  lizt = {}  # dict of db
  for i in db:
    lizt[i] = dict(db[i])  # add items to dict
  for i in lizt:
    liz += f"<p><b>{i}:</b><br>{lizt[i]}</p><br>"  # convert dict to html
  return f"""<html><body style="color : white; background : black">{liz}</body></html>"""  # Return html


RefrenceList = [
]  # User classes need to have a global refrence or they will be discarded


@app.route("/cuser", methods=["POST"])
def Create_User():  # Create a user page
  token = getcookie(request, "Verif")
  if token == None:
    token = "None"
  if not admin_token.check(token):
    return redirect(url_for("admin"))
  global RefrenceList
  sched = []
  errors = 0
  for i in request.form.get("schedule").split(" "):  # Convert schedule to list
    if i != "":
      try:
        sched.append(int(i))  # add to dchedule
      except:
        errors += 1
  user = User(first_name=request.form.get("username"),
              last_name=request.form.get("lastname"),
              schedule=sched,
              username=request.form.get("username"),
              password=request.form.get("password"),
              perms=Permissions.get_permissions(
                request.form.get("AccountType")))  # make the user
  RefrenceList.append(user)  # Refrence list (look at refrence list comment)
  gen_ids()  # New uuid, so regenerate the name to uuid list
  print(
    f"[*] Admin account externally created user with name '{request.form.get('username')}'"
  )  # Log what the admin acc is doing
  return f"<html><p>Action completed with {errors} errors</p><br><br><br><p>Info:</p><br><br><p>First name: {request.form.get('username')}</p><br><br><p>Last name: {request.form.get('lastname')}</p><br><br><p>Schedule: {str(sched)}</p><br><br><p>Password: {request.form.get('password')}</p><br><br><br><a href={url_for('admin')}>Back</a></html>"  # Return the result


@app.route("/cmd", methods=["POST"])
def command():  # Run a command
  global db
  token = getcookie(request, "Verif")
  if token == None:
    token = "None"
  if not admin_token.check(token):
    return redirect(url_for("admin"))  # admin dashboard
  out1 = "No output."  # Command output
  f = StringIO()
  with redirect_stdout(f):  # redirect output to stringio
    try:
      eval(request.form.get("command"))  # Run cmd
    except:
      try:
        exec(request.form.get("command"))  # Run cmd if it failed the first time
      except Exception as e:
        print(f"Failed both exec and eval\n{str(e)}")
  out1 = f.getvalue()  # Get output of stringio
  return render_template("/admin/RunCommand.html").replace(
    "<!--MESSAGE-->", f"<p>Output:<br><br>{out1}<br><br><br><br><br><br></p>"
  )  # Return the command results


@app.route("/handle", methods=["POST"])
def handle_admin():  # Handle admin dashboard selections
  msg = ""  # Message to include in html
  token = getcookie(request, "Verif")
  if token == None:
    token = "None"
  if not admin_token.check(token):
    return redirect(url_for("admin"))  # Back to dashboard
  # Handle form items in here
  if request.form.get("cleandb"):  # clean duplicate db values
    print("[*] Admin account externally requested clean_db()")  # log cmd
    clean_db()
    msg = "<p>Cleaned data base</p>"  # message
  if request.form.get("cleardb"):  # clear db
    print("[*] Admin account externally requested to clear the db")  # log cmd
    delete_all_keys()
    msg = "<p>Successfully deleted all keys</p>"  # message
  if request.form.get("DoCommand"):  # Go to the command running page
    return render_template("/admin/RunCommand.html")  # cmd runing page
  if request.form.get("cleanTokens"):  # remove invalid tokens
    print("[*] Admin account externally requested to clean tokens")  # log cmd
    clean_tokens(admin_token)  # clean admin tokens
    clean_tokens(tokens)  # clean user tokens
    msg = "<p>Cleaned tokens</p>"
  if request.form.get("createUser"):  # create user
    return render_template("/admin/createuser.html")  # Return create user page
  return render_template("/admin/admin.html").replace(
    "MESSAGE", msg)  # return admin dashboard with msg


@app.route("/alog", methods=["POST"])
def alog():  # The login handler
  token = getcookie(request, "Verif")
  if token == None:
    token = "None"
  if admin_token.check(token):
    return redirect(url_for("admin"))  # return admin dashboard redirect
  passwordd = tok = hashlib.md5(
    request.form.get("password").encode()).hexdigest()  #ENCRYPT
  for i in db:  # loop through the database
    if i == "Pass":  # Ignore the passes data base
      continue
    if request.form.get("username") == db[i][
        "first_name"]:  # Check if username is the first name
      if passwordd == db[i]["password"]:  # check if password is the password
        if db[i]["perms"][
            "can_view_dev"]:  # check if user has permission to view developer pages
          resp = redirect(url_for("alog"))  # redirect here again
          resp.set_cookie("Verif",
                          admin_token.generate_token())  # set admin token
          resp.set_cookie("User", i)  # set user uuid
          return resp
  return redirect(url_for("admin"))  # admin dashboard


# this comment ends the messy code section

#starting to define the sections within the website

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

@app.route("/loginAbout")
def loginAbout():
  return render_template("loginAbout.html")

@app.errorhandler(500)
def Server_error(error):
  return """<html><link type="text/css" rel="stylesheet" href="{{ url_for('static', filename='style.css')}}"/><p>500: Internal server error ☹</p></html>""", 500


@app.errorhandler(404)
def page_not_found(error):
  return """<html><link type="text/css" rel="stylesheet" href="{{ url_for('static', filename='style.css')}}"/><p>404: Page not found ☹</p></html>""", 404


@app.errorhandler(405)
def Method_not_allowed(error):
  return """<html><link type="text/css" rel="stylesheet" href="{{ url_for('static', filename='style.css')}}"/><p>405: Method not allowed ☹</p></html>""", 405


@app.errorhandler(403)
def denied(error):
  return """<html><link type="text/css" rel="stylesheet" href="{{ url_for('static', filename='style.css')}}"/><p>403: Access denied ☹</p></html>""", 403


if __name__ == "__main__":
  app.run(
    debug=True, host='0.0.0.0', port=8080
  )  # Host on port 8080, because linux wants root privleges for the lower ports and makes the program slower on replit
