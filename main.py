import web
web.config.debug = False
from multiprocessing import Process, Queue
import sys, time
from replit import db
from ast import literal_eval
from scrapers import *
import random
from youtube_search import YoutubeSearch
from GoogleNews import GoogleNews



urls = (
    '/', 'search',
	'/login', 'login',
	'/signup', 'signup',
	'/settings', 'settings'
)

app = web.application(urls, globals())
render = web.template.render("templates")
session = web.session.Session(app, web.session.DiskStore('sessions'))


cache = {}

class settings:
	def GET(self):
		if not session.get("user"):
			raise web.seeother('/login')
		return render.settings(db[session.get("user")])
	def POST(self):
		i = web.input()
		engines = []
		sort = i.sort
		typ = i.typ
		if "Google" in i:
			engines.append("Google")
		if "Bing" in i:
			engines.append("Bing")
		if "DuckDuckGo" in i:
			engines.append("DuckDuckGo")
		if "Yahoo" in i:
			engines.append("Yahoo")

		if "cache" in i:
			cache = "Enabled"
		else:
			cache = "Disabled"

		db[session.get("user")] = {
			"theme": "dark",
			"engines": f"{engines}",
			"default_sort": sort,
			"default_typ": typ,
			"cache": cache
		}
		raise web.seeother("/")

