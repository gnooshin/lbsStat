#  -*- coding: utf-8 -*-
# encoding=utf8
import sys,os

from errbot import BotPlugin, botcmd
import requests
import pickle
import jmespath
import pandas as pd
import numpy as np
from slacker import Slacker

# import json, ast,pprint
# from sets import Set
from errbot.backends.slack import SlackRoom

reload(sys)
sys.setdefaultencoding('utf8')
prodHost='https://ssglbs.shinsegae-inc.com'
stageHost='http://202.3.20.124'
# def get_visit_stat(uri,branch,company,start,end):
headers={'request_type':'1', 'access_token':'79E5F0BA4352C7D23BAF36618DF605E881E458BB0B803BF49E4DA8DE75741BEC23A28F0E795FCFA36FE7F89E573C6C05AB4D5738EA15D8511C4B4301095E5995B1E12ED670A78BC3AA014DECB98F30B2AD3F26BBBF510E9AF5A39D1D094DD1FDC381A7A05DB1C59D11A9B2AAC0231F30FDE8ACABD0A42DD948E997BDC6CB44C4',
          'Content-Type':'application/json','Accept-Encoding':'gzip, deflate',
          'x-ssg-deviceid':'88888888-8888-8888-8888-888888888888', 'x-ssg-userid':'C88888888/restful_check'}
# global audiences=set([])
BASE_DIR='errbot-plugins/LbsStat/'
ROSTER= BASE_DIR+'roster.pkl'
IMG_PATH=BASE_DIR+'lbsstat.png'
CHART_URL='http://gnooshin.github.io/lbsStat/lbsStat.html'
SVC_NAME='SSG LBS Platform Stat '


def get_visit_stat(uri,branch,company,start,end):
    args={'branch_id':branch,'brand_id':'-1','term':'30', 'company_id':company, 'start_date':start, 'end_date':end}
    resp = requests.get(uri,headers=headers,params=args)

    if resp.status_code != 200:
        raise requests.exception.HTTPError ('GET /v1/mms/map_graph_datas.do?map_id=1 {}'.format(resp.status_code))
#    for item in resp.json()['map_graph_data_list'][0]['map_graph_edge_list'][:3]:
    # pp = pprint.PrettyPrinter(indent=2)
    return resp
def gen_webshot(url,file):
    from selenium import webdriver
    import contextlib,time
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
        print "##### png file : "+str(file)

class LbsStat(BotPlugin):
    """SSG LbsStat plugin for Errbot"""
    audiences=set([])
    def callback_message(self, mess):
        if len(self.audiences) == 0:
            if os.path.isfile(ROSTER):
                self.audiences=pickle.load(open(ROSTER, 'rb'))
            else:
                print "mess.to"+str(mess.to)+",  mess.frm:"+str(mess.frm)
                receiver=(mess.to if str(mess.to) in str(mess.frm) else mess.frm )
                self.send(receiver,SVC_NAME+' 수신자 명단이 비어 있습니다. 받을 사람들에 대한 정보를 addpeople 명령어로 넣어주세요')
        if mess.body.find('ssglbs stat') != -1:
            statStr=self.draw_chart()
            att='[{'
            att+=' "fallback": "30일 간의 신세계 백화점 강남점 통계: 링크를 누르면 자세한 차트 확인 가능 - @gnoopy - 박진우 올림 - http://gnooshin.github.io/lbsStat/lbsStat.html",'
            att+='"title": "30일 간의 신세계 백화점 강남점 통계",'
            att+='"title_link": "http://gnooshin.github.io/lbsStat/lbsStat.html",'
            att+='"text": "상세하게 차트를 확인하시려면 위 제목을 클릭 부탁드립니다.",'
            att+='"image_url": "http://gnooshin.github.io/lbsStat/lbsstat.png",'
            att+='"color": "#764FA5"'
            att+='}]'

           #files.upload(f.name,None,None,'log.txt',None, "Here's the log file of interest",'logsmons')

            for person in self.audiences:
                slack = Slacker(self._bot.token)
                slack.chat.post_message(person, statStr, username='@gnoopy', as_user='@gnoopy',
                     parse=None, link_names=None, attachments=att,
                     unfurl_links=None, unfurl_media=None, icon_url=None,
                     icon_emoji=None)
                # self.send(self.build_identifier(person),statStr)

    def draw_chart(self):
        from datetime import datetime, timedelta
        yesterday = (datetime.today() - timedelta(days=1))
        startdt=(yesterday-timedelta(days=30)).strftime('%Y%m%d')
        enddt=yesterday.strftime('%Y%m%d')
        response=get_visit_stat(prodHost+"/v1/lms/visit_stats_date_graph.do",'11','55',startdt,enddt)
        # print "rest"+str(resp)
        #resp=json.load(open('visitdata.json','rb'))
        resp=response.json()
        exp_new = jmespath.compile('visit_graph_date_list[*].new_visit')
        new_visit_arr=exp_new.search(resp)
        exp_re = jmespath.compile('visit_graph_date_list[*].re_visit')
        re_visit_arr=exp_re.search(resp)
        total_visit_arr=np.array(new_visit_arr)+np.array(re_visit_arr)

        response=get_visit_stat(prodHost+"/v1/lms/campaign_stats_date_graph.do",'11','55',startdt,enddt)
        resp=response.json()
        exp_and = jmespath.compile('campaign_graph_date_list[*].android_count')
        android_cpgn_arr=exp_and.search(resp)
        exp_ios = jmespath.compile('campaign_graph_date_list[*].ios_count')
        ios_cpgn_arr=exp_ios.search(resp)

        exp_dates = jmespath.compile('campaign_graph_date_list[*].xkey_str')
        dates=exp_dates.search(resp)
        xaxis= [ pd.to_datetime(date,format='%Y%m%d').strftime('%m-%d') for date in dates ]
        total_cpgn_arr=np.array(android_cpgn_arr)+np.array(ios_cpgn_arr)
        files = os.listdir(os.curdir)
        print "cur dir:"+str(files)
        with open(BASE_DIR+"lbsStat.html", "wt") as fout:
            with open(BASE_DIR+'template.html', "rt") as fin:
                for line in fin:
                    line=line.replace('**dateMMdd**' ,str(xaxis))
                    line=line.replace('**newVisit**' ,str(new_visit_arr))
                    line=line.replace('**reVisit**'  ,str(re_visit_arr))
                    line=line.replace('**cpgnCount**',str(list(total_cpgn_arr)))
                    # print line
                    fout.write(line)
                fout.close()
        import sh
        sh.cd(BASE_DIR)
        print "#######"+str(sh.pwd())
        repo_origin = 'https://github.com/gnooshin/lbsStat.git'
        # sh.git.remote('add', 'sh-pages', repo_origin)
        sh.git.add('.')
        sh.git.commit('-m', '"SsgBot commits html"')
        sh.git.push('origin', 'origin/gh-pages')

        #TODO: should push lbsStat.html to github
        gen_webshot(CHART_URL,IMG_PATH)
        # sh.git.remote('add', 'sh-pages', repo_origin)
        print "#######"+str(sh.pwd())

        sh.git.add('.')
        sh.git.commit('-m', '"SsgBot commits png"')
        sh.git.push('origin', 'origin/gh-pages')


