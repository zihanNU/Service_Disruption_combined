import pyodbc
import pandas as pd
import numpy as np
import math
import datetime
import os
from patsy import dmatrices,dmatrix
from sklearn.linear_model import LogisticRegression

now = datetime.datetime.now()
now_tz=datetime.datetime.now().astimezone().tzinfo
now = pd.Timestamp(now).tz_localize(now_tz)



def get_dummies(data):
    dummies=pd.get_dummies(data['Code'])
    data['Appt_dummy']=dummies['Appt'].tolist()
    data['Notice_dummy']=dummies['Notice'].tolist()
    data['Open_dummy']=dummies['Open'].tolist()
    return data

def generate_results(daily_results):
    progress =["Available", "Covered", "Dispatched", "Loading Start", "Picked Up", "Unloading Start", "Delivered",
                  "Invoiced"]
    # loadtype<-c
    result_file="DelayPredictor" + now.strftime("%Y%m%d%H%M")+".csv"
    stoptype =["PickUp", "Delivery"]

    columnnames  =['LoadID','ProgressType','Parent_Customer','LoadType','NextStop_Type','NextStop_City/State','ETA','RiskScore','LeadingReason']
    result_df = pd.DataFrame( columns=columnnames)
    loadids=set (daily_results['LoadID'].tolist())
    for lid in loadids:
        loaddata=daily_results[daily_results['LoadID']==lid]
        if len(loaddata[loaddata['arrived']== 0])>0:
            nextstop=loaddata[loaddata['arrived']== 0].iloc[0]   #needs to verify whether it is loc or iloc
            stop_result={'LoadID':lid,
                            'ProgressType': progress[int(loaddata.iloc[0]['ProgressType'])],
                            'Parent_Customer':loaddata.iloc[0]['Customer'],
                            'LoadType':loaddata.iloc[0]['Load_M_B'],
                            'NextStop_Type': stoptype[int(nextstop['PDType'])],
                            'NextStop_City/State':nextstop['StateCode'],
                            'ETA':str(nextstop['ETA']),   # there is a problem in ETA data type
                            'RiskScore':int(nextstop['RiskScore']),
                            'LeadingReason':nextstop['Reason']
                                        }
            result_df=result_df.append(stop_result, ignore_index=True)
        else:
            result_df =result_df.append({'LoadID':lid,
                            'ProgressType': progress[int(loaddata.iloc[0]['ProgressType'])],
                            'Parent_Customer':loaddata.iloc[0]['Customer'],
                            'LoadType':loaddata.iloc[0]['Load_M_B'],
                            'NextStop_Type':'-',
                            'NextStop_City/State':'-',
                            'ETA':'-',
                            'RiskScore':'-',
                            'LeadingReason':'-'}, ignore_index=True)
    result_df.to_csv(result_file,index=False)
    return(0)

def ontime_score(testData,threshold):
    relaxation = 0.98
    threshold=threshold * relaxation
    A_P = 1
    D_M = 0
    # thresholds<-quantile(testData$ontime_prob,c(D_level,C_level,B_level,A_level),names=FALSE)
    thresholdscore = 50.0
    for i in range(len(testData)):
        if  testData['ontime_prob'].iloc[i] > threshold:
            lowerbound = threshold
            upperbound = A_P
            L_score = thresholdscore / 20
            H_score = 5
        else:
            lowerbound = D_M
            upperbound = threshold
            H_score  = thresholdscore / 20
            L_score = 0

        testData['SafeScore'].iloc[i]=(L_score+(testData['ontime_prob'].iloc[i]-lowerbound) * (H_score-L_score) / (upperbound-lowerbound))
    return (testData)

def reason(coef,outputdata,inputdata,flag):
    if flag==1:
        names = ["preStop_OnTime", "preStop_Duration", "dist", "f_rate", "cust_rate"]
        reasons = ["PreStop_Delay", "PreStop_Duration", "Distance", "Facility", "Customer"]
    if flag==2:
        names = ["preStop_OnTime", "preStop_Duration", "dist", "f_rate", "cust_rate","carrier_rate","latebooking"]
        reasons = ["PreStop_Delay", "PreStop_Duration", "Distance", "Facility", "Customer","Carrier","Late_Book"]
    if flag==3:
        names = ["preStop_OnTime", "preStop_Duration", "dist", "f_rate", "cust_rate","carrier_rate"]
        reasons = ["PreStop_Delay", "PreStop_Duration", "Distance", "Facility", "Customer","Carrier"]
    refervalue =[]
    coef = coef[0][3:]  # there is dimensional problem, coef is a 2d matrix, we need to be careful with that.
    #coef=coef.fillna(0, inplace=True)
    for i in range (0,len(names)):
        refervalue.append(pd.DataFrame.mean(inputdata[names[i]]))
    for i in outputdata.index:
        delta = (outputdata[names].loc[i]-refervalue).tolist() * coef
        #output['Reason'].loc[i] = np.where(output['Reason'].loc[i] == "" or output['Reason'].loc[i].isnull(),reasons[np.argmin(delta)],output['Reason'].loc[i])
        # we do not use np.where as it returns an array. we could use tolist() to change the one element array into a number, but it may be resource consuming
        outputdata['Reason'].loc[i] =reasons[np.argmin(delta)]  if outputdata['Reason'].loc[i] == ""  else outputdata['Reason'].loc[i]
    return (outputdata)

