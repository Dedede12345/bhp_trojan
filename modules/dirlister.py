import os

def run(**args):
    print("[*] In dirlister module.")
    files = os.listdir(os.getcwd())
    return str(files)