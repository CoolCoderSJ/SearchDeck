import requests
from bs4 import BeautifulSoup, SoupStrainer
#from ScrapeSearchEngine.ScrapeSearchEngine import Duckduckgo, Yahoo
import cchardet, lxml

requests_session = requests.Session()

def google(query, que):
	query = query.replace(' ', '+')
	URL = f"https://google.com/search?q={query}"

	# desktop user-agent
	USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

	headers = {"user-agent" : USER_AGENT}

	resp = requests_session.get(URL, headers=headers)
	print(resp.status_code)
	if resp.status_code == 200:
		#<h3 class="LC20lb DKV0Md">
		result_div = SoupStrainer(id="search")
		soup = BeautifulSoup(resp.text, "lxml", parse_only=result_div)
		results = []
		#print(soup.find_all('div', class_='g'))
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
	else:
		results = [{"title": "We're sorry, but Google returned a 429. Please try again later.", "link": "/"}]
	
	#return results
	que.put(results)

def bing(term, que):
	term = term.replace(" ", "+")
	url = f"http://www.bing.com/search?q={term}"

	resp = requests_session.get(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'}) 

	soup = BeautifulSoup(resp.text, "lxml")

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
	#return results_to_return
	que.put(results_to_return)

def ddg(q, que):
	q = q.replace(" ", "+")
	resp = requests_session.get("https://html.duckduckgo.com/html/?q="+q, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'})

	result_div = SoupStrainer(id="links")
	soup = BeautifulSoup(resp.text, "lxml", parse_only=result_div)

	results = []
	
	for result in soup.findAll("h2",class_="result__title"):
		title = str(result.find('a'))
		link = title.split('href="')[-1].split('"')[0]
		title = title.split('">')[-1].split("</a>")[0]
		results.append({"title": title, "link": link})

	que.put(results)

	"""
	ddg = Duckduckgo(q, "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0")
	results = []
	if len(ddg) > 15:
		ddg = ddg[:15]
	only_title_tags = SoupStrainer("title")
	for link in ddg:
		r = requests_session.get(link, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'})
		soup = BeautifulSoup(r.text, 'lxml', parse_only=only_title_tags)
		try:
			title = soup.title.text
			results.append({"title":title, "link":link})
		except:
			continue
		#shortlink = link.split("://")[1]
		#title = requests_session.get(f"https://url-title.now.sh/{shortlink}").text
	#return results
	"""

def yahoo(q, que):
	q = q.replace(" ", "+")

	resp = requests_session.get("https://search.yahoo.com/search?q="+q, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'}) 
	result_div = SoupStrainer(id="results")
	soup = BeautifulSoup(resp.text, "lxml", parse_only=result_div)

	results = []

	for result in soup.findAll("h3",class_="title ov-h"):
		title = str(result.find('a'))
		link = title.split('href="')[-1].split('"')[0]
		title = title.split('">')[-1].split("</a>")[0]
		results.append({"title": title, "link": link})
	"""yahoo = Yahoo(q, "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0")
	results = []
	for link in yahoo:
		resp = requests_session.get(link, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'})
		soup = BeautifulSoup(resp.text, 'lxml') 
		try:
			title = soup.title.text
			results.append({"title":title, "link":link})
		except:
			continue
	#return results"""
	que.put(results)

def gshop(query, que):
	query = query.replace(' ', '+')
	URL = f"https://google.com/search?q={query}&tbm=shop"

	# desktop user-agent
	USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

	headers = {"user-agent" : USER_AGENT}

	resp = requests_session.get(URL, headers=headers)
	print(resp.status_code)
	if resp.status_code == 200:
		#<h3 class="LC20lb DKV0Md">
		result_div = SoupStrainer(id="search")
		soup = BeautifulSoup(resp.text, "lxml", parse_only=result_div)
		results = []
		#print(soup.find_all('div', class_='g'))
		for g in soup.find_all(class_ = 'sh-dlr__list-result'):
			anchors = g.find_all('a')
			if anchors:
				try:
					link = anchors[0]['href']
					link = "https://google.com" + link
				except:
					link = "/"
				title = g.find('h3')
				title = str(title).split(">")
				try:
					title = title[1].split("<")[0]
				except:
					title = title[0]

				rating = g.find("span")
				rating = str(rating).split(">")
				try:
					rating = rating[1].split("<")[0]
				except:
					rating = rating[0]
				

				if title != "None":
					item = {
						"title": title,
						"link": link,
						"rating": rating
					}
					results.append(item)
	else:
		results = [{"title": "We're sorry, but Google returned a 429. Please try again later.", "link": "/"}]
	
	# return results
	que.put(results)

def bing_shopping(query, que):
	query = query.replace(' ', '+')
	URL = f"https://www.bing.com/shop?q={query}"
	# desktop user-agent
	USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
	print(URL)
	headers = {"user-agent" : USER_AGENT}
	resp = requests_session.get(URL, headers=headers)
	print(resp.status_code)
	if resp.status_code == 200:
		soup = BeautifulSoup(resp.text, "lxml")
		results = []
		for g in soup.find_all('li', class_ = "br-item"):
			anchors = g.find_all('a')
			if anchors:
				try:
					link = anchors[1]['href']
				except:
					link = "/"

				title = anchors[2]
				title = title.find("div")
				title = str(title).split(">")
				try:
					title = title[1].split("<")[0]
				except:
					title = title[0]

				price = g.find("div", class_ = "pd-price")
				price = str(price).split(">")
				try:
					price = price[1].split("<")[0]
				except:
					price = price[0]

				if title != "None":
					item = {
						"title": title,
						"link": link,
						"price": price,
						"img": g.find("img")['src']
					}
					results.append(item)
	else:
		results = [{"title": "We're sorry, but Bing returned a 429. Please try again later.", "link": "/"}]
	
	# return results
	que.put(results)