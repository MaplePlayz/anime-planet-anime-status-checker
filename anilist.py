import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_anime_status(username):
    # URL of the user's anime list
    url = f"https://www.anime-planet.com/users/{username}/anime/wanttowatch"

    # Headers with User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }

    # Send a GET request to the URL with headers
    logger.info("Fetching data from: %s", url)
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all anime entries
        anime_list = soup.find_all('li', attrs={'data-type': 'anime'})

        # Check if the anime list is empty
        if not anime_list:
            logger.info("Anime list is empty.")
            return None
        
        # Dictionary to store anime titles and their statuses
        anime_status = {}

        for anime in anime_list:
            title = anime.find('a', class_='tooltip').text.strip()
            logger.info("Processing anime: %s", title)
            anime_link = anime.find('a', class_='tooltip')['href']
            anime_page_url = f"https://www.anime-planet.com{anime_link}"
            
            # Visit the anime page and check the number of episodes
            anime_page_response = requests.get(anime_page_url, headers=headers)
            if anime_page_response.status_code == 200:
                anime_page_soup = BeautifulSoup(anime_page_response.text, 'html.parser')
                episode_info = anime_page_soup.find('span', class_='type').text.strip()
                
                # Determine the status based on the presence of a plus sign in the episode info
                if '+' in episode_info:
                    # Extract episode number for ongoing anime
                    episode_number = episode_info.split('(')[1].split(' ')[0]
                    status = f'Ongoing (Episode {episode_number})'
                elif 'eps' in episode_info:
                    status = 'Finished'
                elif '1 ep' in episode_info:
                    status = 'Finished'
                else:
                    status = 'Not Started'
                
                anime_status[title] = status
            else:
                logger.error("Failed to retrieve data for %s. Status code: %s", title, anime_page_response.status_code)

        return anime_status
    else:
        logger.error("Failed to retrieve data. Status code: %s", response.status_code)
        return None

# Input username
username = ""
anime_status = check_anime_status(username)
if anime_status:
    print("Anime and their status:")
    for anime, status in anime_status.items():
        print(f"{anime}: {status}")
