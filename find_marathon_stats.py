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
            mm_removed_colons = mm.replace(".", "_").replace("-", "_").replace(":", "_").replace('(', '_').replace(')', '_')
            metric = Metric( mm_removed_colons,'', 'gauge')
            if type(marathonmetrics['gauges'][mm][u'mean']) != list:
              metric.add_sample(mm_removed_colons, value=marathonmetrics['gauges'][mm][u'mean'],
                              labels={'name': mm})
              yield metric
              logging.info("%s:%d" % (mm, marathonmetrics['gauges'][mm][u'mean']))

            
         for mm in marathonmetrics['counters']:
            logging.info(mm)           
            mm_removed_colons = mm.replace(".", "_").replace("-", "_").replace(":", "_").replace('(', '_').replace(')', '_')
            metric = Metric( mm_removed_colons,'', 'counter')
            if type(marathonmetrics['counters'][mm][u'count']) != list:
              metric.add_sample(mm_removed_colons, value=marathonmetrics['counters'][mm][u'count'],
                              labels={'name': mm})
              yield metric
              logging.info("%s:%d" % (mm, marathonmetrics['counters'][mm][u'count']))

         for mm in marathonmetrics['min-max-counters']:
            logging.info(mm)           
            mm_removed_colons = mm.replace(".", "_").replace("-", "_").replace(":", "_").replace('(', '_').replace(')', '_')
            metric = Metric( mm_removed_colons,'', 'counter')
            if type(marathonmetrics['min-max-counters'][mm][u'max']) != list:
              metric.add_sample(mm_removed_colons, value=marathonmetrics['min-max-counters'][mm][u'max'],
                              labels={'name': mm})
              yield metric
              logging.info("%s:%d" % (mm, marathonmetrics['min-max-counters'][mm][u'max']))

         for mm in marathonmetrics['histograms']:
            logging.info(mm)           
            mm_removed_colons = mm.replace(".", "_").replace("-", "_").replace(":", "_").replace('(', '_').replace(')', '_')
            metric = Metric( mm_removed_colons,'', 'counter')
            if type(marathonmetrics['histograms'][mm][u'count']) != list:
              metric.add_sample(mm_removed_colons, value=marathonmetrics['histograms'][mm][u'count'],
                              labels={'name': mm})
              yield metric
              logging.info("%s:%d" % (mm, marathonmetrics['histograms'][mm][u'count']))

         for mm in marathonmetrics['system-metric']:
            logging.info(mm)
            mm_removed_colons = mm.replace(".", "_").replace("-", "_").replace(":", "_").replace('(', '_').replace(')', '_')
            metric = Metric( mm_removed_colons,'', 'counter')
            if type(marathonmetrics['system-metric'][mm][u'count']) != list:
              metric.add_sample(mm_removed_colons, value=marathonmetrics['system-metric'][mm][u'count'],
                              labels={'name': mm})
              yield metric
              logging.info("%s:%d" % (mm, marathonmetrics['system-metric'][mm][u'count'])) 

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
