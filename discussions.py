import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

options = Options()
#options.headless = True

driver = webdriver.Firefox(options=options)

# Navigate to the desired page
url = "https://github.com/filecoin-project/FIPs/discussions?page="
driver.get(url)


with open('discussion_links.json', 'r') as outfile:
    discussion_links = json.load(outfile)

with open('discussions.json', 'r') as json_file:
    data = json.load(json_file)

i = 0
discussions = []
for discussion in discussion_links:

    driver.get(discussion)
    discussion = {}

    title = driver.find_element("css selector", "span.js-issue-title")
    print(title.text)

    for discussion in data:
        if discussion["title"] == title.text:
            break

    # Get the first comment
    # #discussion-5531329 > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)
    # #discussion-5556999 > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)
    #/html/body/div[1]/div[6]/div/main/turbo-frame/div/div/div[2]/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/task-lists/table/tbody/tr/td
    # 
    first_comment_author = driver.find_element("css selector", "h2.timeline-comment-header-text > div:nth-child(1) > a:nth-child(1) > div:nth-child(2) > span:nth-child(1)")
    num_comments = driver.find_element("css selector", "#discussion-comment-count > span:nth-child(2)")
    parsed = BeautifulSoup(driver.page_source, 'html.parser')

    #print(discussion_starter.text)
    # #discussioncomment-6822488 > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > h3:nth-child(3) > div:nth-child(1) > a:nth-child(1) > div:nth-child(2) > span:nth-child(1)
    #print(driver.page_source)

    discussion["title"] = title.text
    discussion["comments"] = []

    post = parsed.find("div", class_="TimelineItem pt-0 js-comment-container discussion-timeline-item ml-0")
    comments_section = parsed.find("div", class_="")
    
    comment_divs = parsed.find_all("div", class_="js-timeline-item js-timeline-progressive-focus-container")
    for i, div in enumerate(comment_divs):
        comment = {}
        comment_author = div.find("span", class_="Truncate-text text-bold")
        comments = div.find_all("td", class_="d-block color-fg-default comment-body markdown-body js-comment-body")
        replies = div.find_all("td", class_="d-block color-fg-default comment-body markdown-body js-comment-body px-3 pt-0 pb-2")
        reply_authors = div.find_all("a", class_="author css-truncate css-truncate-target lh-condensed Link--primary Link text-bold")
        comment["author"] = comment_author.text if comment_author else "error"
        comment["comment"] = comments[0].text if comments else "error"
        comment["replies"] = []
        for j, reply in enumerate(replies):
            reply_ = {}
            reply_["author"] = reply_authors[j].text
            reply_["comment"] = reply.text
            comment["replies"].append(reply_)
        discussion["comments"].append(comment)

    # open the discussion.json file and append the discussion
    with open('discussions.json', 'r') as json_file:
        data = json.load(json_file)
        data.append(discussion)
    # write the new discussion to the file
    with open('discussions.json', 'w') as outfile:
        json.dump(data, outfile)

    with open('discussion_links.json', 'r') as outfile:
        discussion_links = json.load(outfile)
    discussion_links.pop(0)
    with open('discussion_links.json', 'w') as outfile:
        json.dump(discussion_links, outfile)

driver.quit()
