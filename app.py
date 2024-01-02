from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

app = Flask(__name__)


# Function to scrape video information from a URL using Selenium and BeautifulSoup
def scrape_video_info_with_selenium(url, max_items=10):
    videos = []
    try:
        driver = webdriver.Chrome()
        driver.get(url)

        # Increase the implicit wait time to ensure the page fully loads
        driver.implicitly_wait(50)

        # Scroll down to load more content
        scroll_pause_time = 2
        num_scrolls = 5  # You can adjust the number of scrolls as needed

        for _ in range(num_scrolls):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        title_data = soup.find_all("yt-formatted-string",
                                   {"class": "style-scope ytd-rich-grid-media", "id": "video-title"})
        thumbnail_data = soup.find_all("img", {
            "class": "yt-core-image--fill-parent-height yt-core-image--fill-parent-width yt-core-image yt-core-image--content-mode-scale-aspect-fill yt-core-image--loaded"})
        video_views_time_data = soup.find_all("span",
                                              {"class": "inline-metadata-item style-scope ytd-video-meta-block"})

        for i in range(min(max_items, len(title_data))):
            title = title_data[i].text if i < len(title_data) else "Title Not Found"
            thumbnail = thumbnail_data[i].get("src") if i < len(thumbnail_data) else ""
            views_time = video_views_time_data[i].text if i < len(video_views_time_data) else "Views and Time Not Found"

            videos.append((thumbnail, title, views_time))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    return videos


# Define the route to display the form
@app.route('/')
def display_form():
    return render_template('index.html', videos=[])


# Define a new route to handle form submission
@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['channel_url']
    videos = scrape_video_info_with_selenium(url)
    return render_template('index.html', videos=videos)


if __name__ == '__main__':
    app.run(debug=True)
