import os

class IssueReporter:
  def __init__(self, file):
    self.file = file
    if not os.path.exists(file):
      with open(file, "w") as e:
        e.write("*")

  def write(self, user, uuid, issue):
    with open(self.file, "a") as e:
      add = f"""Username: {user}
      Uuid: {uuid}
      Report: {issue}
      \n
      """
      e.write(add)
