import pandas as pd
import pyodbc

class QueryEngine:

    @property
    def researchScienceConnectionString(self):
        return self.__researchScienceConnectionString

    @property
    def bazookaAnalyticsConnString(self):
        return self.__bazookaAnalyticsConnString    

    def __init__(self, researchScienceConnectionString, bazookaAnalyticsConnString):
        self.__researchScienceConnectionString = researchScienceConnectionString
        self.__bazookaAnalyticsConnString = bazookaAnalyticsConnString

    def get_carrier_histload (self, CarrierID,date1,date2):
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


    def get_corridorinfo(self):
        cn = pyodbc.connect(self.__researchScienceConnectionString) 
        sql="""select * from [ResearchScience].[dbo].[Recommendation_CorridorMargin]"""
        corridor_info=pd.read_sql(sql = sql, con = cn)
        return corridor_info


    def get_truckinsurance(self, carrierID):
        cn = pyodbc.connect(self.__bazookaAnalyticsConnString)
        cursor = cn.cursor()
        row = cursor.execute("{call [Research].[spCarrier_GetCargoLimitWithDefault](?)}", (carrierID,)).fetchone()
        return row.CargoLimit     


    def get_trucksearch(self, carrierID):
        """Merged the daily truck table into the model"""

        cn = pyodbc.connect(self.__researchScienceConnectionString)
        sql = """
            select 
                carrierID, originCluster, destinationCluster
                from
                [ResearchScience].[dbo].[Recommendation_Trucks] 
                where carrierID=?
                """
        truck = pd.read_sql(sql=sql, con=cn, params=[carrierID])
        trucks_df=truck.drop_duplicates()
        return trucks_df   