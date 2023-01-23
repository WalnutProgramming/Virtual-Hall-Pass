import os
import time
import Todo
"""
Overall utility file!
"""

time_now = time.ctime()
day_time = time.gmtime().tm_yday


def cleanup_backups(loud=False):  #Delete backups older than 5 days
  for b in os.listdir("./backups"):
    for i in os.listdir(f"./backups/{b}"):
      try:
        day = int(i[0])
      except:
        continue
      if day <= day_time - 5 or day >= day_time + 5:
        os.remove(f"./backups/{b}/{i}")
        if loud:
          print(f"Removed {b} backup older than five days")
  if loud:
    print("Finished backup cleanup")


def backup(file, loud=False):  #Backup file based on current day of the year
  if loud:
    print("Creating backup")
  filefoldername = file.split(".")[0]
  with open(f"./{file}", "r") as e:
    cont = e.read()
  cont = f"BackupTime = '{time_now}'#Automatically generated backup time\n" + cont
  if not os.path.exists("./backups"):
    os.mkdir("./backups")
  if not os.path.exists(f"./backups/{filefoldername}"):
    os.mkdir(f"./backups/{filefoldername}")
  with open(f"./backups/{filefoldername}/{day_time}{file}", "w") as e:
    #print("passing")
    e.write(cont)
  if loud:
    print(f"Backup saved in ./backups/{filefoldername}/{day_time}{file}")


backup("main.py")
backup("Token.py")
backup("Pass.py")
backup("User.py")
backup("Todo.py")
backup("backup.py")
cleanup_backups()
print("[*] Finished backup routine")
