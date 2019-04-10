import pyodbc
import pandas as pd
import numpy as np
import math
import datetime
import os
from patsy import dmatrices,dmatrix
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import xgboost as xgb

now = datetime.datetime.now()
now_tz=datetime.datetime.now().astimezone().tzinfo
now = pd.Timestamp(now).tz_localize(now_tz)



def get_dummies(data):
    dummies=pd.get_dummies(data['appttype'])
    data[['appt_appt','appt_notice','appt_open']]=dummies
    #data['appt_notice']=dummies['Notice'].tolist()
    #data['appt_open']=dummies['Open'].tolist()
    dummies=pd.get_dummies(data['loadtype'])
    data[['loadtype_s','loadtype_c']]= dummies
    #data[] = dummies['C'].tolist()
    return data



def trainmodel(trainData):
    feature_names_1=['stopsequence','numstops','carrier_rate','facility_rate','customer_rate','prestop_ontime',
                   'prestop_duration','distance','latebooking','latedispatch','holiday_season','day_of_week',
                   'loadtype_c','appt_appt','appt_notice']

    trainData = get_dummies(trainData)
    y = trainData['ontime']
    # split the training set into 80, 20 with training set and cross validation set.
    Xtr, Xv, ytr, yv = train_test_split(trainData[feature_names_1].values, y, test_size=0.2, random_state=0)
    dtrain = xgb.DMatrix(Xtr, label=ytr)
    dvalid = xgb.DMatrix(Xv, label=yv)
    # dtest = xgb.DMatrix(test[feature_names].values)
    watchlist = [(dtrain, 'train'), (dvalid, 'valid')]
    xgb_pars = {'base_score': np.average(y),'min_child_weight': 30, 'eta': 0.3, 'colsample_bytree': 0.3, 'max_depth': 5,
                'subsample': 0.7, 'lambda': 1., 'nthread': 2, 'booster': 'gbtree', 'silent': 1,
                'eval_metric': 'error', 'objective': 'binary:logistic'}   # may need to change eval-metric
    model_1 = xgb.train(xgb_pars, dtrain, 30, watchlist, early_stopping_rounds=50,
                      maximize=False, verbose_eval=1)
    print('Modeling  %.5f' % model_1.best_score)
    xgb.plot_importance(model_1, max_num_features=10, height=0.7)

    feature_names_2=['stopsequence','numstops','facility_rate','customer_rate','prestop_ontime',
                   'prestop_duration','distance','latebooking','latedispatch','holiday_season','day_of_week',
                   'loadtype_c','appt_appt','appt_notice']
    Xtr, Xv, ytr, yv = train_test_split(trainData[feature_names_2].values, y, test_size=0.2, random_state=0)
    dtrain = xgb.DMatrix(Xtr, label=ytr)
    dvalid = xgb.DMatrix(Xv, label=yv)
    watchlist = [(dtrain, 'train'), (dvalid, 'valid')]
    model_2 = xgb.train(xgb_pars, dtrain, 30, watchlist, early_stopping_rounds=50,
                        maximize=False, verbose_eval=1)
    return [model_1,model_2],[feature_names_1,feature_names_2]


def scoring(testdata):
    for Type in set(testdata['PDType'].tolist()):
        if len(testdata[testdata['PDType']==Type].axes[0])> 0:
            threshold = pd.DataFrame.mean(testdata[testdata.PDType == Type]['ontime'])
            testdata[testdata['PDType'] == Type] = ontime_score (testdata[testdata['PDType'] == Type], threshold)
            testdata['ontime_pred'][testdata['PDType'] == Type] = (testdata['ontime_prob'][testdata['PDType'] == Type] > threshold * 0.98)
    return (testdata)

def roll_prediction(testData,model,feature):
    if len(testData.axes[0]) > 0:
        #note: test['duration'] = model.predict()
        dtest= xgb.DMatrix(testData[testData['StopSequence'] == 1][feature ].values)
        testData['ontime_prob'][testData['StopSequence'] == 1] =model.predict(dtest )
        max_stop = max(testData.NumStops) + 1
        nrow_testData_1 = len(testData)
        for k in range(2, max_stop):
            for i in range(nrow_testData_1):
                if testData['StopSequence'].iloc[i] == k:
                    if testData['arrived'].iloc[i - 1] == 0:
                        testData['preStop_OnTime'].iloc[i] = testData['ontime_prob'].iloc[i - 1]
            dtest = xgb.DMatrix(testData[testData['StopSequence'] == k][feature[1]].values)
            testData['ontime_prob'][testData['StopSequence'] == k] = model[1].predict(dtest)
            # testData_1[testData_1['StopSequence'] == k] = Get_Results(trainData[trainData['StopSequence'] > 1],
    testData=scoring(testData)
    return testData

def delay_predictor(model,feature, testData):

    """main recommendation function

    Args:
    carrier_load: Pandas DF with historical loads for the carrier.
    trucks_df: Pandas DF with truck(s) (orig,dest,ready date, etc.) sent to search()
    """
    testData = get_dummies(testData)

    testData['ontime_prob'] = -1
    testData['ontime_pred'] = -1
    testData['SafeScore'] = -1
    testData['RiskScore'] = -1
    testData['CheckScore'] = -1
    testData_1 = testData[testData['ProgressType'] == 1]
    testData_2 = testData[testData['ProgressType'] > 1]
    testData_1 =roll_prediction(testData_1,model[1],feature[1])
    testData_2 = roll_prediction(testData_2, model[0], feature[0])
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

