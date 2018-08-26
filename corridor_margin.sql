declare @CarrierDate1 as date = dateadd(day,-37,getdate())
	declare @CarrierDate2 as date = dateadd(day,-7,getdate())
 


	If(OBJECT_ID('tempdb..#histload') Is Not Null)
	Begin
	Drop Table #histload
	End
	Create Table #histload (LoadID int, miles float, Totalrate float, OriginCluster varchar (50), DestinationCluster varchar (50), Corridor varchar (100))
	Insert into #histload


	select   L.id 'LoadID',  L.miles,L.totalrate,
	--L.margin,  
	--L.totalrate,
	--L.margin/L.totalrate*100 'margin_perc',
	 RCO.ClusterNAME 'OriginCluster'
	,RCD.ClusterName 'DestinationCluster'
	,RCO.ClusterNAME+'-'+RCD.ClusterName  'Corridor'
	FROM Bazooka.dbo.[Load] L
	--INNER JOIN Bazooka.dbo.LoadCarrier LCAR ON LCAR.LoadID = L.ID and LCAR.Main = 1 and LCAR.IsBounced = 0
	--INNER JOIN Bazooka.dbo.LoadCustomer LCUS ON LCUS.LoadID = L.ID AND LCUS.Main = 1 
	--INNER JOIN bazooka.dbo.LoadRate LR ON LR.LoadID = L.ID AND LR.EntityType = 13 AND LR.EntityID = LCAR.ID and LR.OriginalQuoteRateLineItemID=0
	--inner join bazooka.dbo.loadstop LS on LS.id=L.OriginLoadStopID
	LEFT JOIN Analytics.CTM.RateClusters RCO ON RCO.Location = L.OriginCityName + ', ' + L.OriginStateCode  
	LEFT JOIN Analytics.CTM.RateClusters RCD ON RCD.Location = L.DestinationCityName + ', ' + L.DestinationStateCode  
	WHERE L.StateType = 1 and L.progresstype>=7
	and  L.LoadDate between @CarrierDate1 and @CarrierDate2  and L.Miles>30 and L.division between 1 and 2
	AND L.Mode = 1   
	AND L.TotalRate >= 150 AND L.TotalCost >= 150 
	AND L.ShipmentType not in (3,4,6,7)
	AND (CASE WHEN L.EquipmentType LIKE '%V%' THEN 'V' ELSE L.EquipmentType END) IN ('V', 'R')
	AND L.TotalRate >= 150 AND L.TotalCost >= 150
	AND  L.[OriginStateCode] in (select [Code]  FROM [Bazooka].[dbo].[State] where [ID]<=51) 
	AND  L.[DestinationStateCode] in (select [Code]  FROM [Bazooka].[dbo].[State] where [ID]<=51) 



	
	If(OBJECT_ID('tempdb..#Corridor_margin') Is Not Null)
	Begin
	Drop Table #Corridor_margin
	End
	Create Table #Corridor_margin (LoadID int,  margin money, Custeromer_Rate money,Carrier_Rate money, rpm float, margin_perc float, OriginCluster varchar (50), DestinationCluster varchar (50), Corridor varchar (100))
	Insert into #Corridor_margin

	select #histload.LoadID 'LoadID',  
	--L.margin,  
	Totalrate-LRCAR.Cost 'gross_margin',
	Totalrate 'Custeromer_Rate', 
	LRCAR.Cost 'Carrier_Rate',
	LRCAR.Cost/(#histload.miles+case when LCAR.ActualDistance<=0.0 then 0.0 else LCAR.ActualDistance end) 'rpm',
	--L.totalrate,
	case when LRCUS.Cost>0 then (Totalrate-LRCAR.Cost)/LRCUS.Cost*100 end 'margin_perc',
	--L.margin/L.totalrate*100 'margin_perc',
	OriginCluster
	,DestinationCluster
	,Corridor
	FROM #histload
	INNER JOIN Bazooka.dbo.LoadCarrier LCAR ON LCAR.LoadID = #histload.loadID and LCAR.Main = 1 and LCAR.IsBounced = 0
	INNER JOIN Bazooka.dbo.LoadCustomer LCUS ON LCUS.LoadID = #histload.loadID AND LCUS.Main = 1 
	INNER JOIN bazooka.dbo.LoadRate LR ON LR.LoadID = LCAR.LoadID AND LR.EntityType = 13 AND LR.EntityID = LCAR.ID and LR.OriginalQuoteRateLineItemID=0
	INNER JOIN Bazooka.dbo.Carrier CAR ON CAR.ID = LCAR.CarrierID
	INNER JOIN Bazooka.dbo.Customer CUS ON LCUS.CustomerID = CUS.ID
	LEFT JOIN Bazooka.dbo.Customer PCUS ON CUS.ParentCustomerID = PCUS.ID
	inner join (select  loadid, SUM(amount) 'Cost' from Bazooka.dbo.LoadRateDetail 
					where EntityType = 12 and EDIDataElementCode IN  ('405','FR',  'PM' ,'MN','SCL','OT','EXP') --and CreateDate > '2018-01-01' 
					Group by loadid) LRCUS on LRCUS.loadid = #histload.LoadID
	inner join (select entityid, SUM(amount) 'Cost' from Bazooka.dbo.LoadRateDetail 
					where EntityType = 13 and EDIDataElementCode IN  ('405','FR',  'PM' ,'MN','SCL') --and CreateDate > '2018-01-01' 
					Group by entityid) LRCAR on LRCAR.entityid = LCAR.id
	WHERE 
	  CAR.ContractVersion NOT IN ('TMS FILE', 'UPSDS CTM', 'UPSCD CTM') --Exclude Managed Loads
	AND COALESCE(PCUS.CODE,CUS.CODE) NOT IN ('UPSAMZGA','UPSRAILPEA')
	and car.Name not like 'UPS%' and CUS.Name not like 'UPS%'  
	order by margin_perc desc
 

	select avg(margin_perc) 'corrdor_margin_perc'
	, min (margin_perc)  'min_margin_perc',  max(margin_perc)  'max_margin_perc',avg(rpm) 'rpm' 
	,  count(loadid) 'Count_Corridor', OriginCluster,corridor
	from  #Corridor_margin
	where margin_perc between -65 and 65
	group by OriginCluster,Corridor
	order by Count_Corridor desc