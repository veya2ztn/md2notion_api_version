import re,os,argparse

class Md2NotionUploader:
    image_host_object = None
    local_root = "markdown_notebook"
    def __init__(self, image_host='smms', onedrive_client_id=None,client_secret=None,auth=False,
                       smms_token = None):
        self.image_host = image_host
        self.smms_token = smms_token
        self.onedrive_client_id = onedrive_client_id
        self.client_secret      = client_secret
        self.auth = auth
    
    def _get_onedrive_client(self):
        self.onedrive = self.image_host_object
        if self.onedrive is None and self.onedrive_client_id is not None:
            from ImageHosting.Onedrive import Onedrive_Hosting
            self.onedrive = Onedrive_Hosting(self.onedrive_client_id, self.client_secret)
            if self.auth:self.onedrive.initilize()
            self.onedrive._obtain_drive()
        self.image_host_object = self.onedrive
        return self.image_host_object
    
    def _get_smms_client(self):
        self.smms = self.image_host_object
        if self.smms is None and self.smms_token is not None:
            from ImageHosting.SMMS import SMMS_Hosting
            self.smms    = SMMS_Hosting(token=self.smms_token)
        self.image_host_object = self.smms
        return self.image_host_object
    
    @staticmethod
    def split_text(text):
        text = re.sub(r'<img\s+src="(.*?)"\s+alt="(.*?)"\s+.*?/>', r'![\2](\1)', text)
        out = []
        double_dollar_parts = re.split(r'(\$\$.*?\$\$)', text, flags=re.S)

        for part in double_dollar_parts:
            if part.startswith('$$') and part.endswith('$$'):
                # replace {align} with {aligned}
                part = part.replace('{align}', '{aligned}')
                # strictly replace `\<newline>` with '\\<newline>'
                # e.g., "\\<newline>" will not be replaced
                pattern = r"(.*[^\\])(\\\n)"
                part = re.sub(pattern, r"\1\\\\\n", part)
                out.append(part)
            else:
                image_parts = re.split(r'(!\[.*?\]\(.*?\))', part)
                out.extend(image_parts)
        out = [t for t in out if t.strip()!='']
        return out

    def blockparser(self, s, _type="paragraph"):
        parts = self.split_text(s)
        result = []
        for part in parts:
            if part.startswith('$$'):
                expression = part.strip('$$')
                result.append({
                    "equation": {
                        "expression": expression.strip()
                    }
                })
            elif part.startswith('![') and '](' in part:
                caption, url = re.match(r'!\[(.*?)\]\((.*?)\)', part).groups()
                url = self.convert_to_oneline_url(url)
                result.append({
                    "image": {
                        "caption": [],#caption,
                        "type": "external",
                        "external": {
                            "url": url
                        }##'embed': {'caption': [],'url': url} #<-- for onedrive
                    }
                })
            else:
                result.append({
                    _type: {
                        "rich_text": self.sentence_parser(part)
                    }
                })

        return result

    @staticmethod
    def is_balanced(s):
        single_dollar_count = s.count('$')
        double_dollar_count = s.count('$$')

        return single_dollar_count % 2 == 0 and double_dollar_count % 2 == 0

    @staticmethod
    def parse_annotations(text):
        annotations = {
            'bold': False,
            'italic': False,
            'strikethrough': False,
            'underline': False,
            'code': False,
            'color': 'default'
        }

        # Add bold
        if '**' in text or '__' in text:
            annotations['bold'] = True
            text = re.sub(r'\*\*|__', '', text)

        # Add italic
        if '*' in text or '_' in text:
            annotations['italic'] = True
            text = re.sub(r'\*|_', '', text)

        # Add strikethrough
        if '~~' in text:
            annotations['strikethrough'] = True
            text = text.replace('~~', '')
        
        if '`' in text:
            annotations['code'] = True
            text = text.replace('`', '')
        
        return annotations, text

    
    def convert_to_oneline_url(self,url):
        # check the url is local. (We assume it in Onedrive File)
        
        if "http" in url:return url
        if (".png" not in url) and (".jpg" not in url) and (".svg" not in url):return url
        ## we will locate the Onedrive image 
        if self.image_host == 'onedrive':
            return self.convert_to_oneline_url_onedrive(url)
        elif self.image_host == 'smms':
            return self.convert_to_oneline_url_smms(url)
        else:
            raise "Invalid Image Hosting"
    def convert_to_oneline_url_onedrive(self,url):
        if os.path.exists(url):
            # the script path is at root
            path = os.path.abspath(url)
            drive, path = os.path.splitdrive(path)
            onedrive_path = '/markdown_notebook'+path.split('markdown_notebook', 1)[1]
        else:
            # the script path is not at root. then we whould use the self.local_root
            url = url.strip('.').strip('/')
            onedrive_path = f'/{self.local_root}/{url}'
        onedrive = self._get_onedrive_client()
        url = onedrive.get_link_by_path(onedrive_path)
        #url = onedrive.get_final_link_by_share(url)
        return url    
    def convert_to_oneline_url_smms(self,url):
        # if the url is relative path, the root dir should be declared
        smms = self._get_smms_client()
        
        smms.upload_image(os.path.join(self.local_root, url))
        return smms.url
    
    def sentence_parser(self, s):
        if not self.is_balanced(s):
            raise ValueError("Unbalanced math delimiters in the input string.")

        # Split string by inline math and markdown links
        parts = re.split(r'(\$.*?\$|\[.*?\]\(.*?\))', s)
        result = []

        for part in parts:
            if part.startswith('$'):
                expression = part.strip('$')
                result.append({
                    "type": "equation",
                    "equation": {
                        "expression": expression
                    }
                })
            elif part.startswith('[') and '](' in part:
                # Process style delimiters before processing link
                style_parts = re.split(r'(\*\*.*?\*\*|__.*?__|\*.*?\*|_.*?_|~~.*?~~|`.*?`)', part)
                for style_part in style_parts:
                    annotations, clean_text = self.parse_annotations(style_part)
                    if clean_text.startswith('[') and '](' in clean_text:
                        link_text, url = re.match(r'\[(.*?)\]\((.*?)\)', clean_text).groups()
                        
                        if (not url.startswith('http://')) and (not url.startswith('https://')):
                            print("[WARN] Does not support uploading local file:\n\t`{}`".format(url))
                            url = "https://local/" + url

                        result.append({
                            "type": "text",
                            "text": {
                                "content": link_text,
                                "link": {
                                    "url": url
                                }
                            },
                            "annotations": annotations,
                            "plain_text": link_text,
                            "href": url
                        })
                    elif clean_text:
                        result.append({
                            "type": "text",
                            "text": {
                                "content": clean_text,
                                "link": None
                            },
                            "annotations": annotations,
                            "plain_text": clean_text,
                            "href": None
                        })
            else:
                # Split text by style delimiters
                style_parts = re.split(r'(\*\*.*?\*\*|__.*?__|\*.*?\*|_.*?_|~~.*?~~|`.*?`)', part)
                for style_part in style_parts:
                    annotations, clean_text = self.parse_annotations(style_part)
                    if clean_text:
                        result.append({
                            "type": "text",
                            "text": {
                                "content": clean_text,
                                "link": None
                            },
                            "annotations": annotations,
                            "plain_text": clean_text,
                            "href": None
                        })

        return result

    def convert_to_raw_cell(self, line):
        children = { "table_row": {"cells":[]}}
        for content in line:
            #print(uploader.blockparser(content,'text'))
            cell_json =  self.sentence_parser(content)
            children["table_row"]["cells"].append(cell_json)
        return children

    def convert_table(self, _dict):

        parents_dict = {
                'table_width': 3,
                'has_column_header': False,
                'has_row_header': False,
                'children':[]
        }
        assert 'rows' in _dict
        if 'schema' in _dict and len(_dict['schema'])>0:
            parents_dict['has_column_header'] = True
            line = [v['name'] for v in _dict['schema'].values()]
            parents_dict['children'].append(self.convert_to_raw_cell(line))

        width = 0
        for line in _dict['rows']: 
            width = max(len(line),width)
            parents_dict['children'].append(self.convert_to_raw_cell(line))
        parents_dict['table_width']=width
        return [{'table':parents_dict}]
    
    def convert_image(self, _dict):
        url = _dict['source']
        url = self.convert_to_oneline_url(url)
        assert url is not None
        return [{"image": {"caption": [],"type": "external",
                           "external": {"url": url}
                          }
                }]
    
    def uploadBlock(self,blockDescriptor, notion, page_id, mdFilePath=None, imagePathFunc=None):
        """
        Uploads a single blockDescriptor for NotionPyRenderer as the child of another block
        and does any post processing for Markdown importing
        @param {dict} blockDescriptor A block descriptor, output from NotionPyRenderer
        @param {NotionBlock} blockParent The parent to add it as a child of
        @param {string} mdFilePath The path to the markdown file to find images with
        @param {callable|None) [imagePathFunc=None] See upload()

        @todo Make mdFilePath optional and don't do searching if not provided
        """
        new_name_map = {
            'text':'paragraph',
            'bulleted_list':'bulleted_list_item',
            'header':'heading_1',
            'sub_header':'heading_2',
            'sub_sub_header':'heading_3',
            'numbered_list':'numbered_list_item'
        }
        blockClass = blockDescriptor["type"]
        
        old_name = blockDescriptor['type']._type
        new_name = new_name_map[old_name] if old_name in new_name_map else old_name
        
        if new_name == 'collection_view':
            # this is a table
            content_block = self.convert_table(blockDescriptor)
        elif new_name == 'image':
            # this is a table
            content_block = self.convert_image(blockDescriptor)
        elif 'title' in blockDescriptor:
            content = blockDescriptor['title']
            content_block = self.blockparser(content,new_name)
        elif new_name == 'code':
            language = blockDescriptor['language']
            content = blockDescriptor['title_plaintext']
            content_block = self.blockparser(content,new_name)
            content_block[0]['code']['language'] = language.lower()
        else:
            content_block = [{new_name:{}}]
        response      = notion.blocks.children.append(block_id=page_id, children=content_block)
        
        blockChildren = None
        if "children" in blockDescriptor:
            blockChildren = blockDescriptor["children"]
        if blockChildren:
            child_id = response['results'][-1]['id']
            for childBlock in blockChildren:
                ### firstly create one than 
                self.uploadBlock(childBlock, notion, child_id, mdFilePath, imagePathFunc)

if __name__ == '__main__':
    # get your smms token from  https://sm.ms/home 
    ## you can also use usename and password. See the code in ImageHosting/SMMS.py
    # you can also use use other image host, such as imgur, qiniu, upyun, github, gitee, aliyun, tencent, jd, netease, huawei, aws, imgbb, smms, v2ex, weibo, weiyun, zimg
    ## the onedrive image hosting is supported, but the onedrive can only provide framed view which is not a direct link to the image.
    uploader       = Md2NotionUploader(image_host='smms', smms_token='{your-smms-token}')
