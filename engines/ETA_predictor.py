testData['CheckScore'] = -1
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
