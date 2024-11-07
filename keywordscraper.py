import json
import sys
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urlunparse
import re
# import nltk
# from nltk.corpus import words

if len(sys.argv) < 3:
    print("Usage: python keywordscraper.py <Instance> <Count_Per_Instance>")
    sys.exit(1)

Instance = sys.argv[1]
Count_Per_Instance = sys.argv[2]
# print(Instance,Count_Per_Instance)

Result_Filename = 'seo_results_'+str(Instance)+'.txt'
Result_Filename_Error = 'seo_error_results_'+str(Instance)+'.txt'

f = open(Result_Filename, "w")
f = open(Result_Filename_Error, "w")

# english_words = set(words.words())

# def remove_non_english_words(text):
    # words_list = nltk.word_tokenize(text)
    # english_only_words = [word for word in words_list if word.lower() in english_words]
    # return ' '.join(english_only_words)

def remove_html_tags_and_urls(text):
    try:
        clean_text = re.sub(r'<[^>]*>', ' ', text)
        clean_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', clean_text)
        clean_text = re.sub(r'[^a-zA-Z0-9\s,.]', ' ', clean_text)
        clean_text = re.sub(r'\,\s+', ',', clean_text)
        clean_text = re.sub(r',{2,}', ',', clean_text)
        # clean_text = re.sub(r'[^\w\s,.]', ' ', clean_text)
        # clean_text = remove_non_english_words(clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()
    except:
        return text
        
def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        # Read and return a list of URLs, removing leading and trailing whitespaces
        url_list = list([line.strip() for line in file.readlines()])
        # print(url_list)
        Start_index = int(Instance)*int(Count_Per_Instance)
        End_index = Start_index+int(Count_Per_Instance)
        # print("Checki")
        print(Start_index,End_index)
        url_list = url_list[Start_index:End_index]
        # print(url_list)
        return url_list

def add_https_if_missing(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        # If no scheme is provided, add https:// and correct double slashes
        return urlunparse(('https',) + parsed_url[1:])
    else:
        return url

def extract_seo_data(url):
    try:
        print("url:::", url)
        response = requests.get(url, timeout=3)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract SEO data with error handling
        title_tag = soup.find('title')
        title = remove_html_tags_and_urls(title_tag.text) if title_tag else None

        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag.get('content') if description_tag else None

        # keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        # keywords = keywords_tag['content'] if keywords_tag else None
        
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        keywords = remove_html_tags_and_urls(keywords_tag.get('content')) if keywords_tag else None

        og_tags_list = soup.find_all('meta', property=True)
        # og_tags = {tag['property']: tag['content'] for tag in og_tags_list} if og_tags_list else None
        
        og_tags = {}
        for tag in og_tags_list:
            
            if 'property' in tag and 'content' in tag:
                tag = remove_html_tags_and_urls(tag)
                og_tags[tag['property']] = tag['content']

        #seo_data['og_tags'] = og_tags if og_tags else None

        headings_list = soup.find_all(('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'body'))
        headings = [remove_html_tags_and_urls(h.text) for h in headings_list] if headings_list else None
        
        if description!= None:
            description = remove_html_tags_and_urls(description)
        if title!= None:
            title = remove_html_tags_and_urls(title)
        # og_tags = og_tags.strip()
        # headings = headings.strip()


        # Create a dictionary with SEO data
        seo_data = {
            'url': url,
            'title': title,
            'description': description,
            'keywords': keywords,
            'og_tags': og_tags,
            'headings': headings
        }

        return seo_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching url '{url}': {e}")
        with open(Result_Filename_Error, 'a', encoding='utf-8') as file:
            file.write(f"{url}\n")
            # json_string = json.dumps(seo_data, ensure_ascii=False)
            # cleaned_string = json_string.replace('\n', '')
            # file.write(cleaned_string + '\n')
        return None

def save_to_file(url, seo_data):
    with open(Result_Filename, 'a', encoding='utf-8') as file:
        file.write(f"{url}\t")
        json_string = json.dumps(seo_data, ensure_ascii=False)
        cleaned_string = json_string.replace('\n', '')
        file.write(cleaned_string + '\n')

# Example usage
file_path = 'input_seo_url.txt'
urls = read_urls_from_file(file_path)
# print(urls)
for url in urls:
    url_with_https = add_https_if_missing(url)
    seo_data = extract_seo_data(url_with_https)

    if seo_data:
        print(f"\nSEO Data for {url_with_https}:")
        # for key, value in seo_data.items():
            # if key != 'url' and value is not None:
               # print(f"{key}: {value}")

        save_to_file(url_with_https, seo_data)
