set nocount on
    declare @CarrierID as int =?

    declare @CarrierDate1 as date = ?
    declare @CarrierDate2 as date = ?

    --declare @HistDate1 as date = '2017-06-01'
    --declare @HistDate2 as date = '2018-06-01'


    If(OBJECT_ID('tempdb..#Bounce_Reason') Is Not Null)
    Begin
    Drop Table #Bounce_Reason
    End
    Create Table #Bounce_Reason (FaultType int, ReasonType int, Reason varchar(30))
    Insert into #Bounce_Reason Values(0,0,	'Carrier')
    Insert into #Bounce_Reason Values(1,1,	'Carrier')
    Insert into #Bounce_Reason Values(1,2,	'Carrier')
    Insert into #Bounce_Reason Values(1,3,	'Carrier')
    Insert into #Bounce_Reason Values(1,4,	'Carrier')
    Insert into #Bounce_Reason Values(1,6,	'Carrier')
    Insert into #Bounce_Reason Values(1,12,	'Carrier') 
    Insert into #Bounce_Reason Values(1,13,	'Carrier')
    Insert into #Bounce_Reason Values(1,7,	'Carrier_Reps')
    Insert into #Bounce_Reason Values(1,8,	'Cust_Reps')
    Insert into #Bounce_Reason Values(2,1,	'Carrier')
    Insert into #Bounce_Reason Values(2,2,	'Carrier')
    Insert into #Bounce_Reason Values(2,3,	'Carrier')
    Insert into #Bounce_Reason Values(2,4,	'Carrier')
    Insert into #Bounce_Reason Values(2,5,	'Customer')
    Insert into #Bounce_Reason Values(2,7,	'Carrier_Reps')
    Insert into #Bounce_Reason Values(2,8,	'Cust_Reps')
    Insert into #Bounce_Reason Values(2,9,	'Carrier')
    Insert into #Bounce_Reason Values(2,10,	'Facility')
    Insert into #Bounce_Reason Values(2,13,	'Carrier_Reps')
    Insert into #Bounce_Reason Values(3,10,	'Facility')
    Insert into #Bounce_Reason Values(3,11,	'Facility')
    Insert into #Bounce_Reason Values(3,12,	'Customer')
    Insert into #Bounce_Reason Values(3,13,	'Customer')

    If(OBJECT_ID('tempdb..#Service') Is Not Null)
    Begin
    Drop Table #Service
    End
    Create Table #Service ( LoadID int, CarrierID int, PUScore int, DelScore int)
    Insert into #Service

    select LoadID,
    Carrierid, 
    case when datediff(minute,PU_Appt,PU_Arrive)<=60 then 25
    when datediff(minute,PU_Appt,PU_Arrive)<= 120 then 20
    when datediff(day,PU_Appt,PU_Arrive)=0 then 10
    else 5 end 'PU',
    case when datediff(minute,DO_Appt,DO_Arrive)<=60 then 25
    when datediff(minute,DO_Appt,DO_Arrive)<= 120 then 20
    when datediff(day,DO_Appt,DO_Arrive)=0 then 10
    else 5 end 'Del'
    from (
    select  L.id 'LoadID', 
    LCAR.CarrierID, 
    (case when LSP.[ScheduleCloseTime] = '1753-01-01' then 
    convert(datetime, CONVERT(date, LSP.LoadByDate)) + convert(datetime, CONVERT(time, LSP.CloseTime)) 
    else LSP.[ScheduleCloseTime] end) 'PU_Appt',
    LSP.[ArriveDateTime] 'PU_Arrive'
    , case when LSD.[ScheduleCloseTime] = '1753-01-01' then 
    convert(datetime, CONVERT(date, LSD.DeliverByDate)) + convert(datetime, CONVERT(time, LSD.CloseTime)) 
    else LSD.[ScheduleCloseTime] end 'DO_Appt',
    LSD.[ArriveDateTime] 'DO_Arrive' 
    FROM Bazooka.dbo.[Load] L
    INNER JOIN Bazooka.dbo.LoadCarrier LCAR ON LCAR.LoadID = L.ID and LCAR.Main = 1 and LCAR.IsBounced = 0
    inner join Bazooka.dbo.loadstop LSP on  LSP.ID=L.OriginLoadStopID
    inner join Bazooka.dbo.loadstop LSD on  LSD.ID=L.DestinationLoadStopID
    WHERE L.Mode = 1 AND    L.LoadDate between @CarrierDate1 and @CarrierDate2 and L.Miles>0 and LCAR.CarrierID= @CarrierID  
    ) X

    If(OBJECT_ID('tempdb..#Bounce') Is Not Null)
    Begin
    Drop Table #Bounce
    End
    Create Table #Bounce ( LoadID int, CarrierID int,  Offer int, Accept int, Bounce int, OriginDH decimal(8,2), EmptyTime datetime)
    Insert into #Bounce

    select
    L.ID, LCAR.CarrierID, 1 'Offer',1 'Accepted Offers', 
    sum (case when BR.Reason like 'Carrier' then 1 else 0 end) 'Bounce',
    min(case when LCAR.ActualDistance<1 then 1 else LCAR.ActualDistance end)   'OriginDH',
    case when convert (date, max(LCAR.ActualDateTime))='1753-01-01' then getdate() else  max(LCAR.ActualDateTime) end 'EmptyTime'
    FROM Bazooka.dbo.[Load] L
    INNER JOIN Bazooka.dbo.LoadCarrier LCAR ON LCAR.LoadID = L.ID  
    left join Bazooka.dbo.LoadChangeLog Log_B on  Log_B.ChangeType=4 and Log_B.EntityID=LCAR.ID and LCAR.IsBounced=1
    left join #Bounce_Reason BR on BR.FaultType=Log_B.FaultType and BR.ReasonType=Log_B.ReasonType 
    WHERE L.Mode = 1 AND    L.LoadDate between @CarrierDate1 and @CarrierDate2 and L.Miles>0 and LCAR.CarrierID=@CarrierID   and L.ProgressType>=7    
    group by L.id, LCAR.CarrierID
    order by Bounce



    If(OBJECT_ID('tempdb..#Offer') Is Not Null)
    Begin
    Drop Table #Offer
    End
    Create Table #Offer( LoadID int, CarrierID int, Offer int, Cost money, Ask money,  BadOffer int,OriginDH int, AvailableTime datetime, Rnk int)
    Insert into #Offer
    select 
    O.LoadID, CarrierID, 1 'Offer',L.totalrate, --LRD.Cost,
    Ask, 
    case when  Ask >L.totalrate*0.9 then 1 else 0 end  'Badoffer',
    case when O.MilesToOrigin<1 then 1 else O.MilesToOrigin end 'OriginDH',
    convert(datetime, CONVERT(date,O.CanLoadDate))+convert(datetime, CONVERT(time,O.CanLoadTime)) 'AvailableTime',
    RANK() over (partition by O.LoadID, O.CarrierID order by O.CreateDate desc) 'rnk'
    from bazooka.dbo.Offer O
    inner join Bazooka.dbo.[Load] L on O.LoadID = L.ID
    inner join Bazooka.dbo.LoadCustomer LCUS on LCUS.LoadID = L.ID and LCUS.Main = 1
    --inner join (select  loadid, SUM(amount) 'Cost' from Bazooka.dbo.LoadRateDetail 
    --				where EntityType = 12 and EDIDataElementCode IN  ('405','FR',  'PM' ,'MN','SCL','OT','EXP') --and CreateDate > '2018-01-01' 
    --				Group by loadid) LRD on LRD.loadid = L.ID
    --inner join #Cost C on C.LoadID=O.LoadID
    where O.Carrierid=@CarrierID   and O.LoadDate between @CarrierDate1 and @CarrierDate2 and  
    Ask>0 and L.totalrate > 150 and  L.Mode = 1  and L.ProgressType>=7  and L.Miles>0

    ---End of Load-Carrier KPI Score


    ---Start of Carrier Features

    If(OBJECT_ID('tempdb..#Carrier_HistLoad') Is Not Null)
    Begin
    Drop Table #Carrier_HistLoad
    End
    Create Table #Carrier_HistLoad (LoadID int,   Origin varchar (50), Destination varchar(50),  OriginCluster varchar (50), DestinationCluster varchar (50), Corridor varchar (100))
    Insert into #Carrier_HistLoad


    select L.id 'LoadID',  
        L.OriginCityName + ', ' + L.OriginStateCode  'Origin'
    ,L.DestinationCityName + ', ' + L.DestinationStateCode  'Destination'
    --,L.TotalValue
    --,case when  l.equipmenttype like '%V%' then 'V' when  l.equipmenttype like 'R' then 'R' else 'other' end Equipment
    ,RCO.ClusterNAME 'OriginCluster'
    ,RCD.ClusterName 'DestinationCluster'
    ,RCO.ClusterNAME+'-'+RCD.ClusterName  'Corridor'
    FROM #Service S
    inner join 	Bazooka.dbo.[Load] L on L.id=S.LoadID
    LEFT JOIN Analytics.CTM.RateClusters RCO ON RCO.Location = L.OriginCityName + ', ' + L.OriginStateCode  
    LEFT JOIN Analytics.CTM.RateClusters RCD ON RCD.Location = L.DestinationCityName + ', ' + L.DestinationStateCode  
    order by Origin,Destination



    If(OBJECT_ID('tempdb..#Carrier_Origin') Is Not Null)
    Begin
    Drop Table #Carrier_Origin
    End
    Create Table #Carrier_Origin (OriginCluster varchar (50), Count_Origin int)
    Insert into #Carrier_Origin
    select distinct OriginCluster,
    count(loadid) 'Count_Origin'
    from #Carrier_HistLoad
    group by OriginCluster
    order by 2 desc


    If(OBJECT_ID('tempdb..#Carrier_Dest') Is Not Null)
    Begin
    Drop Table #Carrier_Dest
    End
    Create Table #Carrier_Dest (DestinationCluster varchar (50), Count_Dest int)
    Insert into #Carrier_Dest
    select distinct DestinationCluster,
    count(loadid) 'Count_Dest'
    from #Carrier_HistLoad
    group by DestinationCluster
    order by 2 desc
    ---End of Carrier Features



    select * from (
    select  COALESCE(B.LoadID,O.LoadID)   'loadID',
    COALESCE(B.CarrierID,O.CarrierID)    'carrierID', L.hot 'hot',
    O.cost 'customer_rate',
    case when  B.Accept=1 then l.totalcost else o.Ask  end 'carrier_cost',
    (O.cost-(case when  B.Accept=1 then l.totalcost else o.Ask  end ) )/O.cost*100 'margin_perc',
    L.miles, (case when  B.Accept=1 then l.totalcost else o.Ask end)/(L.miles+COALESCE(O.OriginDH,B.OriginDH) )  'rpm',
    --COALESCE(S.PUScore,0)          'puScore',
    --COALESCE(S.DelScore,0)            'delScore',
    --Coalesce(O.Offer, B.Offer)*40    'offer',
    --COALESCE(B.Accept,0)*10    'offerAccept' ,
    --COALESCE(B.Bounce,0)*(-20)     'bounce'  ,
    --COALESCE(O.BadOffer,0)*-20     'badOffer',
    COALESCE(S.PUScore,0) +       COALESCE(S.DelScore,0)  +
    Coalesce(O.Offer, B.Offer)*40  +
    COALESCE(B.Accept,0)*10   +
    COALESCE(B.Bounce,0)*(-20)     +
    COALESCE(O.BadOffer,0)*-20     'kpiScore',
    COALESCE(O.OriginDH,B.OriginDH )   'originDH',
    --case when COALESCE(O.OriginDH,B.OriginDH )<=10 then 10
    --when COALESCE(O.OriginDH,B.OriginDH )<=50 then 50
    --when COALESCE(O.OriginDH,B.OriginDH )<=100 then 100
    --else 200 end 'originDH-levels',
    --COALESCE(O.AvailableTime,B.EmptyTime) 'Available',
    --case when LSP.[ScheduleCloseTime] = '1753-01-01' then
    --convert(datetime, CONVERT(date, LSP.LoadByDate)) + convert(datetime, CONVERT(time, LSP.CloseTime))
    --else LSP.[ScheduleCloseTime] end  'PU_Appt',
    datediff(hour,COALESCE(O.AvailableTime,B.EmptyTime),case when LSP.[ScheduleCloseTime] = '1753-01-01' then
    convert(datetime, CONVERT(date, LSP.LoadByDate)) + convert(datetime, CONVERT(time, LSP.CloseTime))
    else LSP.[ScheduleCloseTime] end) 'pu_GAP',
    --datediff(minute,COALESCE(O.AvailableTime,S.EmptyTime),S.PU_Appt) 'PU_GAP',
    --CUS.name 'CustomerName'
    RCO.ClusterNAME 'originCluster'
    ,RCD.ClusterName 'destinationCluster'
    ,RCO.ClusterNAME+'-'+RCD.ClusterName 'corridor'
    , case when  l.equipmenttype like '%V%' then 'V' when  l.equipmenttype like 'R' then 'R' else 'other' end 'equipment'
    --,COALESCE(Cor.Count_Corridor,0)  'corridor_count' 
    ,COALESCE(Ori.Count_Origin,0)  'origin_count' 
    ,COALESCE(Dest.Count_Dest,0)  'dest_count' 
    --,COALESCE(CC.Count_Cus,0)  'cus_Count'
    --,COALESCE(CC.Count_ALL,0)   'cus_All'
    --,case when COALESCE(CC.Count_ALL,0)<3000 then 'Small'
    --when COALESCE(CC.Count_ALL,0)<10000 then 'Small-Med'
    --when COALESCE(CC.Count_ALL,0)< 25000 then   'Med'
    --when COALESCE(CC.Count_ALL,0)<50000 then  'Med-Large'
    --else 'Large' end 'cus_Size'
    ,C.DandBIndustryId  'industryID', 
    D.Code 'industry'
    ,	CityO.Latitude 'originLat',CityO.Longitude 'originLon',
    CityD.Latitude 'destinationLat',CityD.Longitude 'destinationLon'
    --,case when CC.Count_ALL>0 then CC.Count_Cus*1.0/CC.Count_ALL  else 0 end 'Cus_Ratio',
    --,L.Miles,
    -- Case
    --when L.Miles <250 then'Short'
    --when L.Miles between 250 and 500 then 'Medium-Short'
    --when L.Miles between 500 and 1000 then 'Medium'
    --when L.Miles between 1000 and 2000 then 'Medium-Long'
    --when L.Miles >2000 then 'Long' end 'Haul-Length'
    from #Service S
    full join #Bounce B on B.LoadID=S.LoadID and B.CarrierID=S.CarrierID
    full join #Offer O on S.LoadID=O.LoadID and S.CarrierID=O.CarrierID
    inner join bazooka.dbo.LoadCustomer LCUS on LCUS.LoadID = COALESCE(B.LoadID,O.LoadID)
    --inner join bazooka.dbo.Customer CUS on CUS.id=LCUS.CustomerID
    inner join bazooka.dbo.load L on L.id=LCUS.LoadID AND LCUS.Main = 1
    inner join bazooka.dbo.loadstop LSP on LSP.id=L.OriginLoadStopID
    inner join bazooka.dbo.loadstop LSD on LSD.id=L.DestinationLoadStopID
    inner join bazooka.dbo.City CityO on CityO.id=LSP.CityID
    inner join bazooka.dbo.City CityD on CityD.id=LSD.CityID
    LEFT JOIN Analytics.CTM.RateClusters RCO ON RCO.Location = L.OriginCityName + ', ' + L.OriginStateCode
    LEFT JOIN Analytics.CTM.RateClusters RCD ON RCD.Location = L.DestinationCityName + ', ' + L.DestinationStateCode
    --left join #Carrier_Corridor Cor on Cor.Corridor=RCO.ClusterNAME +'-'+RCD.ClusterName  
    left join #Carrier_Origin Ori on Ori.OriginCluster=RCO.ClusterNAME  
    left join #Carrier_Dest Dest on Dest.DestinationCluster=RCD.ClusterNAME 
    --left join #Carrier_Cust CC on CC.CustID = LCUS.CustomerID  
    inner join bazooka.dbo.CustomerRelationshipManagement  C on C.CustomerID=LCUS.CustomerID
    inner join
    bazooka.dbo.DandBIndustry D  on C.DandBIndustryId=D.DandBIndustryId
    where   rnk=1  and L.Miles>0
)X
    where pu_Gap>=0 and margin_perc between -65 and 65
    ----65 and 65 are 1% to 99% of the margin_perc
    order by corridor
    """