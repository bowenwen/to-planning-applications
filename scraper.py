import requests
import sys
import os
import time

DATA_DIR = 'data'
DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), DATA_DIR)

wardcodes = ["W01","W02","W03","W04","W05","W06","W07","N08","N09","N10","W11",
             "W12","W13","S14","N15","N16","W17","S18","S19","S20","S21","S22",
             "N23","N24","N25","N26","S27","S28","S29","S30","S31","S32","N33",
             "N34","E35","E36","E37","E38","E39","E40","E41","E42","E43","E44"]

apptyps = ["0","1","2"]

request_url = "http://app.toronto.ca/DevelopmentApplications/dwr/call/plaincall/MapSearchService.searchApplications.dwr"

session_id = 'AD485EE3CA6FA7518C3A5501AFF5AAA6911'

# add 'c0-param1':'string:WARDCODE' and 'scriptSessionId':session_id 
# for a full payload
payload = {
  'callCount':'1',
  'page':'/DevelopmentApplications/mapSearchSetup.do?action=init',
  'httpSessionId':'',
  'c0-scriptName':'MapSearchService',
  'c0-methodName':'searchApplications',
  'c0-id':'0',
  'c0-param0':'string:S',
  'c0-param2':'string:',
  'c0-param3':'string:',
  'c0-param4':'string:',
  'c0-param5':'string:',
  'c0-param6':'string:',
  'c0-param7':'string:',
  'c0-param8':'string:',
  'c0-param9':'string:',
  'c0-param10':'string:',
  'c0-param11':'string:',
  #'c0-param12':'string:0', #app type can vary
  'c0-param13':'string:',
  'c0-param14':'string:', #2018 update
  'c0-param15':'string:', #2018 update
  'batchId':'0'
}


def download_request(wardcode,apptyp):

  f = open(os.path.join(DATA_PATH, "{0}_{1}".format(wardcode,apptyp)), 'w')

  # add the desired wardcode to the payload
  payload["c0-param1"] = "string:" + wardcode

  # add the desired app type to the payload
  payload["c0-param12"] = "string:" + apptyp

  # this may have to change, unclear when the session id expires
  payload['scriptSessionId'] = session_id

  print("{0}_{1}...".format(wardcode,apptyp)),
  sys.stdout.flush()

  # make the request and write the response to ./data/wardcode
  r = requests.post(request_url, data=payload)
  f.write(r.text)
  
  f.close()
  r.close()
  print "done!"


def run():
  for ward in wardcodes:
        for app in apptyps:
                  time.sleep(5) #sleep to prevent server block
                  download_request(ward,app)
	

if __name__ == "__main__":
  run()