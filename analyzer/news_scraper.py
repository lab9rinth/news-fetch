import requests
from bs4 import BeautifulSoup
import traceback
import logging
import re
from datetime import datetime
import json

# Set up logging
logger = logging.getLogger(__name__)

def clean_text(text):
    if not text:
        return ""
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove any special characters that might appear
    text = re.sub(r'[\xa0\u200b]', ' ', text)
    return text

def extract_json_ld(soup):
    """Extract article data from JSON-LD script tags"""
    try:
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                if data.get('@type') in ['NewsArticle', 'Article']:
                    return data
            except:
                continue
        return None
    except Exception as e:
        logger.error(f"Error extracting JSON-LD: {str(e)}")
        return None

def get_bbc_article(soup, url):
    """Extract content from BBC articles"""
    try:
        title = None
        content = []
        author = 'BBC News'
        pub_date = None
        category = 'News'

        # Get title
        title_elem = soup.select_one('h1[id="main-heading"]')
        if title_elem:
            title = clean_text(title_elem.text)

        # Get content
        article_body = soup.select_one('article')
        if article_body:
            # Get all paragraphs from the article
            paragraphs = article_body.select('div[data-component="text-block"] p')
            for p in paragraphs:
                text = clean_text(p.text)
                if text and len(text) > 20:
                    content.append(text)

        # Get date
        time_elem = soup.select_one('time')
        if time_elem:
            pub_date = time_elem.get('datetime', 'Date not found')

        # Get category from URL
        if '/news/' in url:
            category_match = re.search(r'/news/([^/]+)', url)
            if category_match:
                category = category_match.group(1).replace('-', ' ').title()

        return {
            'title': title or 'Title not found',
            'content': '\n\n'.join(content) if content else 'Content not found',
            'date': pub_date or 'Date not found',
            'author': author,
            'category': category,
            'word_count': sum(len(p.split()) for p in content),
            'paragraph_count': len(content)
        }
    except Exception as e:
        logger.error(f"Error extracting BBC article: {str(e)}")
        return None

def get_dd_news_article(soup, url):
    """Extract content from DD News articles"""
    try:
        title = None
        content = []
        author = 'DD News'
        pub_date = None
        category = 'News'

        # Get title
        title_elem = soup.select_one('h1.title')
        if title_elem:
            title = clean_text(title_elem.text)

        # Get content
        article_body = soup.select_one('div.field-name-body')
        if article_body:
            # Get all paragraphs from the article
            paragraphs = article_body.select('p')
            for p in paragraphs:
                text = clean_text(p.text)
                if text and len(text) > 20:
                    content.append(text)

        # Get date
        date_elem = soup.select_one('span.date-display-single')
        if date_elem:
            pub_date = date_elem.get('content') or clean_text(date_elem.text)

        # Get category from breadcrumb
        category_elem = soup.select_one('div.breadcrumb a:last-child')
        if category_elem:
            category = clean_text(category_elem.text)

        return {
            'title': title or 'Title not found',
            'content': '\n\n'.join(content) if content else 'Content not found',
            'date': pub_date or 'Date not found',
            'author': author,
            'category': category,
            'word_count': sum(len(p.split()) for p in content),
            'paragraph_count': len(content)
        }
    except Exception as e:
        logger.error(f"Error extracting DD News article: {str(e)}")
        return None

def get_article_content(url):
    try:
        logger.info(f"Starting to scrape URL: {url}")
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Get the page content
        logger.info("Making HTTP request...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Determine the source and extract accordingly
        if 'bbc.com' in url or 'bbc.co.uk' in url:
            article_data = get_bbc_article(soup, url)
        elif 'ddnews.gov.in' in url:
            article_data = get_dd_news_article(soup, url)
        else:
            raise ValueError("Unsupported news source. Currently supporting BBC News and DD News only.")
        
        if not article_data:
            raise Exception("Failed to extract article data")
        
        article_data['url'] = url
        
        # Validate result
        if article_data['title'] == 'Title not found' and article_data['content'] == 'Content not found':
            logger.error("Failed to extract both title and content")
            return None
        
        logger.info("Successfully extracted article data")
        return article_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error extracting article content: {str(e)}")
        logger.error(traceback.format_exc())
        return None 