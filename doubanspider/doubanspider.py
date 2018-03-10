# -*- coding: UTF-8 -*-
import sys
import time
from urllib.request import urlopen
from urllib.parse import quote
import lxml
import urllib
from urllib.request import Request
import numpy as np
from bs4 import BeautifulSoup
from imp import reload
import sqlite3


class doubanspider():
    reload(sys)
    # 构建请求头
    headers = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
        {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
        {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]
    page_num = 0
    book_list = []
    try_times = 0
    def book_spider(self,book_tag_lists):
        for book_tag in book_tag_lists:
            # url='http://www.douban.com/tag/%E5%B0%8F%E8%AF%B4/book?start=0' # For Test
            url = 'http://www.douban.com/tag/' + quote(book_tag) + '/book?start=' + str(self.page_num * 15)
            print(url)
            # 随机选择时间睡眠
            time.sleep(np.random.rand() * 5)
            try:
                req = Request(url, headers=self.headers[self.page_num % len(self.headers)])
                source_code = urlopen(req).read()
                plain_text = str(source_code,'utf-8')
            except (urllib.HTTPError, urllib.URLError) as e:
                print(e)
                continue
            soup = BeautifulSoup(plain_text, 'lxml')
            list_soup = soup.find('div', {'class': 'mod book-list'})
            self.try_times += 1;
            if list_soup == None and self.try_times < 200:
                continue
            elif list_soup == None or len(list_soup) <= 1:
                break  # 超过200次或list_soup无数据尝试跳出循环
    #获取书籍信息
    def get_book_info(self, list_soup):
        # url='http://book.douban.com/subject/6082808/?from=tag_all' # For Test
        for book_info in list_soup.findAll('dd'):
            #书名
            title = book_info.find('a', {'class': 'title'}).string.strip()
            # desc = book_info.find('div', {'class': 'desc'}).string.strip()
            # desc_list = desc.split('/')
            book_url = book_info.find('a', {'class': 'title'}).get('href')
        try:
            req = Request(book_url, headers=self.headers[np.random.randint(0, len(self.headers))])
            source_code = urlopen(req).read()
            plain_text = str(source_code, 'utf-8')
        except (urllib.HTTPError, urllib.URLError) as e:
            print(e)
        soup = BeautifulSoup(plain_text,'lxml')
        try:
            author_info = '作者： ' + soup.xpath('div',{'a':''})
            print(author_info)
        except:
            author_info = '作者： 暂无'
        #评论人数
        people_num = soup.find('div', {'class': 'rating_sum'}).findAll('span')[1].string.strip()
        return people_num

        #获取书籍内容
        def get_book(self,list_soup):
            for book_info in list_soup.findAll('dd'):
                title = book_info.find('a', {'class': 'title'}).string.strip()
                desc = book_info.find('div', {'class': 'desc'}).string.strip()
                desc_list = desc.split('/')
                # 书籍url
                book_url = book_info.find('a', {'class': 'title'}).get('href')
                print(title)
                '''需要的数据：
                书名、作者、出版社、出版年、页数、定价、ISBN、评论人数
                '''
                try:
                    author_info = '作者/译者： ' + '/'.join(desc_list[0:-3])
                    print(author_info)
                except:
                    author_info = '作者/译者： 暂无'
                try:
                    pub_info = '出版信息： ' + '/'.join(desc_list[-3:])
                    print(pub_info)
                except:
                    pub_info = '出版信息： 暂无'
                try:
                    rating = book_info.find('span', {'class': 'rating_nums'}).string.strip()
                    print(rating)
                except:
                    rating = '0.0'
                try:
                    # people_num = book_info.findAll('span')[2].string.strip()
                    people_num = get_people_num(book_url)
                    people_num = people_num.strip('人评价')
                    print(people_num)
                except:
                    people_num = '0'

                book_list.append([title, rating, people_num, author_info, pub_info])
                try_times = 0  # 将尝试次数归零
            # page_num += 1
            print('从%d页下载信息!' % page_num)
        return book_list
    #爬虫入口
    # def do_spider(self,book_tag_lists):
    #     book_lists = []
    #     for book_tag in book_tag_lists:
    #         book_list = book_spider(book_tag)
    #         book_list = sorted(book_list, key=lambda x: x[1], reverse=True)
    #         book_lists.append(book_list)
    #     return book_lists
    #将书籍信息写入数据库
    def print_book_lists_database(self):
        global title, author_info, pub_info, people_num
        con = sqlite3.connect('shuji.db')
        cursor = con.cursor()
        try:
            sql1 = 'create table  If Not Exists  book(fid INTEGER PRIMARY KEY autoincrement,title char(20),author_info char(30),pub_info char(50),people_num int)'
            sql2 = 'insert into book VALUES (\'%s\',\'%s\',\'%s\',%d)' % (title, author_info, pub_info, people_num)
            cursor.execute(sql1)
            cursor.execute(sql2)
            cursor.commit()
        finally:
            cursor.close()
    #入口
    if __name__ == '__main__':
        # book_tag_lists = ['心理','判断与决策','算法','数据结构','经济','历史']
        # book_tag_lists = ['传记','哲学','编程','创业','理财','社会学','佛教']
        # book_tag_lists = ['思想','科技','科学','web','股票','爱情','两性']
        # book_tag_lists = ['计算机','机器学习','linux','android','数据库','互联网']
        # book_tag_lists = ['数学']
        # book_tag_lists = ['摄影','设计','音乐','旅行','教育','成长','情感','育儿','健康','养生']
        # book_tag_lists = ['商业','理财','管理']
        book_tag_lists = ['名著']
        # book_tag_lists = ['科普','经典','生活','心灵','文学']
        # book_tag_lists = ['科幻','思维','金融']
        # book_tag_lists = ['个人管理', '时间管理', '投资', '文化', '宗教']
        book_lists = do_spider(book_tag_lists)
