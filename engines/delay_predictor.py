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
    #print('Modeling  %.5f' % model_1.best_score)
    #xgb.plot_importance(model_1, max_num_features=10, height=0.7)

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

        testData['safescore'].iloc[i]=(L_score+(testData['ontime_prob'].iloc[i]-lowerbound) * (H_score-L_score) / (upperbound-lowerbound))
    return (testData)

def scoring(testdata):
    threshold = pd.DataFrame.mean(testdata['ontime_prob'])
    testdata = ontime_score (testdata, threshold)
    testdata['ontime_pred'] = (testdata['ontime_prob'] > threshold * 0.98)
    return (testdata)


def roll_prediction(testData, model, feature):
    if len(testData.axes[0]) > 0:
        # note: test['duration'] = model.predict()
        dtest = xgb.DMatrix(testData[testData['stopsequence'] == 1][feature].values)
        testData.ontime_prob[testData['stopsequence'] == 1] = model.predict(dtest).tolist()
        max_stop = max(testData.numstops) + 1
        nrow_testData_1 = len(testData)
        for k in range(2, max_stop):
            for i in range(nrow_testData_1):
                if testData['stopsequence'].iloc[i] == k:
                    if testData['ontime_actual'].iloc[i - 1] == -1:
                        testData['prestop_ontime'].iloc[i] = testData['ontime_actual'].iloc[i - 1]
            print(k)
            dtest = xgb.DMatrix(testData[testData['stopsequence'] == k][feature].values)
            testData.ontime_prob[testData['stopsequence'] == k] = model.predict(dtest).tolist()
            # testData_1[testData_1['StopSequence'] == k] = Get_Results(trainData[trainData['StopSequence'] > 1],

    testData = scoring(testData)
    return testData


def delay_predictor(model,feature, testData):
    """main recommendation function
    Args:
    carrier_load: Pandas DF with historical loads for the carrier.
    trucks_df: Pandas DF with truck(s) (orig,dest,ready date, etc.) sent to search()
    """
    testData = get_dummies(testData)
    testData['safescore']=-1
    testData['ontime_prob'] = -1
    testData["ontime_pred"] = -1
    testData_1 = testData[testData['progresstype'] == 1]
    testData_2 = testData[testData['progresstype'] > 1]
    testData_1 =roll_prediction(testData_1,model[1],feature[1])
    testData_2 = roll_prediction(testData_2, model[0], feature[0])
    testData_df = pd.concat([testData_1, testData_2])

    testData_df['riskscore'] = 100 - testData_df['safescore'] * 20
    return (testData_df)

