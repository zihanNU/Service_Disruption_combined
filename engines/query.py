import pandas as pd
import pyodbc

class QueryEngine:

    @property
    def researchScienceConnectionString(self):
        return self.__researchScienceConnectionString

    def __init__(self, researchScienceConnectionString):
        self.__researchScienceConnectionString = researchScienceConnectionString
        
    def Get_Carrier_histLoad (self, CarrierID,date1,date2):
        cn = pyodbc.connect(self.__researchScienceConnectionString)
        sql = """
                SET NOCOUNT ON
                DECLARE @CarrierID as int =?   
                DECLARE @date1 as date = ?
                DECLARE @date2 as date =?
                
                SELECT * 
                FROM [ResearchScience].[dbo].[Recommendation_HistLoads]
                WHERE CarrierID= @CarrierID  
                AND loaddate BETWEEN @date1 and @date2
            """

        histload = pd.read_sql(sql = sql, con = cn, params=(CarrierID,date1,date2,))
        if (len(histload)==0):
            return {'flag':0,'histload':0}

        histload['origin_max']=max(histload.origin_count)
        histload['dest_max']=max(histload.dest_count)
        return {'flag':1,'histload':histload}


    def Get_corridorinfo(self):
        cn = pyodbc.connect(self.__researchScienceConnectionString) 
        sql="""select * from [ResearchScience].[dbo].[Recommendation_CorridorMargin]"""
        corridor_info=pd.read_sql(sql = sql, con = cn)
        return corridor_info