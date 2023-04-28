from notion_client import Client
from notion_client.helpers import is_full_page

class NotionSyncDatabase:
    def __init__(self, connection_key, database_id ):
        self.notion       = Client(auth=connection_key)
        self.database_id  = database_id
        full_or_partial_pages = self.notion.databases.query(database_id=self.database_id)
        self.file_names   = {}
        for page in full_or_partial_pages["results"]:
            if not is_full_page(page):continue
            if len(page['properties']['Name']['title'])==0:continue
            page_title = page['properties']['Name']['title'][0]['plain_text']
            if  page_title not in self.file_names:
                self.file_names[page_title] = 1
            else:
                print(f"WARNING: detect repeat file names:{page_title}")
        self.file_names = list(self.file_names.keys())
        print(f"this database has totally {len(self.file_names)} unique items")
    def show_items(self):
        full_or_partial_pages = self.notion.databases.query(database_id=self.database_id)                
        for page in full_or_partial_pages["results"]:
            if not is_full_page(page):continue
            name_list = page['properties']['Name']['title']
            if len(name_list) == 0:continue
            page_title = name_list[0]['plain_text']
            print(f"Name:{page_title} Created at: {page['created_time']} _id:{page['id']}")
    def create_new_page(self, page_name, tags=[{"name": "general"}],**kargs):
        new_page = {
            "Name": {"title": [{"text": {"content": page_name}}]},
            "Tags": {"type": "multi_select", "multi_select":tags},
        }
        if page_name not in self.file_names:
            self.notion.pages.create(parent={"database_id": self.database_id}, properties=new_page)
            print(f"You add {page_name} page into database!")
        else:
            print(f"Use existed {page_name} page in database!")
    def get_page_id_via_name(self, page_name):
        query_string = {
                "database_id": self.database_id,
                "filter": {"property": "Name", "rich_text": {"contains": page_name}},
            }
        results = self.notion.databases.query(**query_string).get("results")
        no_of_results = len(results)
        if no_of_results == 0:
            print("No results found.")
            return 

        print(f"No.of results found: {len(results)}, choose the first one")
        result = results[0]
        print(f"The first result is a {result['object']} with id {result['id']}.")
        return result['id']   
    
if __name__ == '__main__':
    # get your token from https://www.notion.so/my-integrations
    connection_key = "secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    # get your database id from url https://www.notion.so/xxxxxxx, add '-' manually.
    database_id    = "88c52f93-7663-497d-93b2-45934c741f39" #<---for example
    client         = NotionSyncDatabase(connection_key, database_id)