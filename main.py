import datetime
import json

import tornado.ioloop
import tornado.web

import util
from util import mongo_tt, proxy

class PersonHandler(tornado.web.RequestHandler):

    #the mongodb store status as 1,2,3,4,5,6, transfer to noticable strings
    status=['IDLE', 'PASS', 'FAIL', 'RUNNING', 'PAUSE', 'BLOCK', 'ERROR']
    def get(self, person):
            if '@' not in person:
                person = person + '@suse.com'
            userid, realname = util.get_id_by_email(person)
            #get all UNPASSED case_run of person
            assigned = mongo_tt.find({'name':'case_run', 'assignee':userid,
                            'iscurrent':1, 'case_run_status_id':{'$ne':2}})

            items={}
            '''items stores params that will be sent to template, like follow:
            {runid_1: {'summary':'summary_of_run',
                       'cases':[{case_run_id:xx,...{bugs:[bug1,bug2]},},
                                {case2....}]},
             runid_2: {'summary':'summary_of_run',...}
            }'''
            for i in assigned:
                i.pop('_id')
                run_id = i.pop('run_id')
                item = items.setdefault(run_id, {})

                case_run_status = i['case_run_status_id']
                i['case_run_status_id'] = self.status[case_run_status - 1]

                #get summary of run
                if 'summary' not in item:
                    run_info = mongo_tt.find_one({'name':'runs', 'run_id':run_id})
                    run_summary = run_info.get('summary')
                    item['summary'] = run_summary

                #show bugs of test case
                bugs = mongo_tt.find({'name':'bugs', 'case_id':i['case_id']},
                        {'_id':0, 'bug_id':1, 'bug_status':1, 'short_desc':1})
                if 'bugs' not in i:
                    i['bugs'] = [bug for bug in bugs]
                    print(i['bugs'])

                item_cases = item.setdefault('cases', [])
                item_cases.append(i)
            self.render('index.html', person=realname, items=items)

if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/([\d\w]+)', PersonHandler),
        #(r'/ajax/([\d\w]+)', AjaxPersonHandler),
        ], debug=True, template_path='templates')
    app.listen(8010)
    tornado.ioloop.IOLoop.instance().start()
