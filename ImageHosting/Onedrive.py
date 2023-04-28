
import re,requests
from O365 import Account
import urllib.parse
class Onedrive_Hosting:
    def __init__(self,client_id, client_secret):
        
        #credentials = ('9ab4802e-e6f8-4235-a219-077552f248f9', 'voj8Q~akDfEWnTArqkPvsreCyaD_2JamKCNuUdu~')
        credentials  = (client_id, client_secret)
        self.account = Account(credentials)
        self.drive   = None
    def initilize(self):
        scopes = ['onedrive_all']
        if self.account.authenticate(scopes=scopes):
            print('Authenticated!')
            
    def _obtain_drive(self):
        self.storage = self.account.storage()
        self.drive   = self.storage.get_default_drive()
        
    def get_link_by_path(self,path):
        if self.drive is None:
            self._obtain_drive()
        #item = self.drive.get_item_by_path('/markdown_notebook/test.assets/images.png')
        item = self.drive.get_item_by_path(path)
        share_link = None
        if item:
            permission = item.share_with_link(share_type='embed')
            share_link = permission.share_link
        #print(share_link)
        return share_link
    
    def get_final_link_by_share(self,url):
        
        url = urllib.parse.unquote(url)
        resid = re.search(r'resid=([^&]+)', url).group(1)
        authkey = re.search(r'authkey=([^&]+|$)', url).group(1)
        cid = re.search(r'([^!]+)', resid).group(1).lower()
        recontrust_url = f'https://onedrive.live.com/download.aspx?cid={cid}&resid={resid}&parId={resid}&authkey={authkey}'
        response = requests.get(recontrust_url, allow_redirects=True)
        final_url = response.url
        image_url = final_url.split(".png")[0] + ".png"
        print(f"cid: {cid} resid: {resid} authkey: {authkey}")
        print(f"build recontrust_url: {recontrust_url}")
        print(f"get image_url: {image_url}")
        return image_url