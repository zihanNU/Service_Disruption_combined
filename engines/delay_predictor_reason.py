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
    dummies = pd.get_dummies(data['appttype'])
    data[['appt_appt', 'appt_notice', 'appt_open']] = dummies
    # data['appt_notice']=dummies['Notice'].tolist()
    # data['appt_open']=dummies['Open'].tolist()
    dummies = pd.get_dummies(data['loadtype'])
    data[['loadtype_s', 'loadtype_c']] = dummies
    # data[] = dummies['C'].tolist()
    return data


def reason(coef, outputdata, inputdata, flag):
    if flag == 1:
        names = ["prestop_ontime", "prestop_duration", "distance", "facility_rate", "customer_rate"]
        reasons = {"prestop_ontime": "PreStop_Delay", "prestop_duration": "PreStop_Duration", "distance": "Distance",
                   "facility_rate": "Facility", "customer_rate": "Customer"}
    if flag == 2:
        names = ["prestop_ontime", "prestop_duration", "distance", "facility_rate", "customer_rate", "carrier_rate",
                 "latebooking"]
        reasons = {"prestop_ontime": "PreStop_Delay", "prestop_duration": "PreStop_Duration", "distance": "Distance",
                   "facility_rate": "Facility", "customer_rate": "Customer", "carrier_rate": "Carrier",
                   "latebooking": "Late_Book"}
    if flag == 3:
        names = ["prestop_ontime", "prestop_duration", "distance", "facility_rate", "customer_rate", "carrier_rate"]
        reasons = {"prestop_ontime": "PreStop_Delay", "prestop_duration": "PreStop_Duration", "distance": "Distance",
                   "facility_rate": "Facility", "customer_rate": "Customer", "carrier_rate": "Carrier"}

    coef = coef[0][3:]  # there is dimensional problem, coef is a 2d matrix, we need to be careful with that.
    # coef=coef.fillna(0, inplace=True)
    # for i in range (0,len(names)):
    # refervalue.append(pd.DataFrame.mean(inputdata[names[i]]))
    refervalue = (pd.DataFrame.mean(inputdata[names]))
    # print ('t',outputdata.loc[36])
    for i in range(outputdata.shape[0]):
        delta = np.multiply((outputdata[names].iloc[i] - refervalue), coef)
        # output['Reason'].loc[i] = np.where(output['Reason'].loc[i] == "" or output['Reason'].loc[i].isnull(),reasons[np.argmin(delta)],output['Reason'].loc[i])
        # we do not use np.where as it returns an array. we could use tolist() to change the one element array into a number, but it may be resource consuming
        if pd.isna(outputdata['reason'].iloc[i]):
            outputdata['reason'].iloc[i] = reasons[np.argmin(delta)]
    return (outputdata)

def gml_stage(inputdata,outputdata,flag):
    # for stage 1, no carrier is booked
    # instead of using C(Code) but dummies, will make sure there is no dimensional change, i.e. maybe some dataset do not have all the levels of categories, if we use C(), it will be one dimension less than the trainning set
    if flag==1:
        X_test = dmatrix('appt_appt + appt_notice+ prestop_ontime + prestop_duration + distance + facility_rate + customer_rate', outputdata,
                         return_type='dataframe')
        y, X = dmatrices('ontime ~ appt_appt + appt_notice+ prestop_ontime + prestop_duration + distance + facility_rate + customer_rate', inputdata,
                         return_type='dataframe')
    elif flag==2:
        y, X = dmatrices(
            'ontime ~ appt_appt + appt_notice+ prestop_ontime + prestop_duration + distance + facility_rate + customer_rate + carrier_rate + latebooking',
            inputdata, return_type='dataframe')
        X_test = dmatrix(
            'appt_appt + appt_notice+ prestop_ontime + prestop_duration + distance + facility_rate + customer_rate + carrier_rate + latebooking',
            outputdata, return_type='dataframe')
    else:
        y, X = dmatrices(
            'ontime ~ appt_appt + appt_notice+ prestop_ontime + prestop_duration + distance + facility_rate + customer_rate + carrier_rate', inputdata,
            return_type='dataframe')
        X_test = dmatrix('appt_appt + appt_notice+ prestop_ontime + prestop_duration + distance + facility_rate + customer_rate + carrier_rate',
                         outputdata, return_type='dataframe')
    model = LogisticRegression(fit_intercept=False)
    model.fit(X, np.ravel(y))
    rate_result = model.predict(X_test)
    rate = model.predict_proba(X_test)[:,1]
    return rate,rate_result,model.coef_


