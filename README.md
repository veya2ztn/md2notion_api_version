# md2notion_api_version
Use Notion API to upload .md file to notion.so for typora writing style.

## Installation

Clone the repository and install dependencies:

```bash
pip install md2notion
git clone https://github.com/veya2ztn/md2notion_api_version.git
cd notion-markdown-uploader

```

## Configuration

### Setup Notion Connection

Create a new integration in your Notion account and obtain the integration token.

The preset configuration work for `all markdown files are collected in one database`. 

For example, all markdown files appear as follow:

![image-20230428191459321](https://raw.githubusercontent.com/veya2ztn/md2notion_api_version/main/figures/image-20230428191459321.png)

We use [notion api](https://developers.notion.com/reference) to update, thus you need 

Step1: Create a "[connection](https://www.notion.so/my-integrations)" first and obtain its `Secrets` in the connection configuration page. 

Step2: link `connection` to the synced database page:

- Open the database page ,
- Press setting button at right-upper
- Find `Add Connection` and link the page

> It is possible to handle the whole notion project via Api and I recommend to read [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) and [API reference](https://developers.notion.com/reference).

----

After setup, you need record

- The **Database ID**. (For example, `88c52f937663497d93b245934c741f39`. )
  - You need manually add `-` and obtain the true id `88c52f93-7663-497d-93b2-45934c741f39`
- The **Connection Secrets**.

### Setup SM.MS

We use [SMMS](https://sm.ms/) to store local image, thus you need provide the `SMMS token` [here](https://sm.ms/home/apitoken).

> You can use `usename` and `password` directly. See class `SMMS_Hosting`.

> Only local image will be shared to SM.MS, any url start with`http`  get ignored.

> It is easy to  implement other image hosting. For example, I also implement the `Onedrive_Hosting`. But it is impossible to create a permanent image link from OneDrive side. The only alternative way is use the `embed` link by `item.share_with_link(share_type='embed')` and upload via `{'embed': {'caption': [],'url': url}}`. See `Onedrive_Hosting` and `Md2NotionUploader._get_onedrive_client` for detail.

> Currently, the notion API [doesn't support](https://developers.notion.com/reference/file-object) upload files.

----

After setup, you need record

- The **SMMS token**.

## Usage

```
python main.py -f <your_file_path> --connection_key <Connection Secrets> --database_id <Database ID> --smms_token <SMMS token>
```

The program will create a database item as same name as the file name.

The upload processing is line by line, if your processing failed at some line, add `start_line=?` to skip uploaded item after debug.

## TODO

- ~~Support basic markdown grammar.~~
- ~~Support typora-style math object: `$..$` for inline math and `$$\n ... \n$$` for block math~~
- Support all markdown grammar
- Support all notion object like `to_do` , `toggle` , etc.
- Support update manner for exist item.
- Support auto sync between local markdown file and online notion database.

## Demo

![三连](https://raw.githubusercontent.com/veya2ztn/md2notion_api_version/main/figures/三连.png)

## Contribution

Majority of this work is accomplished by [chatGPT](https://chat.openai.com/). It seems that anyone now can debug and implement new feature now without much familiar with "string operation". You can refer my conversation as [here](https://shareg.pt/oSacXil) . For this project, `GPT4` is much much much much more powerful than `GPT3.5`. 

So far, I only pass test examples for my own notebooks consist of equation, table and content. If you find a bug, have a feature request, or just want to give feedback, please open an issue. If you would like to contribute code, you can fork the repository and make your changes on a separate branch. Once you are ready, create a pull request. We appreciate all contributions, big or small, and look forward to working with you!

## Reference

This repo cannot build without follow projects:

- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) 
- [md_img_uploader](https://github.com/nifanle7/md_img_uploader)
- [python-o365](https://github.com/O365/python-o365)
- [md2notion](https://github.com/Cobertos/md2notion)
- [Notion 导入 LaTeX 公式](https://zhuanlan.zhihu.com/p/360430369)

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
