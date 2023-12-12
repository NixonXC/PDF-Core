from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup, Comment
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

base_url = r'https://annas-archive.org'

class Annas_Archive_Parser():
    def __init__(self, params):
        self.params = params

    def get_top_five_links(self):
        book_name = self.params["book-name"]
        url = f"https://annas-archive.org/search?index=&q={book_name}"
        response = requests.get(url=url)
        data = response.text

        soup = BeautifulSoup(data, 'html.parser')

        # Find the container of each result
        result_containers = soup.find_all("div", class_="h-[125] flex flex-col justify-center")

        top_five_links = []
        for result in result_containers[:5]:
            link = result.find("a")
            top_five_links.append(link)

        links_1 = []
        for link in top_five_links:
            href_value = link.get('href')
            links_1.append(href_value)

        commented_a_tag = soup.find_all(string=lambda text: isinstance(text, Comment) and 'class="js-vim-focus custom-a' in text)

        links_2 = []
        for a_tag in commented_a_tag:
            a_soup = BeautifulSoup(a_tag, 'html.parser')
            href_value = a_soup.find('a')['href']
            links_2.append(href_value)

        links_1.extend(links_2)

        return links_1
    
    def url_returns(self): 
        links = self.get_top_five_links()
        data = links[:5]
        final_links = []
        for item in data: 
            final_url = base_url + item
            final_links.append({
                'id': final_url.replace("https://annas-archive.org/md5/",""),
                'url': final_url,
            })
        return final_links

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
    
    results = []

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
        initialise = Annas_Archive_Parser(params={"book-name": "Art of war"})
        final_links = initialise.url_returns()
        results = [{'pdf_name': f"ID: {links['id']}", 'pdf_url': links['url']} for links in final_links]
    else:
        return redirect("/")

    return render_template('results.html', results=results)

    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)