def get_results(traindata,testdata,flag):
    for Type in set(traindata['pdtype'].tolist()):
        if len(testdata[testdata['pdtype']==Type].axes[0])> 0:
            rate, delay_result,coef = gml_stage(traindata[traindata['pdtype'] == Type ], testdata[testdata['pdtype'] == Type],flag)
            testdata['ontime_prob_logit'][testdata['pdtype'] == Type] = rate
            testdata['ontime_pred_logit'][testdata['pdtype'] == Type] = delay_result
            if len(testdata[(testdata['pdtype']==Type) & ( min(testdata['ontime_prob_logit'],testdata['ontime_pred'])<0.95)& (testdata['ontime_actual'] == -1)].axes[0])>0:
                reasons=reason(coef, testdata[(testdata['pdtype'] == Type) & ( min(testdata['ontime_prob_logit'],testdata['ontime_pred'])<0.95) & (
                        testdata['ontime_actual'] == -1)], traindata[traindata['pdtype'] == Type], flag)
                testdata[(testdata['pdtype']==Type)& (min(testdata['ontime_prob_logit'],testdata['ontime_pred'])<0.95) &(testdata['ontime_actual'] == -1)] = reasons
    return (testdata)



def delay_predictor(trainData, testData):
    """main recommendation function
    Args:
    carrier_load: Pandas DF with historical loads for the carrier.
    trucks_df: Pandas DF with truck(s) (orig,dest,ready date, etc.) sent to search()
    """
    trainData = get_dummies(trainData)
    testData['ontime_prob_logit']=-1
    testData['ontime_pred_logit']=-1
    testData['facility_rate'].fillna((testData['facility_rate'].mean()), inplace=True)
    testData['customer_rate'].fillna((testData['customer_rate'].mean()), inplace=True)
    testData['carrier_rate'].fillna((testData['carrier_rate'].mean()), inplace=True)
    testData['prestop_duration'].fillna((testData['prestop_duration'].mean()), inplace=True)
    testData['distance'].fillna(1, inplace=True)
    testData['reason']=np.nan
    testData_1 = testData[testData['progresstype'] == 1]
    if len(testData_1.axes[0]) > 0:
        testData_1[testData_1['stopsequence'] == 1] = get_results(trainData[trainData['stopsequence'] == 1],
                                                                  testData_1[testData_1['stopsequence'] == 1], 1)
        max_stop = max(testData_1.numstops) + 1
        nrow_testData_1 = len(testData_1)
        for k in range(2, max_stop):
            for i in range(nrow_testData_1):
                if testData_1['stopsequence'].iloc[i] == k:
                    if testData_1['ontime_actual'].iloc[i - 1] == -1:
                        testData_1['prestop_ontime'].iloc[i] = testData_1['ontime_prob_logit'].iloc[i - 1]
            testData_1[testData_1['stopsequence'] == k] = get_results(trainData[trainData['stopsequence'] > 1],
                                                                      testData_1[testData_1['stopsequence'] == k], 1)
    # Stage 2
    testData_2 = testData[testData['progresstype'] > 1]
    testData_2[testData_2['stopsequence'] == 1] = get_results(trainData[trainData['stopsequence'] == 1],
                                                              testData_2[testData_2['stopsequence'] == 1], 2)
    max_stop = max(testData_2.numstops) + 1
    nrow_testData_2 = len(testData_2)
    for k in range(2, max_stop):
        # for i in testData_2.index:
        for i in range(nrow_testData_2):
            if testData_2['stopsequence'].iloc[i] == k:
                if testData_2['ontime_actual'].iloc[i - 1] == -1:
                    testData_2['prestop_ontime'].iloc[i] = testData_2['ontime_prob_logit'].iloc[i - 1]
        testData_2[testData_2['stopsequence'] == k] = get_results(trainData[trainData['stopsequence'] > 1],
                                                                  testData_2[testData_2['stopsequence'] == k], 3)
    testData_df = pd.concat([testData_1, testData_2])
    return (testData_df)

