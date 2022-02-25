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
	'/settings', 'settings',
	'/about', 'about'
)

app = web.application(urls, globals())
render = web.template.render("templates")
session = web.session.Session(app, web.session.DiskStore('sessions'))

class supersecretstylesheet:
	def GET(self):
		web.header("Content-Type", "text/css")
		return open("templates/style.css", "rb").read()

cache = {}

class about:
	def GET(self):
		return render.about()

class settings:
	def GET(self):
		if not session.get("user"):
			raise web.seeother('/login')
		return render.settings(db[session.get("user")])
	def POST(self):
		i = web.input()
		engines = {
            "Google": "",
            "Bing": "",
            "Yahoo": "",
            "DuckDuckGo": ""
        }
		sort = None
		selected_typ = i.typ
		typ = {
            "text": "",
            "image": "",
            "video": "",
            "news": "",
            "maps": "",
            "shopping": ""
        }
		typ[selected_typ] = "checked"
        
		if "Google" in i:
			engines["Google"] = 'checked'
		if "Bing" in i:
			engines["Bing"] = 'checked'
		if "DuckDuckGo" in i:
			engines["DuckDuckGo"] = 'checked'
		if "Yahoo" in i:
			engines["Yahoo"] = 'checked'

		if "cache" in i:
			cache = "Enabled"
		else:
			cache = "Disabled"

		db[session.get("user")] = {
			"theme": "dark",
			"engines": engines,
			"default_sort": sort,
			"default_typ": typ,
			"cache": cache
		}
		raise web.seeother("/")