def gml_stage(inputdata,outputdata,flag):
    # for stage 1, no carrier is booked
    # instead of using C(Code) but dummies, will make sure there is no dimensional change, i.e. maybe some dataset do not have all the levels of categories, if we use C(), it will be one dimension less than the trainning set
    if flag==1:
        X_test = dmatrix('Appt_dummy + Notice_dummy+ preStop_OnTime + preStop_Duration + dist + f_rate + cust_rate', outputdata,
                         return_type='dataframe')
        y, X = dmatrices('ontime ~ Appt_dummy + Notice_dummy + preStop_OnTime + preStop_Duration + dist + f_rate + cust_rate', inputdata,
                         return_type='dataframe')
    elif flag==2:
        y, X = dmatrices(
            'ontime ~ Appt_dummy + Notice_dummy + preStop_OnTime + preStop_Duration + dist + f_rate + cust_rate + carrier_rate + latebooking',
            inputdata, return_type='dataframe')
        X_test = dmatrix(
            'Appt_dummy + Notice_dummy+ preStop_OnTime + preStop_Duration + dist + f_rate + cust_rate + carrier_rate + latebooking',
            outputdata, return_type='dataframe')
    else:
        y, X = dmatrices(
            'ontime ~ Appt_dummy + Notice_dummy+ preStop_OnTime + preStop_Duration + dist + f_rate + cust_rate + carrier_rate', inputdata,
            return_type='dataframe')
        X_test = dmatrix('Appt_dummy + Notice_dummy + preStop_OnTime + preStop_Duration + dist + f_rate + cust_rate + carrier_rate',
                         outputdata, return_type='dataframe')
    model = LogisticRegression(fit_intercept=False)
    mdl = model.fit(X, np.ravel(y))
    rate_result = model.predict(X_test)
    rate = model.predict_proba(X_test)[:,1]
    # dummy_ranks = pd.get_dummies(inputdata['Code'], prefix='Code')
    # cols_to_keep = ['preStop_OnTime','preStop_Duration','dist','f_rate','cust_rate']
    # data = inputdata[cols_to_keep].join(dummy_ranks.ix[:, 'Code_1':])
    # data['intercept'] = 1.0
    return rate,rate_result,model.coef_


def get_results(traindata,testdata,flag):
    for Type in set(traindata['PDType'].tolist()):
        if len(testdata[testdata['PDType']==Type].axes[0])> 0:
            rate, delay_result,coef = gml_stage(traindata[traindata['PDType'] == Type ], testdata[testdata['PDType'] == Type],flag)
            testdata['ontime_prob'][testdata['PDType'] == Type] = rate
            testdata['ontime_pred'][testdata['PDType'] == Type] = delay_result
            threshold = pd.DataFrame.mean(traindata[traindata.PDType == Type]['ontime'])
            testdata[testdata['PDType'] == Type] = ontime_score (testdata[testdata['PDType'] == Type], threshold)
            testdata['ontime_pred'][testdata['PDType'] == Type] = (rate > threshold * 0.98)
            testdata["Reason"][(testdata['ETA_ontime'] == 0) &  (testdata['arrived'] == 0 )& (testdata['Reason'].isin(["","NAN"])) ] = "ETA_Delay"
            testdata["ontime_pred"][testdata['ETA_ontime'] == 0] = -2
            if len(testdata[(testdata['PDType']==Type) & (testdata['SafeScore']<2.5) & (testdata['arrived'] == 0)].axes[0])>0:
                testdata[(testdata['PDType']==Type)  &(testdata['ontime_prob']<0.95)& (testdata['arrived'] == 0)] = reason(coef,testdata[(testdata['PDType']==Type)  &(testdata['ontime_prob']<0.95)& (testdata['arrived']== 0)],traindata[traindata['PDType']==Type],flag)
    return (testdata)



