import requests
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

RAPIDAPI_KEY = "Your RAPIDAPI_KEY"

def scrape_and_analyze_articles(driver):
    """Entry point for BrowserStack execution - scrapes El País articles and analyzes them"""
    try:
        articles = get_opinion_articles(driver)
        
        if not articles:
            print(f"No articles found | Browser: {driver.capabilities.get('browserName', 'Unknown')}")
            return {"status": "failed", "reason": "No articles found"}
        
        titles = [art["title"] for art in articles]
        translated = translate_headers(titles)
        
        repeated = count_repeated_words(translated)
        
        # Print minimal results
        print(f"Articles found: {len(articles)} | Browser: {driver.capabilities.get('browserName', 'Unknown')}")
        print(f"Translated titles: {', '.join(translated)}")
        if repeated:
            print(f"Repeated words: {', '.join([f'{word}({count})' for word, count in repeated.items()])}")
        else:
            print("No words repeated more than twice")
        
        return {
            "status": "success", 
            "articles_count": len(articles),
            "titles": titles,
            "translated": translated,
            "repeated_words": repeated
        }
        
    except Exception as e:
        print(f"Error in {driver.capabilities.get('browserName', 'Unknown')}: {str(e)[:50]}")
        return {"status": "failed", "reason": str(e)}

def get_opinion_articles(driver, max_articles=5):
    driver.get("https://elpais.com/")

    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button//span[contains(text(), 'Accept') or contains(text(), 'Aceptar')]"))
        )
        cookie_button.click()
    except Exception:
        pass  # Continue without cookie acceptance

    try:
        opinion_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/opinion/') and contains(text(), 'Opinión')]"))
        )
        opinion_link.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/opinion"))
    except Exception:
        return []
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "main-content"))
    )
    
    articles = driver.find_elements(By.XPATH, "//main[@id='main-content']//section//article")[:max_articles]
    
    if not articles:
        return []
    
    result = []
    for i, article in enumerate(articles, 1):
        try:
            title_element = article.find_element(By.XPATH, ".//h1 | .//h2 | .//h3")
            title = title_element.text
            
            link_element = article.find_element(By.XPATH, ".//a[@href]")
            link = link_element.get_attribute('href')
            
            content_elements = article.find_elements(By.XPATH, ".//p")
            content = " ".join([p.text for p in content_elements if p.text.strip()]) or article.text
            
            img_name = None
            try:
                img_element = article.find_element(By.XPATH, ".//img")
                img_url = img_element.get_attribute("src")
                if img_url:
                    img_data = requests.get(img_url).content
                    safe_title = title[:10].replace(' ', '_').replace('/', '')
                    img_name = f"cover_{safe_title}.jpg"
                    with open(img_name, 'wb') as handler:
                        handler.write(img_data)
            except Exception:
                pass
            
            result.append({
                "title": title,
                "content": content,
                "image": img_name,
                "link": link
            })
            
        except Exception:
            continue
    return result

def translate_headers(headers):
    if not headers:
        return []
    
    try:
        url = "https://google-translate113.p.rapidapi.com/api/v1/translator/json"
        
        json_data = {f"title_{i}": header for i, header in enumerate(headers)}
        
        payload = {
            "from": "es",
            "to": "en",
            "json": json_data
        }
        
        headers_api = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "google-translate113.p.rapidapi.com",
            'Content-Type': "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers_api)
        
        if response.status_code == 200:
            response_data = response.json()
            return [response_data.get("trans", {}).get(f"title_{i}", headers[i]) 
                   for i in range(len(headers))]
        else:
            return headers
            
    except Exception:
        return headers


def count_repeated_words(headers):
    words = re.findall(r'\w+', ' '.join(headers).lower())
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return {word: count for word, count in freq.items() if count > 2}
