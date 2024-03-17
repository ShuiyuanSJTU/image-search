import time
import sys
import os

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

target_url = "https://shuiyuan.sjtu.edu.cn/t/topic/229757"  # qutu 9

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}

target_dir = "images"


def process_cookies(cookies_str):
    cookies = cookies_str.strip().split(";")
    result = []
    for cookie in cookies:
        name, value = cookie.strip().split("=")
        result.append({"name": name, "value": value, "domain": ".sjtu.edu.cn"})
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Copy cookies from the browser and paste them here:")
        cookies_str = input()
        cookies = process_cookies(cookies_str)
    else:
        cookies_str = sys.argv[1]
        cookies = process_cookies(cookies_str)

    target_path = os.path.join(os.getcwd(), target_dir)
    print(f"Target directory: {target_path}")
    print("Continue? (Y/n) ", end="")
    if input().strip().lower() == "n":
        sys.exit(0)

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    driver = webdriver.Chrome()
    driver.get(target_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.refresh()
    driver.get(target_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "main")))

    print(driver.title)

    s = requests.Session()
    for cookie in driver.get_cookies():
        s.cookies.set(cookie["name"], cookie["value"])

    last = 0
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        posts = driver.find_elements(
            By.CSS_SELECTOR, ".ember-view .post-stream .topic-post"
        )
        for post in posts:
            articles = post.find_elements(By.CSS_SELECTOR, "article")
            for article in articles:
                post_id = article.get_attribute("id")
                if post_id is None or not post_id.startswith("post_"):
                    continue

                cur = int(post_id[5:])
                if cur > last:
                    last = cur
                    print(article.get_attribute("id"))
                    cooked = article.find_element(By.CSS_SELECTOR, ".cooked")
                    # print(cooked.get_attribute("outerHTML"))
                    imgs = cooked.find_elements(
                        By.XPATH,
                        ".//img[not(contains(@class, 'emoji')) and not(contains(@class, 'avatar')) and not(contains(@class, 'site-icon'))]",
                    )
                    for i, img in enumerate(imgs):
                        url = img.get_attribute("src")
                        print(i, url)
                        if url is not None:
                            response = s.get(url, headers=headers)
                            if response.status_code == 200:
                                with open(
                                    f"{target_path}/{post_id}_{i}.jpg", "wb"
                                ) as f:
                                    f.write(response.content)
                                print(f"Get {post_id}_{i}.jpg")
                            else:
                                print(f"Failed to get {post_id}_{i}.jpg")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("scrolling...")
        time.sleep(1)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

    driver.quit()
