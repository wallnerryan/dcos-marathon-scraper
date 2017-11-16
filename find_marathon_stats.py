#!/usr/bin/env python

from prometheus_client import start_http_server, Metric, REGISTRY
import requests
requests.packages.urllib3.disable_warnings()
import json
import commands
import sys, os
import time
import logging
logging.basicConfig(level=logging.DEBUG)

class HealthJsonCollector(object):
  def __init__(self, url, svc_u, svc_p):
    self._url = url
    self._svc_u = svc_u
    self._svc_p = svc_p
    self._token = "none"

  def get_token(self):
     logging.info("Getting New Auth Token")
     payload={"uid": self._svc_u, "password": self._svc_p }
     token_r = requests.post('%s/acs/api/v1/auth/login' % self._url, 
                             data=json.dumps(payload), 
                             headers={'Content-Type': 'application/json'},
                             verify=False)
     if token_r.status_code == 200:
       token_json=json.loads(token_r.content)
       self._token = token_json['token']

  def collect(self):

     r = requests.get('%s/marathon/metrics' % self._url,
                      headers={'Authorization': 'token='+self._token},
                      verify=False)

     # if failed, refresh token
     if r.status_code == 401:
         logging.info("Failed auth, getting new auth token")
         self.get_token()
         self.collect()
     else:
         marathonmetrics=r.json()
         for mm in marathonmetrics['gauges']:
            logging.info(mm)           
            mm_removed_periods = mm.replace(".", "_")
            mm_removed_dashes = mm_removed_periods.replace("-", "_")
            metric = Metric( mm_removed_dashes,'', 'gauge')
            if type(marathonmetrics['gauges'][mm][u'value']) != list:
              metric.add_sample(mm_removed_dashes, value=marathonmetrics['gauges'][mm][u'value'],
                              labels={'name': mm})
              yield metric
              logging.info("%s:%d" % (mm, marathonmetrics['gauges'][mm][u'value']))

            
         for mm in marathonmetrics['counters']:
            logging.info(mm)           
            mm_removed_periods = mm.replace(".", "_")
            mm_removed_dashes = mm_removed_periods.replace("-", "_")
            metric = Metric( mm_removed_dashes,'', 'counter')
            if type(marathonmetrics['counters'][mm][u'count']) != list:
              metric.add_sample(mm_removed_dashes, value=marathonmetrics['counters'][mm][u'count'],
                              labels={'name': mm})
              yield metric
              logging.info("%s:%d" % (mm, marathonmetrics['counters'][mm][u'count']))

         for mm in marathonmetrics['histograms']:
            logging.info(mm)           
            mm_removed_periods = mm.replace(".", "_")
            mm_removed_dashes = mm_removed_periods.replace("-", "_")
            metric = Metric( mm_removed_dashes,'', 'counter')
            if type(marathonmetrics['histograms'][mm][u'count']) != list:
              metric.add_sample(mm_removed_dashes, value=marathonmetrics['histograms'][mm][u'count'],
                              labels={'name': mm})
              yield metric
              logging.info("%s:%d" % (mm, marathonmetrics['histograms'][mm][u'count']))

         for mm in marathonmetrics['meters']:
            logging.info(mm)           
            mm_removed_periods = mm.replace(".", "_")
            mm_removed_dashes = mm_removed_periods.replace("-", "_")
            metric = Metric( mm_removed_dashes,'', 'gauge')
            if type(marathonmetrics['meters'][mm][u'count']) != list:
              metric.add_sample("%s_count" % mm_removed_dashes, value=marathonmetrics['meters'][mm][u'count'],
                              labels={'name': mm,
                                      'units': marathonmetrics['meters'][mm][u'units']})
              metric.add_sample("%s_m5_rate" % mm_removed_dashes, value=marathonmetrics['meters'][mm][u'm5_rate'],
                              labels={'name': mm,
                                      'units': marathonmetrics['meters'][mm][u'units']})
              metric.add_sample("%s_m15_rate" % mm_removed_dashes, value=marathonmetrics['meters'][mm][u'm15_rate'],
                              labels={'name': mm,
                                      'units': marathonmetrics['meters'][mm][u'units']})
              yield metric
              logging.info("%s:%d" % (mm, marathonmetrics['meters'][mm][u'count']))
          

if __name__ == "__main__":
   if len(sys.argv) > 1:
     if sys.argv[1] == "--help" or sys.argv[1] == "help" or sys.argv[1] == "-help":
       print """
            Make sure MARATHON_SVC_U, MARATHON_SVC_P, and DCOS_URL are set in the environment
            MARATHON_SVC_U: service user used to login to dcos
            MARATHON_SVC_P: service user password used to login to dcos
       
       USAGE:
       %s 
       """ % sys.argv[0]
       exit(0)

   uid = os.environ['MARATHON_SVC_U']
   uid_p = os.environ['MARATHON_SVC_P']
   dcos_url = os.environ['DCOS_URL']

   start_http_server(int(os.environ['PORT0']))
   REGISTRY.register(HealthJsonCollector(dcos_url, uid, uid_p))

   while True: time.sleep(1)
