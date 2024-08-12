import json
import requests
from bs4 import BeautifulSoup
from io import BytesIO

def fetch_instagram_profile(username):
    url = f"https://www.instagram.com/{username}/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script', type="text/javascript")
        shared_data_script = None
        print(scripts)
        for script in scripts:
            if script.string and "window._sharedData" in script.string:
                shared_data_script = script.string
                break

        if shared_data_script:
            shared_data_script = shared_data_script.split("window._sharedData = ")[1][:-1]
            shared_data = json.loads(shared_data_script)
            user_data = shared_data['entry_data']['ProfilePage'][0]['graphql']['user']
            profile_pic_url = user_data['profile_pic_url_hd']
            follower_count = user_data['edge_followed_by']['count']
            return profile_pic_url, follower_count
    return None, None

# Example usage
profile_pic_url, follower_count = fetch_instagram_profile("_bugs_bunny_.wanders")
print(profile_pic_url, follower_count)
