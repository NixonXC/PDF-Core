from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def fetch_pdf_links_google(query):
    base_url = f"https://www.google.com/search?q={query}&num=3&as_filetype=pdf"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = [a['href'] for a in soup.find_all('a', href=True) if '.pdf' in a['href']][:1]
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
        for doc in docs[:1]:  # Get up to three results
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
    if engine == "google":
        data = fetch_pdf_links_google(query=pdf_name)
        print(data)
        return redirect(data[0])
    else:
        data = search_archive_org(book_title=pdf_name)
        print(data)
        return redirect(data[0]["url"])

    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 