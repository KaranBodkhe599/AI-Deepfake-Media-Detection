from newspaper import Article

def scrape_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()

        return {
            "title": article.title or "No Title",
            "text": article.text[:1500] or "No Text",
            "image": article.top_image or ""
        }

    except Exception as e:
        print("Scraper Error:", str(e))

        return {
            "title": "Scraping Failed",
            "text": "Content not available",
            "image": ""
        }