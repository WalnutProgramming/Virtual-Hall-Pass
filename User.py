from replit import db
from uuid import uuid4
from Permissions import Permission
import hashlib

#classes = {
#  1: "band",
#  2: "chemistry",
#  3: "math",
#  4: "social studies",
#  5: "Foriegn language",
#  6: "english",
#  7: "physics",
#  8: "computer science"
#}

#Using a list is simpler.
classes = [
  None,  #Value 0 has no class, so we start a value 1
  "band",
  "chemistry",
  "math",
  "social studies",
  "Foriegn language",
  "english",
  "physics",
  "computer science"
]


def index(dict, key):

  for i in dict:
    if dict[i] == key:
      return i
  return False

#TODO: store user passwords encrypted, it is unsafe to store them raw in the database
class User:

  def __init__(self,
               first_name,
               last_name,
               schedule,
               username,
               password,
               perms: Permission = Permission()):
    global db
    self.perms = perms
    self.password_encrypted = False
    self.first_name = first_name
    self.last_name = last_name
    #self.pass_history = []  # Hall passes history
    self.schedule = []
    self.id = uuid4()
    self.username = username
    self.password = password
    self.encrypt_password()
    for c in schedule:
      try:
        self.schedule.append(classes[c])
      except:
        if c in classes:
          self.schedule.append(c)
        else:
          print(f"[!] Class '{c}' not listed, ignoring class.")
    db[self.id] = self.generate_dict()

  def encrypt_password(self):
    if self.password_encrypted:
      return
    self.password = hashlib.md5(self.password.encode()).hexdigest()
    self.password_encrypted = True

  def compare_passwords(self, password):
    if not self.password_encrypted:
      return False
    password = hashlib.md5(password.encode()).hexdigest()
    if password == self.password:
      return True
    return False
  
  def get_first_name(
    self
  ):  #You may not need this function to get the first name, you can do new_pass.first_name to save time
    return self.first_name

  def get_last_name(self):
    return self.last_name

  def get_schedule(self):
    return self.schedule

  def get_username(self):
    return self.username
    
  def get_password(self):
    return self.password

  def set_first_name(self, first_name):
    self.first_name = first_name

  def set_last_name(self, last_name):
    self.last_name = last_name

  def set_classes(self, classes):
    self.classes = classes

  def set_pass_status(self, pass_status):
    self.pass_status = pass_status

  def set_permissions(self, perms_dict):
    temp = Permission()
    temp.load_dict(perms_dict)
    self.perms = temp

  def generate_dict(self):
    return {
      "first_name": self.first_name,
      "last_name": self.last_name,
      "schedule": self.schedule,
      "username": self.username,
      "password": self.password,
      "perms": self.perms.dict()
      #"passes": self.pass_history
    }

  def stringify(self):
    return "first_name : {}, last_name : {}, classes : {}".format(
      self.first_name, self.last_name, self.classes)
