from flask import Flask, jsonify, request
import pandas as pd
from scipy import spatial
import geopy.distance
import numpy as np
import engines.delay_predictor_2 as DelayPredictor
import engines.delay_predictor as DelayPredictor_Reason
import math
import os
from patsy import dmatrices,dmatrix
from sklearn.linear_model import LogisticRegression

from pytictoc import TicToc
from scipy import stats
import datetime
now = datetime.datetime.now()

app = Flask (__name__)

import traceback
import logging
import os
import config 
from logging.config import dictConfig

import engines

dictConfig({
    'version': 1,
    'root': {
        'level': 'INFO'
    }
})
#setup logging
CONFIG = config.CONFIG
CURRENT_DATE = datetime.datetime.now().date()
LOGFILENAME = 'service_disruption_log_{}.log'.format(CURRENT_DATE)
if not os.path.exists(CONFIG.logPath):
    os.makedirs(CONFIG.logPath)
#initialize logging
LOGFILENAME = CONFIG.logPath + LOGFILENAME
logging.basicConfig(filename=LOGFILENAME, format='%(asctime)s  %(name)s:%(levelname)s:%(message)s')
LOGGER = logging.getLogger('service_disruption_predictor_log')
LOGGER.info("*** Prediction Restart t={} name={}".format(datetime.datetime.now(), __name__))

#setup data location
if not os.path.exists(CONFIG.carrierDataPath):
    os.makedirs(CONFIG.carrierDataPath)

#setup QUERY engine
QUERY = engines.QueryEngine(CONFIG.researchScienceConnString, CONFIG.bazookaAnalyticsConnString, CONFIG.bazookaReplConnString)




def api_json_output(results_df):
    results_df['Score'] = results_df['Score'].apply(np.int)
    #api_resultes_df = results_df[['loadID', 'Reason', 'Score']]
    loads=[]

    for i in results_df.index:
        load = results_df.loc[i]
        _loadid = load["loadID"].item()
        _reason = load["Reason"]
        _score = load["Score"].item()
        loads.append({
            "loadid": _loadid, 
            "Reason": _reason,
            "Score": _score
        })
    return loads

def service_predict():
    LOGGER.info("GET /search/ called")

    try:
        trainData_delay = QUERY.get_hist_load()
        trainData_model, trainData_feature = DelayPredictor.trainmodel(trainData_delay)
        testData_delay = QUERY.get_dynamic_load()
        delay_risk=DelayPredictor.delay_predictor(trainData_model, trainData_feature ,testData_delay)


        trainData_bounce = QUERY.get_hist_load()
        trainModel_bounce = DelayPredictor.train1()
        testData_bounce = QUERY.get_dynamic_load()
        bounce_risk=DelayPredictor.delay_predictor(trainModel_bounce,trainData_bounce,testData_bounce)

        return delay_risk,bounce_risk


    except Exception as ex:
        LOGGER.exception(ex)

        errormessage = {
            'Title': 'Something bad happened',
            'Message': traceback.format_exc()
        }
        return jsonify(errormessage), 500, {'Content-Type': 'application/json'}

if __name__=='__main__':
    service_predict()