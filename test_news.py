import requests
from bs4 import BeautifulSoup
import traceback
from datetime import datetime


def get_article_content(url):
    try:
        print(f"Accessing URL: {url}")

        # Set headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

        # Get the page content
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title_elem = None
        for title_class in ["hdg1", "article-title"]:
            title_elem = soup.find("h1", class_=title_class)
            if title_elem:
                break
        if not title_elem:
            title_elem = soup.find("h1")

        title = title_elem.text.strip() if title_elem else "Title not found"

        # Extract content
        content = ""
        content_div = None
        for content_class in ["storyDetails", "detail", "article-body"]:
            content_div = soup.find(["div", "article"], class_=content_class)
            if content_div:
                break

        if content_div:
            # Remove unwanted elements
            for unwanted in content_div.find_all(
                ["script", "style", "nav", "header", "footer"]
            ):
                unwanted.decompose()

            paragraphs = content_div.find_all("p")
            content = " ".join(p.text.strip() for p in paragraphs if p.text.strip())

        # Extract date
        date_elem = None
        for date_class in ["dateTime", "article-date"]:
            date_elem = soup.find(["span", "time"], class_=date_class)
            if date_elem:
                break

        if not date_elem:
            date_elem = soup.find("meta", {"property": "article:published_time"})

        pub_date = (
            date_elem.get("datetime")
            or date_elem.get("content")
            or date_elem.text.strip()
            if date_elem
            else "Date not found"
        )

        return {"title": title, "content": content, "date": pub_date, "url": url}
    except Exception as e:
        print(f"Error extracting article content: {str(e)}")
        traceback.print_exc()
        return None


def get_latest_articles():
    try:
        # Main news page URL
        main_url = "https://www.hindustantimes.com/india-news"
        print(f"Accessing main page: {main_url}")

        # Set headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

        # Get the main page content
        response = requests.get(main_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all article links
        articles = []
        for article in soup.find_all("h3", class_="hdg3"):
            link = article.find("a")
            if link and link.get("href"):
                url = link["href"]
                if not url.startswith("http"):
                    url = "https://www.hindustantimes.com" + url
                articles.append(url)

        return articles
    except Exception as e:
        print(f"Error getting latest articles: {str(e)}")
        traceback.print_exc()
        return []


def main():
    print("Extracting news from Hindustan Times...")

    try:
        # Get latest articles
        articles = get_latest_articles()

        if articles:
            # Get the first article's content
            article_url = articles[0]
            print(f"Found article: {article_url}")

            # Get article content
            article_data = get_article_content(article_url)

            if article_data:
                print("\nExtracted Article Information:")
                print(f"URL: {article_data['url']}")
                print(f"Headline: {article_data['title']}")
                print(f"Publication Date: {article_data['date']}")
                print(f"\nArticle Content Preview: {article_data['content'][:500]}...")
            else:
                print("Failed to extract article content.")
        else:
            print("No articles found on the main page.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