#보낼 문장 생성
#-------------------------------------------------------------
        ret="> *SSG LBS 신세계 백화점 강남점의 어제("+ yesterday.strftime('%m/%d')+ ") 방문자수*\n"
        # ret+=' 조회 기간 : '+str(start)+"\n"
        ret+='> 전체 방문자 : '+str(total_visit_arr[len(total_visit_arr)-1])+"\n"
        ret+='> 신규 방문자 : '+str(new_visit_arr[len(new_visit_arr)-1])+"\n"
        ret+='> 재 방문자 : '+str(re_visit_arr[len(re_visit_arr)-1])+"\n"
        ret+='> 캠페인 이벤트 발생 : '+str(total_cpgn_arr[len(total_cpgn_arr)-1])+"\n"
#-------------------------------------------------------------
        return ret
    def push_file(self, name):
        print "abc"
        # git add lbsStat.html lbsstat.png
        # git commit -m "add html and png files"
        # git push

    @botcmd(split_args_with=None)
    def addpeople(self,msg,args):
        """SSG LBS stat 수신자 리스트 추가"""
        print "args:"+str(args)
        if args is None or len(args) == 0:
            return
        for arg in args:
            self.audiences.add(arg)
        ret=SVC_NAME+"수신자 리스트\n"
        ret+=str(list(self.audiences))
        pickle.dump(self.audiences, open(ROSTER, 'wb'))
        return ret

    @botcmd
    def cleanroster(self,msg,args):
        """SSG LBS stat 수신자 리스트 초기화"""
        self.audiences.clear()
        pickle.dump(self.audiences, open(ROSTER, 'wb'))

    @botcmd
    def hello(self, msg, args):
        """Just ping command"""
        return "Hello, world! How may I help you"

    @botcmd
    def stat(self, msg, args):
        """Check the statistics simply"""
        uri=prodHost+"/v1/lms/visit_stats.do"
        branch='11'
        company='55'
        start='20160407'
        end='20160407'
        args={'branch_id':branch, 'company_id':company, 'start_date':start, 'end_date':end}
        resp = requests.get(uri,headers=headers,params=args)

        if resp.status_code != 200:
            raise requests.exception.HTTPError ('GET /v1/mms/map_graph_datas.do?map_id=1 {}'.format(resp.status_code))
    #    for item in resp.json()['map_graph_data_list'][0]['map_graph_edge_list'][:3]:
    #        print item

        # pp = pprint.PrettyPrinter(indent=2)
        # print pp.pprint(ast.literal_eval(json.dumps(resp.json()['visit_stats_vo'])))
        ret= '``` 조회 기간 : '+str(start)+' ~ '+str(end)+"\n"
        ret+='전체 방문자 : '+str(resp.json()['visit_stats_vo']['n_tot_visit'])+"\n"
        ret+='신규 방문자 : '+str(resp.json()['visit_stats_vo']['n_new_visit'])+"\n"
        ret+='재  방문자 : '+str(resp.json()['visit_stats_vo']['n_re_visit'])+"```"
        return ret

