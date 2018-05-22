import pprint
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import os

class News:
    def __init__(self, title, url, category, category_url, post_date, source, editor, content):
        self.title = title
        self.url = url
        self.category = category
        self.category_url = category_url
        self.post_date = post_date
        self.source = source
        self.editor = editor
        self.content = content

    def __str__(self):
        desc_str = "%s [%s] posted on %s from %s" % (self.title, self.url, self.post_date, self.source)
        return desc_str
    
    def setEditor(self, editor):
        self.editor = editor
    
    def setContent(self, content):
        self.content = content
    
    def setPostDate(self, post_date):
        self.post_date = post_date

    def to_csv(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s" % (self.title, self.url, self.category, self.category_url, self.post_date, self.source, self.editor, self.content)
    def to_tsv(self):
        return "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.title, self.url, self.category, self.category_url, self.post_date, self.source, self.editor, self.content)

def wait_for_xpath_to_be_available(browser, xpath, total_wait=30):
    try:
        # Give only one class name, if you want to check multiple classes then 'and' will be use in XPATH
        # e.g //*[contains(@class, "class_name") and contains(@class, "second_class_name")]
        elem = browser.find_element_by_xpath(xpath)
        print("Yeah! found", xpath, total_wait)
    except:
        print("not found", xpath, total_wait)
        total_wait -= 1
        time.sleep(1)
        if total_wait > 1: wait_for_xpath_to_be_available(browser, xpath, total_wait)

if __name__ == "__main__":
    # path to selenium server standalone jar, downloaded here:
    # http://docs.seleniumhq.org/download/
    # or a direct url:
    # http://selenium-release.storage.googleapis.com/2.41/selenium-server-standalone-2.41.0.jar
    os.environ["SELENIUM_SERVER_JAR"] = "selenium-server-standalone-2.41.0.jar"
    # note: I've put this jar file in the same folder as this python file

    browser = webdriver.Safari()

    # makes the browser wait if it can't find an element
    browser.implicitly_wait(10)

    browser.get("https://www.joc.com/user/login")

    search_input = browser.find_element_by_id("edit-name")
    search_input.send_keys("*******")
    search_input = browser.find_element_by_id("edit-pass")
    search_input.send_keys("******")
    search_input.send_keys(Keys.RETURN)

    wait_for_xpath_to_be_available(browser, '//span[@class="header-welcome-user"]')

    browser.get("https://www.joc.com/news")

    wait_for_xpath_to_be_available(browser, '//*[@id="panel-pane"]/div/div/div[2]/table/tbody')


    table = browser.find_element_by_xpath('//*[@id="panel-pane"]/div/div/div[2]/table/tbody')
    rows = table.find_elements_by_tag_name('tr')

    news_list = []
    for r in rows:
        title = r.find_element_by_xpath('./td[1]/a').text
        url = r.find_element_by_xpath('./td[1]/a').get_attribute('href')
        category = r.find_element_by_xpath('./td[1]/div[@class="category"]/a').text
        category_url = r.find_element_by_xpath('./td[1]/div[@class="category"]/a').get_attribute('href')
        post_date = r.find_element_by_xpath('./td[2]').text
        
        news = News(title, url, category, category_url, post_date, 'JOC.com', '', '')

        news_list.append(news)
        #break

    for i, n in enumerate(news_list):
        url = n.url
        print(url)
        # # load news url
        browser.get(url)
        wait_for_xpath_to_be_available(browser, '//*[@id="panel-pane--2"]/div/article')
        
        article = browser.find_element_by_xpath('//*[@id="panel-pane--2"]/div/article')

        header = article.find_element_by_xpath('./header/p[@class="submitted"]').text
        # print(header)
        editor, post_date = header.split('|')
        # print(editor, post_date)

        content = article.find_element_by_css_selector('div.field-name-body > div > div').get_attribute('innerHTML')

        n.setEditor(editor)
        n.setPostDate(post_date)
        n.setContent(content)

    with open("test.tsv", "a") as myfile:
        
        for i, n in enumerate(news_list):
            s = "%s\t%s\n" % (i, n.to_tsv())
            myfile.write(s)
    input("Press Enter to close...")

    browser.quit()
