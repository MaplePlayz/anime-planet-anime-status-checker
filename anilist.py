import requests
from bs4 import BeautifulSoup

def check_anime_status(username):
    # URL of the user's anime list
    url = f"https://www.anime-planet.com/users/{username}/anime/wanttowatch"

    # Headers with User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }

    # Send a GET request to the URL with headers
    print("Fetching data from:", url)  # Add this line for debugging
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the anime titles and their statuses
        anime_list = soup.find_all('li', attrs={'data-type': 'anime'})

        # Check if the anime list is empty
        if not anime_list:
            print("Anime list is empty.")
            return None
        
        # Dictionary to store anime titles and their statuses
        anime_status = {}

        for anime in anime_list:
            title = anime.find('a', class_='tooltip').text.strip()
            anime_link = anime.find('a', class_='tooltip')['href']
            anime_page_url = f"https://www.anime-planet.com{anime_link}"
            
            # Visit the anime page and check if the season is finished
            anime_page_response = requests.get(anime_page_url, headers=headers)
            if anime_page_response.status_code == 200:
                anime_page_soup = BeautifulSoup(anime_page_response.text, 'html.parser')
                status_class = anime_page_soup.find('span', class_='status1')
                is_finished = status_class is not None
                anime_status[title] = is_finished
            else:
                print(f"Failed to retrieve data for {title}. Status code:", anime_page_response.status_code)

        return anime_status
    else:
        print("Failed to retrieve data. Status code:", response.status_code)  # Add this line for debugging
        return None

# Example usage
username = "MaplePlayz"
anime_status = check_anime_status(username)
if anime_status:
    print("Anime and their status:")
    for anime, status in anime_status.items():
        print(f"{anime}: {'Finished' if status else 'Not Finished'}")
