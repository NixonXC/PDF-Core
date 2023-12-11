from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

from bs4 import BeautifulSoup
import requests

def fetch_anna(book_name):
    return redirect("/")


def fetch_pdf_links_google(query):
    base_url = f"https://www.google.com/search?q={query}&num=3&as_filetype=pdf"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = [a['href'] for a in soup.find_all('a', href=True) if '.pdf' in a['href']][:5]
        return pdf_links
    else:
        print(f"Error: Unable to fetch Google search results. Status code: {response.status}")
        return ["/"]

def search_archive_org(book_title):
    base_url = "https://archive.org/advancedsearch.php"
    params = {
        'q': f'title:"{book_title}" AND mediatype:texts',
        'fl[]': 'identifier,title,creator',
        'output': 'json'
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        docs = data.get('response', {}).get('docs', [])

        results = []
        for doc in docs[:3]:  # Get up to three results
            identifier = doc.get('identifier', '')
            title = doc.get('title', '')
            creator = doc.get('creator', '')
            url = f"https://archive.org/details/{identifier}"

            results.append({
                'identifier': identifier,
                'title': title,
                'creator': creator,
                'url': url
            })

        return results
    else:
        return ["/"]



@app.route('/search', methods=["POST"])
def search():
    pdf_name = request.form.get("pdf_name")
    engine = request.form.get("engine")
    
    results = []  # Initialize results list outside the if-else blocks

    if engine == "google":
        pdf_links = fetch_pdf_links_google(query=pdf_name)
        for pdf_link in pdf_links:
            filename = os.path.basename(pdf_link)
            # Append each result to the results list
            results.append({'pdf_name': filename, 'pdf_url': pdf_link})
    elif engine == "archive":
        archive_results = search_archive_org(book_title=pdf_name)
        results = [{'pdf_name': result['title'], 'pdf_url': result['url']} for result in archive_results]
    elif engine == "anna":
        return "Anna's archive scraping is still under development, please try to search via Google or archive.org"
    else:
        return redirect("/")

    return render_template('results.html', results=results)

    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)