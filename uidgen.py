from datetime import datetime
import random

def generateuid():
    now = str(datetime.now())
    now = now.replace("-", "")
    now = now.replace(":", "")
    now = now.replace(" ", "")
    uid = now[0:12]

    return uid
