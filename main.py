
import tornado.ioloop
import tornado.web

import util
from util import mongo_bz, mongo_tt, proxy

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class ExpireRunHandler(tornado.web.RequestHandler):
    def get(self, runid):
        try:
            mongo_tt.update_one({'name':'runs', 'run_id': int(runid)},
                    {'$set': {'expire':1}})
        except:
            pass

class PersonHandler(tornado.web.RequestHandler):

    @staticmethod
    def get_cases(userid):

        #the mongodb store status as 1,2,3,4,5,6, transfer to noticable strings
        status=['IDLE', 'PASS', 'FAIL', 'RUNNING', 'PAUSE', 'BLOCK', 'ERROR']

        #get all UNPASSED case_run of person
        all_case_run= mongo_tt.find({'name':'case_run', 'assignee':userid,
            'iscurrent':1, 'case_run_status_id':{'$ne':2}}, {'_id':0})

        items={}
        '''items stores params that will be sent to template, like follow:
        {runid_1: {'summary':'summary_of_run',
                   'cases':[{case_run_id:xx,...{bugs:[bug1,bug2]},},
                            {case2....}]},
         runid_2: {'summary':'summary_of_run',...}
        }'''
        #get expired runs
        expired_run = []
        for i in mongo_tt.find({'name':'runs', 'expire':1}, {'run_id':1}):
            expired_run.append(i['run_id'])

        for i in all_case_run:
            #escape cases in expired run
            run_id = i.pop('run_id')
            if run_id in expired_run:
                continue

            item = items.setdefault(run_id, {})
            #get summary of run
            if 'summary' not in item:
                run_info = mongo_tt.find_one({'name':'runs', 'run_id':run_id})
                run_summary = run_info.get('summary')
                item['summary'] = run_summary

            case_run_status = i['case_run_status_id']
            i['case_run_status_id'] = status[case_run_status - 1]

            #show bugs of test case
            bugs = mongo_tt.find({'name':'bugs', 'case_id':i['case_id']},
                    {'_id':0, 'bug_id':1, 'bug_status':1, 'short_desc':1})
            if 'bugs' not in i:
                i['bugs'] = [bug for bug in bugs]

            item_cases = item.setdefault('cases', [])
            item_cases.append(i)
        return items

    @staticmethod
    def get_bugs(email):
        bugs = {}
        results = mongo_bz.find({'creator':email, 'is_open': True})
        for item in results:
            prod = item.pop('product')
            item_bugs = bugs.setdefault(prod, [])
            item_bugs.append(item)
        return bugs

    def get(self, person):
            if '@' not in person:
                person = person + '@suse.com'
            userid, realname = util.get_id_by_email(person)
            testcases = self.get_cases(userid)
            bugs = self.get_bugs(person)
            self.render('person.html', realname=realname, testcases=testcases,
                    bugs=bugs)

if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/expirerun/([\d]+)', ExpireRunHandler),
        (r'/([.@\d\w]+)', PersonHandler),
        ], debug=True, template_path='templates')
    app.listen(8010)
    tornado.ioloop.IOLoop.instance().start()
