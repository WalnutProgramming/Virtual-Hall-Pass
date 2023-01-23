from replit import db
import time as time
import datetime as datetime

#passes = len(db.prefix("pass")) + 1


class PassStore:
  """
  A class to handle and store passes
  You must load the pass' dict to interact with the class
  """

  def __init__(self, admin_password="password"):
    self.data = {}
    self.a = admin_password
    self.load()

  def load(self):
    """
    Load passes into the internal data from database
    """

    if not "Pass" in db:
      db["Pass"] = {}
    self.data = db["Pass"]

  def write(self):
    """
    Write passes to the database from internal data
    """

    db["Pass"] = self.data

  def create_pass(self, origin, destination, user):
    """
    Create a pass object and store it

    return: Pass(origin, destination, user)
    """
    if not user in self.data:
      self.data[user] = []
    tempass = Pass(origin, destination, user)
    self.data[user].append(tempass.dict())
    self.write()
    return tempass

  def get_user_passes(self, user):
    """
    Get all passes of a user

    return: list
    """
    if user in self.data:
      return self.data[user]
    else:
      return []

  def get_latest_pass(self, user):
    """
    Get the most recent pass from the specified user based on start times

    return: Pass(origin, destination, user) OR None
    """

    greatest = None
    if user in self.data:
      for i in self.data[user]:
        b = Pass("4", "4", "4")
        b.load_dict(i)
        if greatest is None:
          greatest = b
        if b.start_time > greatest.start_time:
          greatest = b

    return greatest

  def clear_all_passes(self, password):
    """
    Clear all passes stored, requiring the admin password.

    return: None
    """

    self.data = {}
    self.write()

  def clear_user_passes(self, password, user):
    """
    Clear the pass history of a user, requiring the admin password.

    return: boolean
    """

    if password != self.a:
      return False

    if user in self.data:
      self.data[user] = []
      self.write()
      return True
    return False

  def finish_pass(self, pas):
    """
    Finish a pass

    returns: None
    """

    #    pas["end_time"] = time.time()
    #   pas["elapsed_time"] = pas["end_time"] - pas["start_time"]
    #  print(pas)
    pas.set_end_time(time.time())

  def get_user_passes_sorted(self, user, reverse=False):
    """
    Get all passes of a user, but in a sorted list from most recent to least recent
    (or opposite order if reverse is True)

    return: list
    """

    sort = []
    if user in self.data:
      sort = []
      for i in self.data[user]:
        temp = Pass("j", "j", "j")
        temp.load_dict(i)
        sort.append(temp)
      sort = sorted(sort, key=lambda e: e.start_time, reverse=reverse)
    return sort


class Pass:

  def __init__(self, origin, destination, user):
    self.start_time = time.time()
    self.end_time = None
    self.origin = origin
    self.destination = destination
    date = datetime.datetime.now()
    # month day year
    self.date = date.strftime("%B %d, %Y")
    self.user = user
    self.elapsed_time = None

  # getters & setters
  def get_start_time(self):
    return self.start_time

  def get_end_time(self):
    if self.end_time != None:
      return self.end_time
    return "Pass in progress"

  def get_origin(self):
    return self.origin

  def get_destination(self):
    return self.destination

  def get_date(self):
    return self.date

  def set_elapsed_time(self):
    self.elapsed_time = self.end_time - self.start_time

  def set_end_time(self, end_time):
    self.end_time = end_time
    self.set_elapsed_time()
    print("[DEBUG] ", self.elapsed_time)
    #print("pass completed " + self.stringify())
    #db["pass" + str(passes)] = self.stringify()
    #Might be causing errs

  def dict(self):
    """
    Loads all variables fron the function into a dict
    """
    dict = {}
    for i in dir(self):
      if not i.startswith("__") and not callable(self.__getattribute__(i)):
        dict[i] = self.__getattribute__(i)
    return dict

  def load_dict(self, dict):
    """
    Used to load the class from a dict (returned by dict())
    """
    for i in dict:
      self.__setattr__(i, dict[i])

  def stringify(self):
    return "{}, origin : {}, destination : {}, date : {}, start_time: {}, end_time : {}, elapsed_time : {} seconds".format(
      self.user, self.origin, self.destination, self.date,
      datetime.datetime.fromtimestamp(self.start_time).strftime("%H:%M"),
      datetime.datetime.fromtimestamp(self.end_time).strftime("%H:%M"),
      self.elapsed_time)
