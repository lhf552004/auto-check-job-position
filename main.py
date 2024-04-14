import os
import requests
from urllib.parse import quote_plus
import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
def get_career_page(company_name, subscription_key):
    search_url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": f"{company_name} careers page",
              "textDecorations": True, "textFormat": "HTML"}

    response = requests.get(search_url, headers=headers, params=params)
    search_results = response.json()

    for webpage in search_results.get("webPages", {}).get("value", []):
        url = webpage.get("url")
        if "careers" in url or "jobs" in url:
            return url  # Returns the first URL that contains 'careers' or 'jobs'

    return None  # No relevant URL found


def check_job_openings(company_career_urls):
    found_positions = False
    for company, url in company_career_urls.items():
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Example: Find all job titles in <div> tags with class 'job-title'
            jobs = soup.find_all('div', class_='job-title')
            print("Jobs count." + str(len(jobs)))
            for job in jobs:
                print(job)
                if 'software developer' in job.text.lower() and 'saint john' in job.text.lower():
                    print("Softwarev developer job found.")
                    found_positions = True
                    send_email(company, url)
        except Exception as e:
            print(e)
    return found_positions

def send_email(company, url):
    msg = EmailMessage()
    msg.set_content('New software developer position available! Check the careers page.\n' + url)
    msg['Subject'] = 'Job Alert: New Position from ' + company
    msg['From'] = os.environ.get('EMAIL_USER')
    msg['To'] = os.environ.get('EMAIL_RECEIVER')
    
    # Set up the SMTP server
    server = smtplib.SMTP(os.environ.get('SMTP_SERVER'), 587)
    server.starttls()
    server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASSWORD'))
    server.send_message(msg)
    server.quit()


def main():
    subscription_key = os.getenv('BING_API_KEY')
    companies = os.getenv('COMPANIES', '').split('|')
    # Initialize an empty dictionary
    company_career_urls = {}

    urls = []
    for company in companies:
        url = get_career_page(company, subscription_key)
        if url:
            print(f"Found career page for {company}: {url}")
            company_career_urls[company] = url
            # urls.append(url)
        else:
            print(f"No career page found for {company}")
    check_job_openings(company_career_urls)

if __name__ == "__main__":
    main()
