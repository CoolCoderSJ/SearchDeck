import requests
from bs4 import BeautifulSoup, SoupStrainer
#from ScrapeSearchEngine.ScrapeSearchEngine import Duckduckgo, Yahoo
import cchardet, lxml, time

requests_session = requests.Session()

def google(query, que):
	query = query.replace(' ', '+')
	URL = f"https://google.com/search?q={query}"

	# desktop user-agent
	USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

	headers = {"user-agent" : USER_AGENT}

	resp = requests_session.get(URL, headers=headers)
	if resp.status_code == 200:
		#<h3 class="LC20lb DKV0Md">
		result_div = SoupStrainer(id="search")
		soup = BeautifulSoup(resp.text, "lxml", parse_only=result_div)
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
				desc = str(g.find("span", class_ = "aCOpRe"))
				if title != "None":
					item = {
						"title": title,
						"link": link,
						"desc": desc
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
	
	for result in soup.findAll(class_="result__body"):
		title = str(result.find('a'))
		desc = str(result.find(class_ ="result__snippet"))
		link = title.split('href="')[-1].split('"')[0]
		title = title.split('">')[-1].split("</a>")[0]
		results.append({"title": title, "link": link, "desc": desc})

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
	x = 0
	descs = []
	for result in soup.findAll(class_ = "compText"):
		desc = str(result.find("p", class_ = "fz-ms"))
		if desc != "None":
			descs.append(desc)
	for result in soup.findAll("h3",class_="title ov-h"):
		title = str(result.find('a'))
		link = title.split('href="')[-1].split('"')[0]
		title = title.split('">')[-1].split("</a>")[0]
		try:
			desc = descs[x]
		except:
			desc = "No Description."
		results.append({"title": title, "link": link, "desc": desc})
		x += 1
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
	if resp.status_code == 200:
		#<h3 class="LC20lb DKV0Md">
		result_div = SoupStrainer(id="search")
		soup = BeautifulSoup(resp.text, "lxml", parse_only=result_div)
		results = []
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
	headers = {"user-agent" : USER_AGENT}
	resp = requests_session.get(URL, headers=headers)
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

def yahoo_shopping(query, que):
	query = query.replace(' ', '+')
	URL = f"https://shopping.yahoo.com/search?p={query}"
	# desktop user-agent
	USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
	headers = {"user-agent" : USER_AGENT}
	resp = requests_session.get(URL, headers=headers)
	if resp.status_code == 200:
		soup = BeautifulSoup(resp.text, "lxml")
		results = []
		for g in soup.find_all('li', class_ = "fJNqPk"):
			anchors = g.find_all('a')
			if anchors:
				try:
					link = anchors[0]['href']
					link = "https://yahoo.com" + link
				except:
					link = "/"

				title = g.find("span", class_ = "FluidProductCell__Title-fsx0f7-9")
				title = str(title).split(">")
				try:
					title = title[1].split("<")[0]
				except:
					title = title[0]

				price = g.find("span", class_ = "FluidProductCell__PriceText-fsx0f7-10")
				price = str(price).split(">")
				try:
					price = price[1].split("<")[0]
				except:
					price = price[0]

				if title != "None":
					item = {
						"title": title,
						"link": link,
						"price": price
					}
					results.append(item)
	else:
		results = [{"title": "We're sorry, but Bing returned a 429. Please try again later.", "link": "/"}]
	
	# return results
	que.put(results)

def word_dictionary(word):
	r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{word}")
	try:
		r = r.json()
	except:
		r = {"title": "", "message": "", "resolution": ""}
	if "title" in r and "message" in r and "resolution" in r:
		return []
	else:
		return r

def infobox(query):
	r = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json&pretty=1")
	try:
		r = r.json()
	except:
		r = {'Abstract': ""}
	if r['Abstract'] == "":
		return []
	else:
		return r

def ansbox(query):
	r = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json&pretty=1")
	try:
		r = r.json()
	except:
		r = {'Answer': ""}
	if r['Answer'] == "":
		return []
	else:
		return r
