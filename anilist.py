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

    anime_status = {}
    processed_anime_titles = set()  # Set to store processed anime titles

    # Variable to store current page number
    page_number = 1

    while True:
        # Construct URL for the current page
        page_url = f"{url}?sort=title&page={page_number}"

        # Send a GET request to the URL with headers
        logger.info("Fetching data from: %s", page_url)
        response = requests.get(page_url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all anime entries
            anime_list = soup.find_all('li', attrs={'data-type': 'anime'})

            # Check if the anime list is empty
            if not anime_list:
                logger.info("No more anime found on page %d.", page_number)
                break

            for anime in anime_list:
                title = anime.find('a', class_='tooltip').text.strip()
                if title in processed_anime_titles:
                    # Stop processing if the anime title is already processed
                    logger.info("Already processed anime: %s. Stopping further collection.", title)
                    return anime_status
                else:
                    processed_anime_titles.add(title)  # Add title to processed set

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

            # Move to the next page
            page_number += 1
        else:
            logger.error("Failed to retrieve data from page %d. Status code: %s", page_number, response.status_code)
            break

    return anime_status

# Input username
username = "Mapleplayz"
anime_status = check_anime_status(username)
if anime_status:
    print("Anime and their status:")
    for anime, status in anime_status.items():
        print(f"{anime}: {status}")
