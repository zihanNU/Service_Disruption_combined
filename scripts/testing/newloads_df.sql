select top 10 'newloads_df.loc[x] = {"loadID":' + CONVERT(VARCHAR,loadID) + ',' + 
    '"loaddate":"' + FORMAT(loaddate, 'yyyy-MM-dd') + '",' + 
    '"StateType":' + CONVERT(VARCHAR,StateType) + ',' + 
    '"value":' + CONVERT(VARCHAR,[value]) + ',' + 
    '"customer_rate":' + CONVERT(VARCHAR,customer_rate) + ',' +
    '"equipment":"' + equipment + '",' +
    '"equipmentlength":' + CONVERT(VARCHAR,equipmentlength) + ',' +
    '"miles":' + CONVERT(VARCHAR,miles) + ',' +
    '"pu_appt":"' + FORMAT(pu_appt, 'yyyy-MM-dd') + '",' +
    '"origin":"' + origin + '",' +
    '"destination":"' + destination + '",' +
    '"originLon":' + CONVERT(VARCHAR,originLon) + ',' +
    '"originLat":' + CONVERT(VARCHAR,originLat) + ',' +
    '"destinationLon":' + CONVERT(VARCHAR,destinationLon) + ',' +
    '"destinationLat":' + CONVERT(VARCHAR,destinationLat) + ',' +
    '"originCluster":"' + originCluster + '",' +
    '"destinationCluster":"' + destinationCluster + '",' + 
    '"corridor":"' + corridor + '",' + 
    '"industryID":' + CONVERT(VARCHAR,industryID) + ',' + 
    '"industry":"' + industry + '",' + 
    '"originDH": 250, ' +
    '"destDH": 300, ' +
    '"puGap": 300, ' +
    '"totalDH": 550 ' +
    '}'
from Recommendation_Newloads
where statetype = 1
order by NEWID()

/*
select top 2 * from   
[ResearchScience].[dbo].[Recommendation_Newloads]
where 
statetype=1 
*/