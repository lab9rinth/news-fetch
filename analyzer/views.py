from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .news_scraper import get_article_content
import json
import logging
import traceback
import re

# Set up logging
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'analyzer/index.html')

def is_valid_news_url(url):
    """Check if the URL is from a supported news source"""
    valid_domains = [
        'bbc.com',
        'bbc.co.uk',
        'ddnews.gov.in'
    ]
    return any(domain in url.lower() for domain in valid_domains)

@csrf_exempt
def analyze_news(request):
    if request.method == 'POST':
        try:
            # Log the raw request body
            logger.info(f"Received request body: {request.body}")
            
            data = json.loads(request.body)
            url = data.get('url', '').strip()
            
            if not url:
                logger.error("No URL provided in request")
                return JsonResponse({
                    'error': 'URL is required',
                    'details': 'Please provide a valid news article URL'
                }, status=400)
            
            # Validate URL
            if not is_valid_news_url(url):
                logger.error("Invalid URL domain")
                return JsonResponse({
                    'error': 'Invalid URL',
                    'details': 'Please provide a valid URL from BBC News or DD News'
                }, status=400)
            
            logger.info(f"Processing URL: {url}")
            
            # Get article content using our scraper
            article_data = get_article_content(url)
            
            if article_data:
                logger.info("Successfully extracted article data")
                return JsonResponse(article_data)
            else:
                logger.error("Failed to extract article data")
                return JsonResponse({
                    'error': 'Failed to analyze the article',
                    'details': 'Could not extract content from the provided URL. Please make sure it is a valid article page.'
                }, status=400)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({
                'error': 'Invalid JSON data',
                'details': str(e)
            }, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=500)
    
    return JsonResponse({
        'error': 'Invalid request method',
        'details': 'Only POST requests are allowed'
    }, status=405)
