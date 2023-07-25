import argparse
import yaml

from NotionClient import NotionSyncDatabase
from uploader import Md2NotionUploader

from main import upload_single_file


def arg_parser():
    parser = argparse.ArgumentParser(prog='Markdown Notion Uploader')

    parser.add_argument(
        "-c", "--src",
        dest="src",
        type=str,
        required=True,
        help="markdown source"
    )

    parser.add_argument(
        "--cfg",
        dest="cfg",
        type=str,
        required=True,
        help="notion account config file"
    )

    return parser.parse_args()


def parse_notion_cfg(notion_cfg_file):
    with open(notion_cfg_file, 'r') as fin:
        cfg = yaml.safe_load(fin)
    
    cfg["database_id"] = cfg["database_id"][:8] + "-" + \
        cfg["database_id"][8:12] + "-" + \
        cfg["database_id"][12:16] + "-" + \
        cfg["database_id"][16:20] + "-" + \
        cfg["database_id"][20:]

    return cfg


def upload_to_notion(md_src, notion_cfg_file):
    cfg = parse_notion_cfg(notion_cfg_file)

    client = NotionSyncDatabase(cfg["notion_token"], cfg["database_id"])
    uploader = Md2NotionUploader(image_host='smms', smms_token=cfg["smms_token"])

    upload_single_file(md_src, client, uploader, start_line=0)


if __name__ == "__main__":
    args = arg_parser()
    upload_to_notion(args.src, args.cfg)