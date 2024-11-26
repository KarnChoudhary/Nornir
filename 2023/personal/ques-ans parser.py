import requests
from bs4 import BeautifulSoup

# URL of the website
url = 'https://learn.soic.in/learn/home/SOIC-Course/SOIC-Intensive-Course-English/section/302460/lesson/1889591'

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the questions and answers
    questions = soup.find_all('div', class_='question-class')
    answers = soup.find_all('div', class_='answer-class')

    # Extract and print the questions and answers
    for question, answer in zip(questions, answers):
        q_text = question.get_text(strip=True)
        a_text = answer.get_text(strip=True)
        print(f'Question: {q_text}')
        print(f'Answer: {a_text}')
        print('---')
else:
    print(f'Failed to retrieve the page. Status code: {response.status_code}')
