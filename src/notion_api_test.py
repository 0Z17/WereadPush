from notion_client import Client
import logging
import random
from datetime import datetime

class BookMarkExtractor:
    def __init__(self, token):
        self.notion = Client(auth=token, log_level=logging.ERROR)

        # get the database id
        self.book_database_id = self.notion.search(query="书架").get("results")[0]["id"]
        self.bookmark_database_id = self.notion.search(query="划线").get("results")[0]["id"]
        self.note_database_id = self.notion.search(query="笔记").get("results")[0]["id"]

    def get_bookmark_info(self, page_id):
        """
        Get the bookmark info of a page.\n
        params:
            page_id: the id of the page
        return:
            a dictionary containing the bookmark info {bookmark, book, date}
        """

        bookmark_page = self.notion.pages.retrieve(page_id=page_id)
        bookmark_text = bookmark_page.get("properties").get("Name").get("title")[0].get("plain_text")
        
        book_id = bookmark_page.get("properties").get("书籍").get("relation")[0].get("id")
        book_name = self.get_bookname(book_id)

        date = bookmark_page.get("properties").get("Date").get("date").get("start")

        return {"bookmark": bookmark_text, "book": book_name, "date": self.transfer_date(date)}

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
    
    def get_number_of_bookmarks(self):
        """
        Get the total number of bookmarks.\n
        return:
            the total number of bookmarks
        """
        return 100

    def get_bookmark_id(self,idx):
        """
        Get the id of the idx-th bookmark.\n
        params:
            idx: the index of the bookmark
        return:
            the id of the idx-th bookmark
        """
        bookmarks = self.notion.databases.query(database_id=self.bookmark_database_id).get("results")
        return bookmarks[idx-1].get("id")

    def get_random_bookmark(self,n):
        """
        Get n random bookmarks.\n
        params:
            n: the number of bookmarks to be returned
        return:
            a list of dictionaries containing the bookmark info {bookmark, book, date}
        """ 
        random_idx = random.sample(range(self.get_number_of_bookmarks()-1),n)
        bookmark_ls = []
        for idx in random_idx:
            bookmark_ls.append(self.get_bookmark_info(self.get_bookmark_id(idx)))
        return bookmark_ls

if __name__ == '__main__':

    token = "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"
    bm_extractor = BookMarkExtractor(token)
    bookmarks = bm_extractor.notion.databases.query(database_id=bm_extractor.note_database_id).get("results")

    print(bm_extractor.get_random_bookmark(5))