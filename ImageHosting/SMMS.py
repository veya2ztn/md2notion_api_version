# (C) https://github.com/nifanle7/md_img_uploader

import requests
import json 
import re

class SMMS_Hosting(object):
    # init with username and password
    def __init__(self, username=None, password=None,token=None):
        self.username = username
        self.password = password
        self.token    = token if token is not None else self.get_api_token()
        self.headers = {'Authorization': self.token}
        self.profile = None
        self.history = None
        self.upload_history = None
        self.url = None
        self.root= 'https://sm.ms/api/v2/'
    # user
    def get_api_token(self):
        data = {
            'username': self.username,
            'password': self.password,
        }
        url = self.root+'token'
        res = requests.post(url, data=data).json()
        return res['data']['token']

    # user
    def get_user_profile(self):
        url = self.root+'profile'
        res = requests.post(url, headers=self.headers).json()
        self.profile = res['data']
        print(json.dumps(res, indent=4))

    # image
    def clear_temporary_history(self):
        data = {
            'format': 'json'
        }
        url = self.root+'clear'
        res = requests.get(url, data=data).json()
        print(json.dumps(res, indent=4))

    # image
    def view_temporary_history(self):
        url = self.root+'history'
        res = requests.get(url).json()
        self.history = res['data']
        print(json.dumps(res, indent=4))

    # image
    def delete_image(self, hash):
        url = self.root+'delete/'+hash
        res = requests.get(url).json()
        print(json.dumps(res, indent=4))

    # image
    def view_upload_history(self):
        url = self.root+'upload_history'
        res = requests.get(url, headers=self.headers).json()
        self.upload_history = res['data']
        print(json.dumps(res, indent=4))

    # image
    def upload_image(self, path):
        try:
            files = {'smfile': open(path, 'rb')}
            url = self.root+'upload'
            res = requests.post(url, files=files, headers=self.headers).json()
            if res['success']:
                self.url = res['data']['url']
                # print(json.dumps(res, indent=4))
                print(self.url)
                # upload repeated， get the url
            elif 'Image upload repeated' in res['message']:
                self.url = re.findall('(http.*\.(?:jpg|jpeg|png|webp|gif))', res['message'])[0]
                print(res['message'])
            else:
                print(res['message'])
        except Exception as e:
            print(e)