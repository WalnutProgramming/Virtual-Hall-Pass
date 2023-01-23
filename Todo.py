"""
This is a program that will gather all of our "#TODO:" arguments in code, and put them
in one place!
"""

#WIP

import os

todos = {}

for i in os.listdir("./"):
  if i.endswith(".py") and i != "Todo.py":
    with open(f"./{i}") as file:
      content = file.read()
      content = content.split("\n")
      linenum = 1
      for line in content:
        if "#TODO:" in line:
          temp = line.split("#TODO:")
          if len(temp) > 1:
            todos["#TODO: " + temp[1]] = {"line": linenum, "file": i}
          else:
            todos["#TODO: " + temp[0]] = {"line": linenum, "file": i}
        linenum += 1

mainstring = "## TODO (auto generated):\n"

for i in todos:
  mainstring += f"- {i}  at line {todos[i]['line']} in file {todos[i]['file']}\n\n"

with open("plan.md", "r") as file:
  content = file.read()

content2 = content.split("## TODO (auto generated):")

if len(content2) > 2:
  content = content + mainstring
else:
  content = content2[0] + mainstring

with open("plan.md", "w") as file:
  file.write(content)

print("[*] Registered todo comments")
