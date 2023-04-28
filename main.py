import argparse
from Parser.md2block import read_file
from NotionClient import NotionSyncDatabase
from uploader import Md2NotionUploader
import os
def get_parameter():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", '-f',help="input file_path")
    parser.add_argument("--connection_key", type=str, help="the notion connection key")
    parser.add_argument("--database_id", type=str, help="the notion database_id")
    parser.add_argument("--smms_token", type=str, help="the smms token")
    parser.add_argument("--start_line", default=0, type=int, help="the start line of the update")
    
    args = parser.parse_args()
    return args


def upload_single_file(filepath, client, uploader,filename=None, start_line = 0):
    if filename is None:
        filename = filepath.split('/')[-1]
    # create a new page for this file
    client.create_new_page(filename)
    page_id = client.get_page_id_via_name(filename)
    # get the notion style block information
    notion_blocks = read_file(filepath)
    uploader.local_root = os.path.dirname(filepath)
    for i,content in enumerate(notion_blocks):
        if i < start_line:continue    
        print(f"uploading line {i},............", end = '')
        uploader.uploadBlock(content, client.notion, page_id)
        print('done!')


if __name__ == '__main__':

   
    args = get_parameter()
    connection_key = args.connection_key
    database_id  = args.database_id
    client      = NotionSyncDatabase(connection_key, database_id)
    uploader       = Md2NotionUploader(image_host='smms', smms_token=args.smms_token)
    filepath   = args.file_path
    start_line = args.start_line
    upload_single_file(filepath, client, uploader, start_line = start_line)