class search:
	def GET(self):
		if session.get("user"):
			logged_in = True
		else:
			logged_in = False
		i = web.input(q="", sort="table", typ="text")
		if i.q == "":
			if logged_in:
				stin = db[session.get("user")]
			else:
				stin = {
					"engines": {
                    "Google": "checked",
                    "Bing": "checked",
                    "DuckDuckGo": "checked",
                    "Yahoo": "checked"
                    },
					"default_typ": {
                        "text": "checked",
                        "image": "",
                        "video": "",
                        "news": "",
                        "maps": "",
                        "shopping": ""
                    }
				}
			return render.home(logged_in, stin)
		
		else:
			r = requests.get("http://httpbin.org/ip")
			global cache
			#clear cache if cache is too big
			if len(cache) > 25:
				cache = {}
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
					engines = db[session.get("user")]['engines']
				else:
					engines = ['Google', 'Bing', 'DuckDuckGo', 'Yahoo']

			dictionary = []
			info = []
			ans = []

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
					dictionary = word_dictionary(i.q)
					info = infobox(i.q)
					ans = ansbox(i.q)
					if "Yahoo" in engines and "Google" in engines and "DuckDuckGo" in engines and "Bing" in engines and logged_in:
						try:
							cache[session.get("user")][i.q] = {"google":goog, "bing":b, "yahoo":yhoo, "duckduckgo":duckduckgo,"last_updated":time.time()}
						except:
							pass
				data = []
				e = []
				f = []
				for g in goog:
					g['engine'] = "Google"
					e.append(g)
					f.append(g['title'])

				for bingresult in b:
					bingresult['engine'] = "Bing"
					e.append(bingresult)
					f.append(bingresult['title'])
				
				for d in duckduckgo:
					d['engine'] = "DuckDuckGo"
					e.append(d)
					f.append(d['title'])

				for y in yhoo:
					y['engine'] = 'Yahoo'
					e.append(y)
					f.append(y['title'])

				def getnum(s0, s1):
					s0 = s0.lower()
					s1 = s1.lower()
					s0List = s0.split(" ")
					s1List = s1.split(" ")
					num = len(list(set(s0List)&set(s1List)))
					return round(num/len(s0List)*100)

				g = set(f)
				counter = 0
				so = []
				for item in e:
					if "stackoverflow.com" in item['link']:
						thing = ""
						for x in so:
							if getnum(x[0]['title'], item['title']) >= 90:
								thing = x
								break
						if thing:
							so.remove(thing)
							engines = x[1]
							engines.append(item['engine'])
							x = [x[0], engines]
							so.append(x)
						else:
							engines = [item['engine']]
							x = [item, engines]
							so.append(x)
					else:
						thing = ""
						for x in data:
							if getnum(x[0]['title'], item['title']) >= 90:
								thing = x
								break
						if thing:
							data.remove(thing)
							engines = x[1]
							engines.append(item['engine'])
							x = [x[0], engines, x[2]]
							data.append(x)
						else:
							engines = [item['engine']]
							x = [item, engines, counter]
							data.append(x)
						counter += 1
				
				done = 0
				data2 = []
				for item in data:
					if done == len(data):
						break
					if data.index(item) != item[2]:
						data.insert(item[2], data.pop(data.index(item)))
						done += 1
				data2, data = data, data2

				for item in so:
					data.append(item)
				
				for item in data2:
					data.append(item)

				print("--- %s seconds ---" % (time.time() - start_time))
				return render.text(data, i.q, dictionary, info, ans, logged_in)
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
				soup = BeautifulSoup(duckduckgo.content, "html.parser")
				images = soup.findAll('img')
				imgs = []
				for image in images:
					image = str(image)
					link = image.split('src="')[-1].split('"')[0]
					imgs.append(link)
				duckduckgo = imgs
				yhoo = requests.get(f"https://images.search.yahoo.com/search/images;_ylt=A0geJaQetm1gPx0AGURXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3BpdnM-?p={query}&fr2=piv-web&fr=opensearch", headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'}).content
				soup = BeautifulSoup(yhoo, "html.parser")
				images = soup.findAll('img')
				imgs = []
				for image in images:
					image = str(image)
					link = image.split('src="')[-1].split('"')[0]
					imgs.append(link)
				yhoo = imgs
			elif i.q != "" and typ == "video":
				query = i.q.replace(" ", "+")
				goog = YoutubeSearch(query, max_results=100).to_dict()
				b, duckduckgo, yhoo = [], [], []
			elif i.q != "" and typ == "news":
				query = i.q.replace(" ", "+")
				news = GoogleNews()

				news.set_lang('en')
				news.set_encode('utf-8')

				news.search(query)
				
				goog = news.results()
				b, duckduckgo, yhoo = [], [], []
			elif i.q != "" and typ == "maps":
				goog, b, duckduckgo, yhoo = [], [], [], []
			elif i.q != "" and typ == "shopping":
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
						p = Process(target= gshop, args= (i.q, queue1))
						p.start()
					if "Bing" in engines:
						queue2 = Queue()
						p2 = Process(target= bing_shopping, args= (i.q, queue2))
						p2.start()
					if "Yahoo" in engines:
						queue3 = Queue()
						p3 = Process(target= yahoo_shopping, args= (i.q, queue3))
						p3.start()
					if "Google" in engines:
						goog = queue1.get()
						p.join()
					if "Bing" in engines:
						b = queue2.get()
						p2.join()
					if "Yahoo" in engines:
						yhoo = queue3.get()
						p3.join()
					if "Yahoo" in engines and "Google" in engines and "DuckDuckGo" in engines and "Bing" in engines and logged_in:
						try:
							cache[session.get("user")][i.q] = {"google":goog, "bing":b, "yahoo":yhoo, "duckduckgo":duckduckgo,"last_updated":time.time()}
						except:
							pass
			return render.search(goog, b, duckduckgo, yhoo, i.q, sort, typ, engines, logged_in, dictionary, info, ans)
			

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
				db[i.user] = {"theme": "dark", "engines": {
                    "Google": "checked",
                    "Bing": "checked",
                    "DuckDuckGo": "checked",
                    "Yahoo": "checked"
                    },
					"default_typ": {
                        "text": "checked",
                        "image": "",
                        "video": "",
                        "news": "",
                        "maps": "",
                        "shopping": ""
                    }, "default_sort": "table", "cache": "Enabled"}
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
				db[i.user] = {"theme": "dark", "engines": {
                    "Google": "checked",
                    "Bing": "checked",
                    "DuckDuckGo": "checked",
                    "Yahoo": "checked"
                    },
					"default_typ": {
                        "text": "checked",
                        "image": "",
                        "video": "",
                        "news": "",
                        "maps": "",
                        "shopping": ""
                    }, "default_sort": "table", "cache": "Enabled"}
			raise web.seeother("/")
		else:
			raise web.seeother("/signup?code=1")
		##os.system("clear")

if __name__ == "__main__":
    app.run()