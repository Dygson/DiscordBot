import os
from pathlib import Path
myfile = "Discord_Bot_Python_Tutorial_2023_Discord_Bot_Tutorial_Python_Projects_for_Resume_Simplilearn-[7RLqCfbs3vg].webm"
print("Files in a directory -->",os.listdir())
print("We can see a file created succesfully")
print("-----------------------------------------------------")
# If file exists, delete it.
if os.path.isfile(myfile):
    os.remove(myfile)
    print("Favtutor file deleted using remove() function")
    print("Current files in directory -->",os.listdir())
    print("-----------------------------------------------------")
else:
    # If it fails, inform the user.
    print("Error: %s file not found" % myfile)