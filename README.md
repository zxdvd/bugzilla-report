### bugzilla-report
Pull data from bugzilla and testopia and restruct the data.

#### Why?
1. Bugzilla is heavy and slow (network problem).
2. My cases distributed in a lot of plans, runs, it's hard to get a overview of all my cases.

#### How?
1. Pull the data from bugzilla using xmlrpc api and store the data in local mongodb.
2. Tornado backend + mongodb + boostrap == a fast local cute bugzilla

#### Todo
1. Currenly the testopia part is finished, bugzilla part is on the go.
2. I want to have a admin page to manage the settings.
3. Maybe there will have a "FATE" tab. (I've found the api and got data from Fate.)

#### Knowing issues
1. Ben reported that some bugs were not linked to related test case 
(I know how it happened but I need time to fix it).
2. Yue reported some cases were removed from the run in bugzilla but still showed.
