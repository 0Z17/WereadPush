from notion_client import Client
import logging
import random
from datetime import datetime

class BookMarkExtractor:
    def __init__(self, token):
        self.notion = Client(auth=token, log_level=logging.ERROR)

        # get the database id
        self.book_database_id = self.get_database_id(self.notion.search(query="书架").get("results"))
        self.bookmark_database_id = self.get_database_id(self.notion.search(query="划线").get("results"))
        self.note_database_id = self.get_database_id(self.notion.search(query="笔记").get("results"))

        self.bookmark_cursors = list()
        self.note_cursors = list()

        self.BOOKMARK = 0
        self.NOTE = 1

    def get_database_id(self,database_ret):
        """
        Check if the database id is valid.\n
        params:
            database_ret: the return value of notion.search()
        return:
            the database id
        """
        if len (database_ret) == 0:
            print("Database not found.")
            raise Exception("Database not found.")
        
        if len (database_ret) == 1:
            return database_ret[0]["id"]
        
        for i in range(len(database_ret)):
            if database_ret[i]["object"] == "database":
                return database_ret[i]["id"]
        
        print("Database not found.")
        raise Exception("Database not found.")


    def get_bookmark_info(self, page_id):
        """
        Get the bookmark info of a page.\n
        params:
            page_id: the id of the page
        return:
            a dictionary containing the bookmark info {bookmark_text, book_name, date}
        """

        bookmark_page = self.notion.pages.retrieve(page_id=page_id)
        bookmark_text = bookmark_page.get("properties").get("Name").get("title")[0].get("plain_text")
        
        book_id = bookmark_page.get("properties").get("书籍").get("relation")[0].get("id")
        book_name = self.get_bookname(book_id)

        date = self.transfer_date(bookmark_page.get("properties").get("Date").get("date").get("start"))

        return {"bookmark_text": bookmark_text, "book_name": book_name, "date": date}
    
    def get_note_info(self, page_id):
        """
        Get the note info of a page.\n
        params:
            page_id: the id of the page
        return:
            a dictionary containing the note info {note_text, content_text, book_name, date}
        """

        note_page = self.notion.pages.retrieve(page_id=page_id)
        note_text = note_page.get("properties").get("Name").get("title")[0].get("plain_text")
        content = note_page.get("properties").get("abstract").get("rich_text")[0].get("plain_text")

        book_id = note_page.get("properties").get("书籍").get("relation")[0].get("id")
        book_name = self.get_bookname(book_id)

        date = self.transfer_date(note_page.get("properties").get("Date").get("date").get("start"))

        return {"note_text": note_text, "content_text": content, "book_name": book_name, "date": date}


    def get_bookname(self, book_id):
        """
        Get the book name of a book.\n
        params:
            book_id: the id of the book
        return:
            the book name
        """
        return self.notion.pages.retrieve(page_id=book_id).get("properties").get("书名").get("title")[0].get("plain_text")

    def transfer_date(self, date):
        """
        Transfer the date format from notion to standard format.\n
        params:
            date: the date in notion format
        return:
            the date in standard format
        """
        dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z')
        return dt.strftime('%Y-%m-%d')
    
    def get_number_of_items(self, item_type):
        """
        Get the total number of bookmarks.\n
        return:
            the total number of bookmarks
        """
        if item_type == self.BOOKMARK:
            cursor_ls = self.bookmark_cursors
            database_id = self.bookmark_database_id
        elif item_type == self.NOTE:
            cursor_ls = self.note_cursors
            database_id = self.note_database_id

        ret = self.notion.databases.query(database_id=database_id)
        has_more = ret.get("has_more")

        number_of_items = len(ret.get("results"))

        while has_more:
            cursor = ret.get("next_cursor")
            cursor_ls.append(cursor)
            ret = self.notion.databases.query(database_id=database_id, start_cursor=ret.get("next_cursor"))
            has_more = ret.get("has_more")
            number_of_items += len(ret.get("results"))

        if item_type == self.BOOKMARK:
            print("Total number of bookmarks:", number_of_items)
        elif item_type == self.NOTE:
            print("Total number of notes:", number_of_items)

        return number_of_items


    def get_item_id(self,item_type,idx):
        """
        Get the id of the idx-th item of the specified type.\n
        params:
            item_type: the type of the item (BOOKMARK or NOTE)
            idx: the index of the item
        return:
            the id of the idx-th item
        """
        if item_type == self.BOOKMARK:
            cursor_ls = self.bookmark_cursors
            database_id = self.bookmark_database_id
        elif item_type == self.NOTE:
            cursor_ls = self.note_cursors
            database_id = self.note_database_id

        items = self.notion.databases.query(database_id=database_id).get("results")
        return items[idx-1].get("id")
    
    def convert_idx(self,item_type,idx):
        pass

    def get_random_item(self,item_type,n):
        """
        Get n random items of the specified type.\n
        params:
            item_type: the type of the item (BOOKMARK or NOTE)
            n: the number of items to be returned
        return:
            a list of dictionaries containing the info of the random items
        """
        random_idx = random.sample(range(self.get_number_of_items(item_type)-1),n)
        item_ls = list()
        for idx in random_idx:
            if item_type == self.BOOKMARK:
                item_ls.append(self.get_bookmark_info(self.get_item_id(item_type,idx)))
            elif item_type == self.NOTE:
                item_ls.append(self.get_note_info(self.get_item_id(item_type,idx)))
        return item_ls

if __name__ == '__main__':

    token = "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"
    bm_extractor = BookMarkExtractor(token)
    print(bm_extractor.get_random_item(bm_extractor.BOOKMARK,5))