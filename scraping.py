import requests
from bs4 import BeautifulSoup

url = "https://realpython.github.io/fake-jobs/"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

jobs = soup.find_all("div", class_="card-content")

for job in jobs[:10]:
    title = job.find("h2").text.strip()
    company = job.find("h3").text.strip()
    location = job.find("p", class_="location").text.strip()

    print("Job Title:", title)
    print("Company:", company)
    print("Location:", location)
    print("-" * 40)