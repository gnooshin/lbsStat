from gittle import Gittle

# repo_path = '/gdev/sm/ssgbot/errbot-plugins/LbsStat'
# repo_url = 'git://github.com/FriendCode/gittle.git'
#
# repo = Gittle(repo_path, origin_uri=repo_url)
# repo.auth(username="gnooshin", password="0Zk2ros!")
# repo.stage('lbsStat.html')
# repo.commit(name="Jeenwoo Park", email="gnoopy@shinsegae.com", message="SsgBot commit")
# repo.push()

# import pygithub3 as Github
# gh = Github("gnooshin", "0Zk2ros!")
# # for repo in g.get_user().get_repos():
# #     print repo.name
# gh.services.repos.Commits("gh-pages", , user="gnooshin",repo="https://github.com/gnooshin/lbsStat.git")
# g.commits.forBranch()


# from selenium import webdriver
# from depot.manager import DepotManager
# depot = DepotManager.get()
# driver = webdriver.PhantomJS()
# driver.set_window_size(1024, 768) # set the window size that you need
# driver.get('http://gnooshin.github.io/lbsStat/lbsStat.html')
# driver.save_screenshot('lbsstat.png')



from selenium import webdriver
import contextlib,time,sh

# @contextlib.contextmanager
# def quitting(thing):
#     yield thing
#     thing.quit()
# with quitting(webdriver.Firefox()) as driver:
#     driver.set_window_position(0, 0)
#     driver.set_window_size(1000, 400)
#     driver.get('file:///Users/jeenuine/PycharmProjects/ErrBots/lbsStat.html')
#     # driver.get('http://gnooshin.github.io/lbsStat/lbsStat.html')
#     time.sleep(5)
#     driver.get_screenshot_as_file('lbsstat.png')
CHART_URL_LOCAL='file:///gdev/sm/ssgbot/errbot-plugins/LbsStat/lbsStat.html'
BASE_DIR='/gdev/sm/ssgbot/errbot-plugins/LbsStat'


def gen_webshot(url,file):
    @contextlib.contextmanager
    def quitting(thing):
        yield thing
        thing.quit()
    with quitting(webdriver.Firefox()) as driver:
        driver.set_window_position(0, 0)
        driver.set_window_size(1000, 400)
        driver.get(url) #'http://gnooshin.github.io/lbsStat/lbsStat.html'
        time.sleep(5)
        driver.save_screenshot(file) #'lbsstat.png'
        print "##### pwd :"+str(sh.pwd())
        print "##### png file : "+str(file)
# gen_webshot('http://gnooshin.github.io/lbsStat/lbsStat.html','lbsstat.png')
#gen_webshot(CHART_URL_LOCAL,'lbsstat.png')
sh.cd(BASE_DIR)
print "####### cur dir: "+str(sh.pwd())
print sh.git.branch()
print sh.git.status()
# sh.git.add('lbsStat.html', 'lbsstat.png')
sh.git.commit('-q', '-m', '"SsgBot commits png and html 34  "', 'lbsstat.png', 'lbsStat.html')
sh.git.push('origin')

# import urllib2
# request = urllib2.Request(
#     'http://gnooshin.github.io/lbsStat/lbsStat.html',
#     headers={'User-Agent':'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 firefox/2.0.0.11'})
# page = urllib2.urlopen(request)
#
# with open('somefile.png','wb') as f:
#     f.write(page.read())
# f.close()