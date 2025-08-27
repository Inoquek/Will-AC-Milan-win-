from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from datetime import datetime

# Initialize lists to store scraped data
matches = []

# Define seasons to scrape (last 5 years from 2023-2024)
# seasons = ["2023-2024", "2022-2023", "2021-2022", "2020-2021", "2019-2020"]
# seasons = ["2022-2023","2023-2024","2024-2025"]
seasons = ["2023-2024"]

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode (no browser UI) 
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Base URL for Serie A results
base_url = "https://www.flashscore.co.uk/football/italy/serie-a-"

def scrape_match_details(match_url):
    """Scrape additional details from the match summary page."""
    print(f"Navigating to: {match_url}")
    driver.get(match_url)
    
    # Define expected statistics to ensure consistent keys
    '''    expected_stats = [
        "Expected_goals_(xG)", "Ball_possession", "Total_shots", "Shots_on_target",
        "Big_chances", "Corner_kicks", "Passes", "Yellow_cards", "Red_cards",
        "Shots_off_target", "Blocked_shots", "Shots_inside_the_box", "Shots_outside_the_box",
        "Hit_the_woodwork", "Headed_goals", "Touches_in_opposition_box", "Offsides",
        "Free_kicks", "Passes_in_final_third", "Crosses", "Throw_ins", "Fouls",
        "Tackles", "Clearances", "Interceptions", "Goalkeeper_saves"
    ]
    # Initialize section_titles with default values
    section_titles = {f"{stat}_home": "0" for stat in expected_stats}
    section_titles.update({f"{stat}_away": "0" for stat in expected_stats})'''
    section_titles = {}
    try:
        # Handle cookie consent popup (OneTrust)
        try:
            accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            accept_button.click()
            print("Clicked cookie consent accept button.")
        except:
            print("No cookie consent popup found or already handled.")    
    
        stats_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-analytics-alias='match-statistics'] button"))
        ) # Wait for the "Stats" tab button and click it to load statistics
        stats_tab.click()
        print("Clicked Stats tab.")


        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-analytics-context='tab-match-statistics'] .sectionHeader"))
        ) # Wait for sectionHeader elements within tab-match-statistics
        sections = driver.find_elements(By.CSS_SELECTOR, "div[data-analytics-context='tab-match-statistics'] .section .wcl-row_OFViZ")
        print(f"Found {len(sections)} sections.")

        for i, section in enumerate(sections):
            home_value = section.find_element(By.CLASS_NAME, "wcl-homeValue_-iJBW").text.strip().replace('\n',',')
            away_value = section.find_element(By.CLASS_NAME, "wcl-awayValue_rQvxs").text.strip().replace('\n',',')
            statistics_title = section.find_element(By.CLASS_NAME, "wcl-category_7qsgP").text.strip().replace(" ", "_")
            # Add statistic to global set
            '''if statistics_title in ["Passes", "Passes_in_final_third", "Crosses", "Tackles"]:
                section_titles[f"{statistics_title}_home"] = home_value.split('\n')[-1]
                section_titles[f"{statistics_title}_away"] = away_value.split('\n')[-1]
            else:
                # print([home_value, statistics_title, away_value])
                section_titles[f"{statistics_title}_home"] = home_value
                section_titles[f"{statistics_title}_away"] = away_value'''
            section_titles[f"{statistics_title}_home"] = home_value
            section_titles[f"{statistics_title}_away"] = away_value
            
        print("Scraped section titles successfully.") 
        print(section_titles)      
        return section_titles

    except Exception as e:
        print(f"Error scraping match details from {match_url}: {e}")
        return None

def scrape_season(season):
    url = f"{base_url}{season}/results/"
    driver.get(url)
    print(f"Scraping season {season} from {url}")

    # Handle cookie consent popup
    try:
        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        accept_button.click()
        print("Clicked cookie consent accept button.")
    except:
        print("No cookie consent popup found or already handled.")

    # Scroll and load all matches
    previous_match_count = 0
    for _ in range(10):  # Try multiple scrolls
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        try:
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "wclButtonLink"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
            time.sleep(1)
            show_more_button.click()
            print("Clicked 'Show more matches' button.")
            WebDriverWait(driver, 20).until(
                lambda driver: len(driver.find_elements(By.CLASS_NAME, "event__match")) > previous_match_count
            )
            time.sleep(3)
            match_elements = driver.find_elements(By.CLASS_NAME, "event__match")
            previous_match_count = len(match_elements)
            print(f"Matches loaded so far: {previous_match_count}")
            if previous_match_count >= 380:
                break
        except (TimeoutException, NoSuchElementException) as e:
            print(f"No more 'Show more matches' button or timeout: {e}")
            break

    # Collect match URLs
    match_elements = driver.find_elements(By.CLASS_NAME, "event__match")
    match_urls = list(set([match.find_element(By.TAG_NAME, "a").get_attribute("href") 
                           for match in match_elements 
                           if match.find_elements(By.TAG_NAME, "a") and "/match/" in match.find_element(By.TAG_NAME, "a").get_attribute("href")]))
    print(f"Found {len(match_urls)} match URLs")

    # Scrape each match
    for i, url in enumerate(match_urls):
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "duelParticipant__home"))
            )
            HomeTeam = driver.find_element(By.XPATH, "//*[contains(@class, 'duelParticipant__home')]").text.replace("\n", " ")
            GuestTeam = driver.find_element(By.XPATH, "//*[contains(@class, 'duelParticipant__away')]").text.replace("\n", " ")
            score = driver.find_element(By.CLASS_NAME, "detailScore__wrapper").text.strip().replace("-",":").replace("\n", "")
            match_date, match_time = driver.find_element(By.CLASS_NAME, "duelParticipant__startTime").text.split(" ")
            match_data = {
                "date": match_date,
                "time": match_time,
                "home_team": HomeTeam,
                "away_team": GuestTeam,
                "score": score,
                "match_url": url
            }
            additional_info = scrape_match_details(url)
            if additional_info:
                match_data.update(additional_info)
            matches.append(match_data)
            print(f"Scraped match {i+1}/{len(match_urls)}: {HomeTeam} vs {GuestTeam}")
        except Exception as e:
            print(f"Failed to scrape match {url}: {str(e)}")
            continue

def main():
    # Scrape each season
    for season in seasons:
        scrape_season(season)

    # Close the driver
    driver.quit()

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(matches)
    df.to_csv("serie_a_results_2023_2024_again.csv", index=False)
    print("Scraping completed. Data saved to serie_a_results_2023_2024_again.csv")


'''
def main(): 
    scrape_match_details("https://www.flashscore.co.uk/match/football/hI7JpOZ1/#/match-summary/match-summary")
'''

if __name__ == "__main__":
    main()