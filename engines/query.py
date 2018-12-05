import pandas as pd
import pyodbc

class QueryEngine:

    @property
    def researchScienceConnectionString(self):
        return self.__researchScienceConnectionString

    @property
    def bazookaAnalyticsConnString(self):
        return self.__bazookaAnalyticsConnString

    @property
    def bazookaReplConnString(self):
        return self.__bazookaReplConnString 

    def __init__(self, researchScienceConnectionString, bazookaAnalyticsConnString, bazookaReplConnString):
        self.__researchScienceConnectionString = researchScienceConnectionString
        self.__bazookaAnalyticsConnString = bazookaAnalyticsConnString
        self.__bazookaReplConnString = bazookaReplConnString

    def get_carrier_histload (self, CarrierID):
        cn = pyodbc.connect(self.__researchScienceConnectionString)
        sql = """
                SET NOCOUNT ON
                DECLARE @CarrierID as int =?   
                DECLARE @date1 as date = dateadd(day,-97,getdate())
                DECLARE @date2 as date = dateadd(day,-07,getdate())
                
                SELECT * 
                FROM [ResearchScience].[dbo].[Recommendation_HistLoads]
                WHERE CarrierID= @CarrierID  
                AND loaddate BETWEEN @date1 and @date2
            """

        histload = pd.read_sql(sql = sql, con = cn, params=(CarrierID,))
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

    def get_truckinsurance_Zihan(self, carrierID): #just for Zihan test, when Zihan do not have bazookastaging access
        cn = pyodbc.connect('DRIVER={SQL Server};SERVER=ANALYTICSPROD;DATABASE=Bazooka;trusted_connection=true')
        query = """
               select 
                case when cargolimit= 0 then 500000 else cargolimit end 'cargolimit'
        		 from
                bazooka.dbo.Carrier Car 
                where Car.ID=?
                """
        truck = pd.read_sql(query, cn, params=[carrierID])

        return truck.cargolimit.tolist()[0]



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


    def get_newload_oldversion(self, startDate,endDate):
        cn = pyodbc.connect(self.__bazookaReplConnString)
        sql = "{call Research.spLoad_GetNonUPSActiveLoadsForResearchMatching(?,?)}"
        df = pd.read_sql(sql = sql, con = cn, params=(startDate,endDate,))
        return df

    def get_newload(self, carrierlat,carrierlon,cargolimit):
        cn = pyodbc.connect(self.__researchScienceConnectionString)  # this dataset is set to be updated every one hour.
        if carrierlat is not None and carrierlon is not None:
            sql="""declare @carrierlat as float =?
            declare @carrierlon as float =?
            declare @cargolimit as float =?
            select * from 
            [ResearchScience].[dbo].[Recommendation_Newloads]
           where 
            statetype=1 
            and originLat between @carrierlat-10 and @carrierlat+10 
            and originLon between  @carrierlon-5 and  @carrierlon+5
            and value <= @cargolimit"""
            newload=pd.read_sql(sql = sql, con = cn, params=(carrierlat,carrierlon,cargolimit,))
        else:
            query = """
                    declare @cargolimit as float =?
                          select * from 
                          [ResearchScience].[dbo].[Recommendation_Newloads]
                         where 
                          statetype=1 and value <= @cargolimit
                          """
            newload = pd.read_sql(query, cn, params=(cargolimit,))
        return newload