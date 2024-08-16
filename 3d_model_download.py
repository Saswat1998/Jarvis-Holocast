import requests
from bs4 import BeautifulSoup
import os

BASE_URL = 'https://nasa3d.arc.nasa.gov'
DOWNLOAD_DIR = 'nasa_3d_models'

def fetch_models():
    url = BASE_URL + '/models'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    models = []
    for link in soup.find_all('a', href=True):
        if '/detail/' in link['href']:
            models.append(BASE_URL + link['href'])
    return models

def download_model(model_url, download_dir):
    response = requests.get(model_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    download_link = None
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.zip') or link['href'].endswith('.obj'):
            download_link = link['href']
            break
    
    if download_link:
        model_response = requests.get(download_link)
        model_response.raise_for_status()
        
        model_name = download_link.split('/')[-1]
        model_path = os.path.join(download_dir, model_name)
        with open(model_path, 'wb') as model_file:
            model_file.write(model_response.content)
        
        print(f'Downloaded {model_name} to {model_path}')
    else:
        print(f'No downloadable link found for {model_url}')

def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    
    models = fetch_models()
    for model_url in models[:5]:  # Limiting to first 5 models for this example
        download_model(model_url, DOWNLOAD_DIR)

if __name__ == '__main__':
    main()
