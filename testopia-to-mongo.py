
import argparse

from util import mongo_tt, proxy

#since I don't have enough authority to get product related information
#I have add plans here manually
plans = ['4902', '4903', '4910', '4911', '4912', '4937',
         '4920', '4925', '4937', '4954']

def update_runs():
    for plan in plans:
        runs=proxy.TestPlan.get_test_runs(plan)
        for run in runs:
            run['name'] = 'runs'
            run_id = run.get('run_id')
            mongo_tt.update_one({'name':'runs', 'run_id':run_id},
                    {'$set': run}, upsert=True)

def update_case_runs():
    runs = mongo_tt.find({'name':'runs'}, {'run_id':1, '_id':0})
    runids = [r['run_id'] for r in runs]
    print(runids)
    for runid in runids:
        case_runs = proxy.TestRun.get_test_case_runs(runid)
        for case_run in case_runs:
            case_run['name'] = 'case_run'
            mongo_tt.update_one({'name':'case_run', 'case_run_id':
                case_run['case_run_id']}, {'$set':case_run}, upsert=True)

    for runid in runids:
        cases = proxy.TestRun.get_test_cases(runid)
        for case in cases:
            #use update_many, since a case may have many case_run
            mongo_tt.update_many({'name':'case_run', 
                    'case_id':case['case_id']}, {'$set':case},
                    upsert=True)


def update_testcase_bugs():
    #only to query cases that are failed or blocked to save server force
    cases = mongo_tt.find({'name':'case_run', 'case_run_status_id':{
                        '$in':[3,4,5,6]}}, {'case_id':1})
    caseids = [i['case_id'] for i in cases]
    caseids = set(caseids)          #avoid duplicate cases
    for case in caseids:
        print(case)
        bugs = proxy.TestCase.get_bugs(case)
        for bug in bugs:
            #I found a situation that a bug binded with a test case bug have no
            #run. I don't know why. So escape it
            if 'case_run_id' not in bug:
                continue
            bug['name'] = 'bugs'
            bug['case_id'] = case
            mongo_tt.update_one({'name':'bugs',
                'case_run_id':bug['case_run_id']}, {'$set':bug},
                upsert=True)

def main():
    parser = argparse.ArgumentParser(description='Import data from bugzilla.',
                usage='%(prog)s [-h] [run, case, bug]')
    parser.add_argument('obj', nargs='*', help='What do you want to update?' +
            ' run, case, or bug.')
    args = parser.parse_args()
    if 'run' in args.obj:
        update_runs()
        args.obj.remove('run')
    if 'case' in args.obj:
        update_case_runs()
        args.obj.remove('case')
    if 'bug' in args.obj:
        update_testcase_bugs()
        args.obj.remove('bug')
    if args.obj:
        print('Invalid argument! You should only use arg in [run, case, bug]!')



if __name__ == '__main__':
    main()

