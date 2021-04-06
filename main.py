import web
import requests
from bs4 import BeautifulSoup
from ScrapeSearchEngine.ScrapeSearchEngine import Duckduckgo, Yahoo
from multiprocessing import Process, Queue
import sys

urls = (
    '/', 'search'
)
app = web.application(urls, globals())
render = web.template.render("templates")

def google(query, que):
	query = query.replace(' ', '+')
	URL = f"https://google.com/search?q={query}"

	# desktop user-agent
	USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

	headers = {"user-agent" : USER_AGENT}
	resp = requests.get(URL, headers=headers)

	if resp.status_code == 200:
		soup = BeautifulSoup(resp.content, "html.parser")
		results = []
		for g in soup.find_all('div', class_='g'):
			anchors = g.find_all('a')
			if anchors:
				try:
					link = anchors[0]['href']
				except:
					link = "/"
				title = g.find('h3')
				title = str(title).split(">")
				try:
					title = title[1].split("<")[0]
				except:
					title = title[0]
				if title != "None":
					item = {
						"title": title,
						"link": link
					}
					results.append(item)
		que.put(results)

def bing(term, que):
	term = term.replace(" ", "+")
	url = f"http://www.bing.com/search?q={term}"


	getRequest = requests.get(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'}) 
	htmlResult = getRequest.content


	soup = BeautifulSoup(htmlResult, features="html5lib")

	[s.extract() for s in soup('span')]
	unwantedTags = ['strong', 'cite']
	for tag in unwantedTags:
		for match in soup.findAll(tag):
			match.replaceWithChildren()
	results = soup.findAll('li', { "class" : "b_algo" })
	results_to_return = []
	for result in results:
		title = str(result.find('h2'))
		link = title.split('href="')[-1].split('"')[0]
		title = title.split('">')[-1].split("</a>")[0]
		title = title.replace(" ", " ").replace("<h2>", "").replace("</h2>", "")
		desc = str(result.find('p')).replace(" ", " ").replace("<p>", "").replace("</p>", "")
		results_to_return.append({"title": title, "link":link, "desc":desc})
	que.put(results_to_return)

def ddg(q, que):
	ddg = Duckduckgo(q, "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0")
	results = []
	for link in ddg:
		r = requests.get(link, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'})
		soup = BeautifulSoup(r.text, 'html.parser') 
		titles = ""
		for title in soup.find_all('title'): 
			title = str(title)
			try:
				titles += str(title.split("<title>")[1].split("</title>")[0])+"\n"
			except:
				titles = "No Title Found."
		results.append({"title":titles, "link":link})
	que.put(results)

def yahoo(q, que):
	yahoo = Yahoo("How to scrape Yahoo with Python", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0")
	results = []
	for link in yahoo:
		r = requests.get(link, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'})
		soup = BeautifulSoup(r.text, 'html.parser') 
		titles = ""
		for title in soup.find_all('title'): 
			title = str(title)
			try:
				titles += str(title.split("<title>")[1].split("</title>")[0])+"\n"
			except:
				titles = "No Title Found."
		results.append({"title":titles, "link":link})
	que.put(results)

class search:
	def GET(self):
		i = web.input(q="")
		if i.q != "":
			queue1 = Queue()
			queue2 = Queue()
			queue3 = Queue()
			queue4 = Queue()
			p = Process(target= google, args= (i.q, queue1))
			p.start()
			p2 = Process(target= bing, args= (i.q, queue2))
			p2.start()
			p3 = Process(target= ddg, args= (i.q, queue3))
			p3.start()
			p4 = Process(target= yahoo, args= (i.q, queue4))
			p4.start()
			goog = queue1.get()
			b = queue2.get()
			duckduckgo = queue3.get()
			yhoo = queue4.get()
			p.join()
			return render.search(goog, b, duckduckgo, yhoo, i.q)
		else:
			return render.home()

if __name__ == "__main__":
    app.run()