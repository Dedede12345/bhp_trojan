import os

def run(**args):
    print("[*] In dirlister module.")
    files = os.listdir("D:\BHP\Chapter06")
    return str(files)