def delay_predictor(trainData, testData):

    """main recommendation function

    Args:
    carrier_load: Pandas DF with historical loads for the carrier.
    trucks_df: Pandas DF with truck(s) (orig,dest,ready date, etc.) sent to search()
    """
    testData = get_dummies(testData)
    trainData = get_dummies(trainData)
    testData['ontime_prob'] = -1
    testData['ontime_pred'] = -1
    testData['SafeScore'] = -1
    testData['RiskScore'] = -1
    testData['CheckScore'] = -1
    testData_1 = testData[testData['ProgressType'] == 1]
    if len(testData_1.axes[0]) > 0:
        testData_1[testData_1['StopSequence'] == 1] = get_results(trainData[trainData['StopSequence'] == 1],
                                                                  testData_1[testData_1['StopSequence'] == 1], 1)
        max_stop = max(testData_1.NumStops) + 1
        nrow_testData_1 = len(testData_1)
        for k in range(2, max_stop):
            for i in range(nrow_testData_1):
                if testData_1['StopSequence'].iloc[i] == k:
                    if testData_1['arrived'].iloc[i - 1] == 0:
                        testData_1['preStop_OnTime'].iloc[i] = testData_1['ontime_prob'].iloc[i - 1]
            testData_1[testData_1['StopSequence'] == k] = get_results(trainData[trainData['StopSequence'] > 1],
                                                                      testData_1[testData_1['StopSequence'] == k], 1)

    # Stage 2
    testData_2 = testData[testData['ProgressType'] > 1]
    testData_2[testData_2['StopSequence'] == 1] = get_results(trainData[trainData['StopSequence'] == 1],
                                                              testData_2[testData_2['StopSequence'] == 1], 2)
    # testData[(testData['ProgressType'] > 1) & (testData['StopSequence'] == 1)]=Get_Results(trainData[trainData['StopSequence'] == 1],testData[(testData['ProgressType'] > 1) & (testData['StopSequence'] == 1)], 1)
    max_stop = max(testData_2.NumStops) + 1
    nrow_testData_2 = len(testData_2)
    for k in range(2, max_stop):
        # for i in testData_2.index:
        for i in range(nrow_testData_2):
            if testData_2['StopSequence'].iloc[i] == k:
                if testData_2['arrived'].iloc[i - 1] == 0:
                    testData_2['preStop_OnTime'].iloc[i] = testData_2['ontime_prob'].iloc[i - 1]
        testData_2[testData_2['StopSequence'] == k] = get_results(trainData[trainData['StopSequence'] > 1],
                                                                  testData_2[testData_2['StopSequence'] == k], 3)
    # for k in range(2, max_stop):
    #     #for i in testData_2.index:
    #     for  i in range(nrow_testData_2):
    #         if testData_2['StopSequence'].iloc[i] == k:
    #             if testData_2['arrived'].iloc[i - 1] == 0:
    #                 testData_2['preStop_OnTime'].iloc[i] = testData_2['ontime_prob'].iloc[i - 1]
    #     testData_2[testData_2['StopSequence']==k]=Get_Results(trainData[trainData['StopSequence'] > 1], testData_2[testData_2['StopSequence'] == k],3)
    # testData_2_pred.append(Get_Results(trainData[trainData['StopSequence'] > 1], testData_2[testData_2['StopSequence'] == k],3))
    testData_df = pd.concat([testData_1, testData_2])
    testData_df['RiskScore'] = 100 - testData_df['SafeScore'] * 20

    # numstop = max(testData_df['NumStops'])

    # results = testData_df[["LoadID", "LoadDate", "Customer", "Load_M_B", "ProgressType", "StopSequence",
    #                        "SafeScore", "Reason", "Arrival"]].sort(['LoadDate', 'LoadID'], ascending=[1, 0])
    testData_df['CheckScore'][(testData_df['ETA_ontime'] == 0) & (testData_df['StopSequence'] == 1) & (
            testData_df['ETA'] - testData_df['Appt'] <= datetime.timedelta(0, 90 * 60))] = 80
    testData_df['CheckScore'][(testData_df['ETA_ontime'] == 0) & (testData_df['StopSequence'] == 1) & (
            testData_df['ETA'] - testData_df['Appt'] > datetime.timedelta(0, 90 * 60))] = 20
    testData_df['CheckScore'][(testData_df['ETA_ontime'] == 0) & (testData_df['StopSequence'] > 1)] = 20
    testData_df['CheckScore'][(testData_df['arrived'] > 0) & (
            testData_df['Arrival'] - testData_df['Appt'] > datetime.timedelta(0, 60 * 60))] = 100
    testData_df['CheckScore'][(testData_df['arrived'] > 0) & (
            testData_df['Arrival'] - testData_df['Appt'] <= datetime.timedelta(0, 60 * 60))] = 0

    results = testData_df[
        ["LoadID", "LoadDate", "Customer", "ProgressType", "StopSequence", "ontime_prob", "ontime_pred",
         "SafeScore", "Reason"]]

    results['RiskScore_2'] = np.ceil(results['SafeScore'])
    results.to_csv("OnTime_Predict" + now.strftime("%Y%m%d%H%M") + ".csv", index=False)
    testData_df.to_csv("testdata" + now.strftime("%Y%m%d%H%M") + ".csv", index=False)

    generate_results(testData_df)

    return (testData_df)

