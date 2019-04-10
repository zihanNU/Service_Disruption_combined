import pandas as pd
import pyodbc
import numpy as np
import datetime
now = datetime.datetime.now()
now_tz=datetime.datetime.now().astimezone().tzinfo
now = pd.Timestamp(now).tz_localize(now_tz)
timezones = {'Timezone': [-5, -6, -7, -12, -8, -9, -10],
             'tz': ['America/New_York', 'America/Chicago', 'America/Denver', 'America/Phoenix',
                    'America/Los_Angeles', 'America/Anchorage', 'Pacific/Honolulu']}
timezones_df = pd.DataFrame(data=timezones)
speed_highway = 55
speed_local = 35

class ProcessEngine:

    @property
    def histload(self):
        return self.__histload
    @property
    def dynaicload(self):
        return self.__dynaicload


    def __init__(self,histload,dynaicload):
        self.__histload=histload
        self.__dynaicload=dynaicload

    def Process_histdata(self):
        hist_load_df= self.__histload
        for i in hist_load_df.index:
            # if (abs(pd.Timestamp(hist_load_df['Appt'].iloc[i]) - pd.Timestamp(
            #         hist_load_df['Arrival'].iloc[i])).days >= 1) or hist_load_df.loc[
            #     0].Arrival.strftime('%Y') == '1753':
            #     filteroutid.append(hist_load_df.loc[i]['LoadID'])
            #     continue
            loadstop = hist_load_df.loc[i]
            localtz = loadstop['tz']
            if loadstop['StopSequence'] == 1:
                dispatch = pd.Timestamp(hist_load_df['Dispatch_Time'].iloc[i], tz='UTC').tz_convert(localtz)
                Appt = pd.Timestamp(hist_load_df['Appt'].iloc[i], tz=localtz)
                # Appt= pd.Timestamp(hist_load_df.loc[i]['Appt'],tz=localtz)
                Empty_Time = pd.Timestamp(hist_load_df['Empty_Time'].iloc[i], tz=localtz)
                BookTime = pd.Timestamp(hist_load_df['BookTimeUTC'].iloc[i], tz='UTC').tz_convert(localtz)
                if dispatch - Appt >= datetime.timedelta(0, 0, 0):
                    dispatch = Empty_Time
                hist_load_df['dispatch_Local'].iloc[i] = dispatch
                leadtime = Appt - BookTime
                lead_dispatch = Appt - dispatch

                # hist_load_df['latebooking'].iloc[i] = np.where((leadtime.days * 24 * 60 + leadtime.seconds / 60) < 241, 1, 0).tolist()
                # hist_load_df['latedispatch'].iloc[i] = np.where(
                #     (lead_dispatch.days * 24 * 60 + lead_dispatch.seconds / 60) < 121, 1, 0).tolist()
                hist_load_df['latebooking'].iloc[i] = 1 if leadtime.days * 24 * 60 + leadtime.seconds / 60 < 241 else 0
                hist_load_df['latedispatch'].iloc[
                    i] = 1 if lead_dispatch.days * 24 * 60 + lead_dispatch.seconds / 60 < 121 else 0
                hist_load_df['preStop_OnTime'].iloc[i] = 1 - hist_load_df['latedispatch'].iloc[i]
        hist_load_select = hist_load_df[~hist_load_df['LoadID'].isin(filteroutid)]
        hist_load_select.to_csv("histdata" + now.strftime("%Y%m%d") + '.csv', index=False)
        return hist_load_select

    def HOS_checking(self, prestop, stop, travtime):
        # travtime unit in seconds

        travtime = travtime / 3600  # change unit from secs to hrs
        empty_dist = min(prestop.Empty_Dist, 200)
        # b/c 200 from quantile(histdata$Empty_Dist, 0.98)
        speed = speed_local if empty_dist < 100 else speed_highway

        travtime_empty = empty_dist / speed  # unit in hrs

        prestop_tz = prestop['tz']
        stop_tz = stop.tz

        if prestop['arrived'] == 1:
            prestop_start = pd.Timestamp(prestop['Arrival'], tz=prestop_tz)

        else:
            prestop_start = pd.Timestamp(prestop['Appt'], tz=prestop_tz)

        if (stop['StopSequence'] == 2):
            loadempty = pd.Timestamp(prestop['Empty_Time'], tz=prestop_tz)

            if (prestop_start - loadempty) >= datetime.timedelta(0, 3600 * 10):
                onduty_start = prestop_start
            # travtime_empty<-0
            else:
                onduty_start = loadempty
        else:
            onduty_start = prestop_start

        if prestop['Departure'].strftime("%Y") != '1753':
            prestop_end = pd.Timestamp(prestop['Departure'], tz=prestop_tz)
            onduty_stop = (prestop_end - onduty_start).days * 24 * 60 + (prestop_end - onduty_start).seconds / 60
            # all units are in minutes
        else:
            onduty_stop = (prestop_start - onduty_start).days * 24 * 60 + (prestop_start - onduty_start).seconds / 60 + \
                          prestop['hist_Duration']
            # all units are in minutes

            prestop_end = prestop_start + datetime.timedelta(0, prestop[
                'hist_Duration'] * 60)  # time + a number should be in unit of seconds

        mealtime = travtime / 4.5 * 40 / 60  # meal time 40 minutes per 4.5 hour; unit in hrs

        onduty_time = np.ceil(onduty_stop / 60 + travtime + mealtime + travtime_empty)  # unit in hrs

        # onduty_stop unit in mins, travtime unit in secs, onduty_time unit in hours
        HOS = 0

        if (onduty_time >= 14 and onduty_time < 28) or (np.ceil(travtime) >= 11 and np.ceil(travtime) < 22):
            HOS = 1
        elif (onduty_time >= 28 and onduty_time < 42) or (np.ceil(travtime) >= 22 and np.ceil(travtime) < 33):
            HOS = 2
        elif (onduty_time >= 42 and onduty_time < 56) or (np.ceil(travtime) >= 33 and np.ceil(travtime) < 44):
            HOS = 3
        elif (onduty_time >= 56 and onduty_time < 70) or (np.ceil(travtime) >= 44 and np.ceil(travtime) < 55):
            HOS = 4
        elif (onduty_time >= 70 and onduty_time < 84) or (np.ceil(travtime) >= 55 and np.ceil(travtime) < 66):
            HOS = 5
        Reason = ""

        if stop['arrived'] == 0:
            ETA = (datetime.timedelta(0, (HOS * 10 + travtime + mealtime) * 3600) + prestop_end).tz_convert(stop_tz)
            if ETA - pd.Timestamp(stop['Appt'], tz=stop_tz) > datetime.timedelta(0.3600):
                if (HOS > 0):
                    Reason = "Scheduling/HOS--ETA_Delay"
                else:
                    Reason = "ETA_Delay"
        else:
            ETA = pd.Timestamp(stop['Arrival'], tz=stop_tz)
        ETA = ETA.tz_convert(stop_tz)
        return (ETA, Reason)


    def Process_histdata(self):
        daily_load= self.__dynamicload
        daily_load_select = pd.merge(left=daily_load, right=timezones_df,
                                     left_on=['Timezone'], right_on=['Timezone'], how='left')

        daily_load_select.to_csv("temp_daily" + now.strftime("%Y%m%d") + '.csv', index=False)
        daily_load_select.to_csv("temp_daily.csv", index=False)

        # columnnames=daily_load_select.columns.tolist()
        # daily_load_df=pd.DataFrame(columns=columnnames )

        daily_load_df = daily_load_select
        daily_load_df['latebooking'] = 0
        daily_load_df['latedispatch'] = 0
        daily_load_df['preStop_OnTime'] = -1
        daily_load_df['preStop_Duration'] = -1
        daily_load_df['dist'] = daily_load_df[
            'Empty_Dist']  # initialize as empty dist, and will be updated with nextstopdistance when stopsequence>1
        daily_load_df['dispatch_Local'] = now
        # daily_load_df['DoW'] = daily_load_df['Appt'].strftime("%w")
        daily_load_df['ETA_ontime'] = -1
        daily_load_df['ETA'] = now
        daily_load_df['Reason'] = ""
        daily_load_df['arrived']=1
        daily_load_df.Customer = daily_load_df.Customer.replace(",", "")
        filteroutid = []
        speed_highway = 55
        speed_local = 35
        detention = 2
        workin_hour = 4

        #for i in daily_load_df.index:
        # not sure if we really need iloc. because loc. and iloc might be equal due to the order by in sql query
        # but it may be safer to use iloc
        #for i in daily_load_df.index:
        for i in range(0, len(daily_load_df)):
            # if(abs(daily_load_df.loc[i]['Appt']-daily_load_df.loc[i]['Arrival']).days>=1 ) :
            #     filteroutid.append(daily_load_df.loc[i]['LoadID'])
            #     continue
            loadstop = daily_load_df.iloc[i]
            localtz = loadstop['tz']
            localAppt = pd.Timestamp(daily_load_df['Appt'].iloc[i], tz=localtz)
            localArri = pd.Timestamp(daily_load_df['Arrival'].iloc[i], tz=localtz)
            daily_load_df['Appt'].iloc[i]=daily_load_df['Appt'].iloc[i].tz_localize(localtz)
            daily_load_df['Arrival'].iloc[i]=daily_load_df['Arrival'].iloc[i].tz_localize(localtz)
            now_local = now.tz_convert(localtz)
            daily_load_df['ETA'].iloc[i]= now_local
            if pd.Timestamp(daily_load_df['Arrival'].iloc[i]).strftime("%Y") == '1753':
                daily_load_df['ontime'].iloc[i] = 0 if now_local - localAppt > datetime.timedelta(0, 3600) else -1
                daily_load_df['arrived'].iloc[i]=0
                ### If we want to assign value, .loc[i] should be after the column name
                daily_load_df['Reason'].iloc[i] = "DataMissing-OverDue" if now_local - localAppt > datetime.timedelta(0,
                                                                                                                    3600) else ""
                # daily_load_df.loc[i]['ontime']=np.where ((pd.Timestamp(now).tz_localize(now_tz) - localAppt)
                #                                          > datetime.timedelta(0, 3600), 0, -1  )
                # daily_load_df.loc[i]['Reason'] = np.where ((pd.Timestamp(now).tz_localize(now_tz) - localAppt)> datetime.timedelta(0, 3600), "DataMising-OverDue", "")
                # ETA = now.tz_convert(localtz)  # initialization
            if daily_load_df.iloc[i]['StopSequence'] > 1:
                daily_load_df['dist'].iloc[i] = daily_load_df['NextStopDistance'].iloc[i - 1]
                speed = speed_local if daily_load_df['dist'].iloc[i] < 100 else speed_highway
                pretz = daily_load_df['tz'].iloc[i - 1]
                preAppt = pd.Timestamp(daily_load_df.iloc[i - 1]['Appt'], tz=pretz).tz_convert(localtz)
                preDept = pd.Timestamp(daily_load_df.iloc[i - 1]['Departure'], tz=pretz).tz_convert(localtz)
                preArrv = pd.Timestamp(daily_load_df.iloc[i - 1]['Arrival'], tz=pretz).tz_convert(localtz)
                travtime = daily_load_df['dist'].iloc[i] / speed * 3600  # unit in seconds

                travel_hour = (localArri - preDept).days * 24 + (localArri - preDept).seconds / 3600
                if daily_load_df['dist'].iloc[i] > speed * travel_hour and localArri.strftime(
                        "%Y") != '1753' and preDept.strftime("%Y") != '1753':
                    filteroutid.append(daily_load_df['LoadID'].iloc[i])
                    continue

                if preArrv.strftime("%Y") == '1753':
                    daily_load_df['preStop_OnTime'].iloc[i] = daily_load_df['f_rate'].iloc[i - 1]
                    daily_load_df['preStop_Duration'].iloc[i] = daily_load_df['hist_Duration'].iloc[i - 1]

                    ##when data is missing, just using historical data. not mandatoryily made the ontime rate = 1 for prestop
                    # if ( now - localAppt > datetime.timedelta(0, 3600)) :
                    #     daily_load_df.loc[i-1]['ontime'] = 0
                    #     daily_load_df.loc[i ]['preStop_OnTime'] = 0
                    #     daily_load_df.loc[i - 1]['Reason'] = "DataMising-OverDue"

                elif preDept.strftime("%Y") == '1753':
                    daily_load_df['preStop_OnTime'].iloc[i] = daily_load_df['ontime'].iloc[i - 1]
                    daily_load_df['preStop_Duration'].iloc[i] = daily_load_df['hist_Duration'].iloc[i - 1]
                else:
                    daily_load_df['preStop_OnTime'].iloc[i] = daily_load_df['ontime'].iloc[i - 1]
                    duration = daily_load_df['duration'].iloc[i - 1]
                    daily_load_df['preStop_Duration'].iloc[i] = duration if duration > 0 and duration < 360 else \
                    daily_load_df['hist_Duration'].iloc[i - 1]

                ETA, daily_load_df['Reason'].iloc[i] = HOS_checking(daily_load_df.iloc[i - 1], daily_load_df.iloc[i], travtime)

            else:
                daily_load_df['dist'].iloc[i] = daily_load_df['Empty_Dist'].iloc[i]
                speed = speed_local if daily_load_df.iloc[i]['dist'] < 100 else speed_highway
                # print (daily_load_df.loc[i]['dist'],speed_local,speed_highway,speed)
                dispatch = pd.Timestamp(daily_load_df.iloc[i]['Dispatch_Time'], tz='UTC').tz_convert(localtz)
                if dispatch - localAppt >= datetime.timedelta(0, 0, 0):
                    dispatch = pd.Timestamp(daily_load_df.iloc[i]['Empty_Time'], tz=localtz)
                daily_load_df['dispatch_Local'].iloc[i] = dispatch
                bookingtime = pd.Timestamp(daily_load_df['BookTimeUTC'].iloc[i], tz='UTC').tz_convert(localtz)

                daily_load_df['latebooking'].iloc[i] = 1 if localAppt - bookingtime <= datetime.timedelta(0, 3600 * 4) else 0
                daily_load_df['latedispatch'].iloc[i] = 1 if localAppt - dispatch <= datetime.timedelta(0, 3600 * 2) else 0
                daily_load_df['preStop_OnTime'].iloc[i] = 1 - daily_load_df['latedispatch'].iloc[i]
                # If already arrived, no need to check ETA. Otherwise, ETA is important
                travel_second = daily_load_df['dist'].iloc[i] / speed * 3600
                ETA = dispatch + datetime.timedelta(0, travel_second)
            if localArri.strftime("%Y") != '1753':
                ETA = localArri
            daily_load_df['ETA_ontime'].iloc[i] = 1 if ETA - localAppt <= datetime.timedelta(0, 3600) else 0
            daily_load_df['ETA'].iloc[i]= ETA
            # if ETA - localAppt <= datetime.timedelta(0, 3600):
            #     daily_load_df['ETA_ontime'].loc[i] = 1
            # else:
            #     daily_load_df['ETA_ontime'].loc[i] = 0
            #      daily_load_df.loc[i]['ETA_ontime'] = 1 if ETA- localAppt <= datetime.timedelta(0, 3600) else 0

            if daily_load_df['ETA_ontime'].iloc[i] == 0 and daily_load_df['StopSequence'].iloc[i - 1] > 1:
                if localArri.strftime("%Y") == '1753':
                    daily_load_df['Reason'].iloc[i] = "Prestop-DataMissing"
        daily_load_select = daily_load_df[~daily_load_df['LoadID'].isin(filteroutid)]
        daily_load_select['latebooking'].fillna(0, inplace=True)
        daily_load_select.to_csv("testdata" + now.strftime("%Y%m%d") + ".csv", index=False)
        return (daily_load_select)