class search:
	def GET(self):
		r = requests.get("http://httpbin.org/ip")
		print(r.json()['origin'])
		global cache
		#clear cache if cache is too big
		if len(cache) > 25:
			cache = {}
		for user in db:
			print(user)
		i = web.input(q="", sort="table", typ="text")
		if session.get("user"):
			logged_in = True
		else:
			logged_in = False
		engines = []
		sort = i.sort
		typ = i.typ
		if "Google" in i:
			engines.append("Google")
		if "Bing" in i:
			engines.append("Bing")
		if "DuckDuckGo" in i:
			engines.append("DuckDuckGo")
		if "Yahoo" in i:
			engines.append("Yahoo")

		if "Google" not in i and "Bing" not in i and "DuckDuckGo" not in i and "Yahoo" not in i:
			if logged_in:
				engines = literal_eval(db[session.get("user")]['engines'])
			else:
				engines = ['Google', 'Bing', 'DuckDuckGo', 'Yahoo']



		if i.q != "" and typ == "text":
			start_time = time.time()
			goog = []
			b = []
			duckduckgo = []
			yhoo = []
			use_cache = False
			try:
				#if within 2 days of last cache, use cache
				#cache per user
				if cache[session.get("user")][i.q]["last_updated"]+172800 > time.time() and random.randint(1, 10) == 5:
					use_cache = True
			except:
				pass
			print(use_cache)
			if use_cache:
				goog = cache[session.get("user")][i.q]["google"]
				b = cache[session.get("user")][i.q]["bing"]
				duckduckgo = cache[session.get("user")][i.q]["duckduckgo"]
				yhoo = cache[session.get("user")][i.q]["yahoo"]
			else:
				if "Google" in engines:
					queue1 = Queue()
					p = Process(target= google, args= (i.q, queue1))
					p.start()
				if "Bing" in engines:
					queue2 = Queue()
					p2 = Process(target= bing, args= (i.q, queue2))
					p2.start()
				if "DuckDuckGo" in engines:
					queue3 = Queue()
					p3 = Process(target= ddg, args= (i.q, queue3))
					p3.start()
				if "Yahoo" in engines:
					queue4 = Queue()
					p4 = Process(target= yahoo, args= (i.q, queue4))
					p4.start()
				if "Google" in engines:
					goog = queue1.get()
					p.join()
				if "Bing" in engines:
					b = queue2.get()
					p2.join()
				if "DuckDuckGo" in engines:
					duckduckgo = queue3.get()
					p3.join()
				if "Yahoo" in engines:
					yhoo = queue4.get()
					p4.join()
				if "Yahoo" in engines and "Google" in engines and "DuckDuckGo" in engines and "Bing" in engines and logged_in:
					try:
						cache[session.get("user")][i.q] = {"google":goog, "bing":b, "yahoo":yhoo, "duckduckgo":duckduckgo,"last_updated":time.time()}
					except:
						pass
			print("--- %s seconds ---" % (time.time() - start_time))
			return render.search(goog, b, duckduckgo, yhoo, i.q, sort, typ, engines, logged_in)
		elif i.q != "" and typ == "image":
			query = i.q.replace(" ", "+")
			goog = requests.get(f"https://google.com/search?q={query}&tbm=isch", headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'}).content
			soup = BeautifulSoup(goog, "html.parser")
			images = soup.findAll('img')
			imgs = []
			for image in images:
				image = str(image)
				link = image.split('src="')[-1].split('"')[0]
				imgs.append(link)
			goog = imgs
			b = requests.get(f"https://bing.com/images/search?q={query}&form=HDRSC2", headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'}).content
			soup = BeautifulSoup(b, "html.parser")
			images = soup.findAll('img')
			imgs = []
			for image in images:
				image = str(image)
				link = image.split('src="')[-1].split('"')[0]
				if link.startswith("/rp"):
					link = f"https://bing.com/images/search?q={query}&form=HDRSC2" + link
				if link != "<img alt=":
					imgs.append(link)
			b = imgs
			duckduckgo = requests.get(f"https://duckduckgo.com/?q={query}&ia=images", headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'})
			print(duckduckgo.content, file=open("ree.html", "a"))
			soup = BeautifulSoup(duckduckgo.content, "html.parser")
			images = soup.findAll('img')
			print(images)
			imgs = []
			print()
			for image in images:
				print("reee")
				image = str(image)
				print(image)
				link = image.split('src="')[-1].split('"')[0]
				print(link)
				imgs.append(link)
			duckduckgo = imgs
			print(duckduckgo)
			yhoo = requests.get(f"https://images.search.yahoo.com/search/images;_ylt=A0geJaQetm1gPx0AGURXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3BpdnM-?p={query}&fr2=piv-web&fr=opensearch", headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'}).content
			soup = BeautifulSoup(yhoo, "html.parser")
			images = soup.findAll('img')
			imgs = []
			for image in images:
				image = str(image)
				link = image.split('src="')[-1].split('"')[0]
				imgs.append(link)
			yhoo = imgs
			return render.search(goog, b, duckduckgo, yhoo, i.q, sort, typ, engines, logged_in)
		elif i.q != "" and typ == "video":
			query = i.q.replace(" ", "+")
			goog = YoutubeSearch(query, max_results=100).to_dict()
			b, duckduckgo, yhoo = [], [], []
			return render.search(goog, b, duckduckgo, yhoo, i.q, sort, typ, engines, logged_in)
		elif i.q != "" and typ == "news":
			query = i.q.replace(" ", "+")
			news = GoogleNews()

			news.set_lang('en')
			news.set_encode('utf-8')

			news.search(query)

			goog = news.results()
			b, duckduckgo, yhoo = [], [], []
			return render.search(goog, b, duckduckgo, yhoo, i.q, sort, typ, engines, logged_in)
		elif i.q != "" and typ == "maps":
			goog, b, duckduckgo, yhoo = [], [], [], []
			return render.search(goog, b, duckduckgo, yhoo, i.q, sort, typ, engines, logged_in)
		else:
			if logged_in:
				try:
					engines = literal_eval(db[session.get("user")]['engines'])
				except:
					engines = db[session.get("user")]['engines']
			else:
				engines = ['Google', 'Bing', 'DuckDuckGo', 'Yahoo']
			if logged_in:
				stin = db[session.get("user")]
			else:
				stin = {
					"engines": "['Google', 'Bing', 'DuckDuckGo', 'Yahoo']",
					"default_typ": "text"
				}
			return render.home(logged_in, stin)

class login:
	def GET(self):
		##os.system("clear")	
		i = web.input(code=0)
		msg = ""
		if i.code == "1":
			msg = "An error occurred while logging you in. Please try again or contact a deveoper."
		return render.login(msg)
		##os.system("clear")	
		 
	def POST(self):
		##os.system("clear")	
		i = web.input()
		r = requests.post("https://sjauth.coolcodersj.repl.co/apil", data={"user":i.user, "passw":i.passw, "cn":"SearchDeck"})
		if r.text == "True":
			session.user = i.user
			if i.user not in db:
				db[i.user] = {"theme": "dark", "engines": "['Google', 'Bing', 'DuckDuckGo', 'Yahoo']", "default_typ": "text", "default_sort": "table", "cache": "Enabled"}
			raise web.seeother("/")
		else:
			raise web.seeother("/login?code=1")
		##os.system("clear")

class signup:
	def GET(self):
		##os.system("clear")
		i = web.input(code=0)
		msg = ""
		if i.code == "1":
			msg = "An error occurred while signing you up. Please try again or contact a deveoper."	
		return render.signup(msg)
		##os.system("clear")	
		 
	def POST(self):
		##os.system("clear")	
		i = web.input()
		r = requests.post("https://sjauth.coolcodersj.repl.co/apisi", data={"user":i.user, "passw":i.passw, "cn":"SearchDeck"})
		if r.text == "True":
			session.user = i.user
			if i.user not in db:
				db[i.user] = {"theme": "dark", "engines": "['Google', 'Bing', 'DuckDuckGo', 'Yahoo']", "default_typ": "text", "default_sort": "table", "cache": "Enabled"}
			raise web.seeother("/")
		else:
			raise web.seeother("/signup?code=1")
		##os.system("clear")

if __name__ == "__main__":
    app.run()