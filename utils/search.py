import nltk
import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config
import logging
from utils.llm import get_llm_response

MAX_EFFECTIVE_URLS = 1

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

nltk.download("punkt")

DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"


def parse_article_details(url):
    try:
        user_agent = DEFAULT_USER_AGENT
        config = Config()
        config.browser_user_agent = user_agent
        article = Article(url, config=config)
        article.download()
        article.parse()
        article.nlp()
        return article.summary, article.text, article.top_image
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download article: {e}")
        return None, None, None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None, None, None


def find_urls(key_words, timeout=5):
    url = f"https://www.google.com/search?q={key_words.replace(' ', '+')}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    search_results = soup.find_all("div", class_="tF2Cxc")

    results = []
    for result in search_results:
        link = result.find("a")["href"]
        title = result.find("h3").text if result.find("h3") else "No title"
        results.append({"url": link, "title": title})

    return results


def is_coherent_content(retrieved_content: str):
    result = get_llm_response(
        f"assess if the following content is coherent scientific writing: {retrieved_content} Return yes or no",
        "",
    )
    logging.info(result)
    return "yes" in result.lower()


def retrieve_info_from_web(
    search_terms: str, max_effective_urls: int = MAX_EFFECTIVE_URLS
):
    url_dicts = find_urls(search_terms)
    retrieval_content = []
    effective_url_count = 0

    logging.info(f"Found {len(url_dicts)} URLs for search terms: {search_terms}")

    for url_dict in url_dicts:
        _, result, _ = parse_article_details(url_dict["url"])
        if not result:
            continue
        effective_url_count += 1
        logging.info(f"Retrieved content from {url_dict['url']}")
        retrieval_content.append(
            {"url": url_dict["url"],
             "title": url_dict["title"],
             "content": result.replace("/n", "")
             }
        )

        if effective_url_count >= max_effective_urls:
            logging.info("Maximum effective URLs reached")
            return retrieval_content
    if retrieval_content:
        return retrieval_content
    logging.warning(f"Failed to retrieve content for search terms: {search_terms}")
    return None