import pandas as pd
import os, sys,argparse


def printColumns(df):
    columns = df.columns
    for col in columns:
        print(col)
def list_unique(df, column):
    uniques = df[column].unique()
    for val in uniques:
        print(val)
def split_modes(df):
    alarm_col = df['Alarm']
    time_col = df['Time']
    date_col = df['Date']
    index_col = df['Index']
    alerts = alarm_col.values
    timestamps = time_col.values
    dates = date_col.values
    index = 0
    tuple_list = []
    for val in alerts:
        if val == "AUTO MODE ACTIVE PLGM OFF":
            print("AUTO MODE ON AT " + str(index))
            tuple_list.append(tuple((dates[index],timestamps[index],index,index_col[index])))
        index += 1
    print(tuple_list)
    return tuple_list
#if returns negative value, time 1 is earlier than time_2
#if returns positive value, time 1 is later than time_2
#if 0, they are the same time
def compare_time(time_1,time_2):
    time_split_1 = time_1.split(":")
    time_split_2 = time_2.split(":")
    total_diff = 0
    for x in range(0,len(time_split_1)):
        diff = int(time_split_1[x]) - int(time_split_2[x])
        if diff != 0:
            if x == 0:
                total_diff += diff * 3600
            if x == 1:
                total_diff += diff * 60
            if x == 2:
                total_diff += diff

    return total_diff
def sync_modes_inclusive(df,auto_on_date,auto_on_time):
    print("Looking for all rows on date: " + auto_on_date)
    dates = df.loc[df['Date'].isin([auto_on_date])]
    #print("Dates is a: " + str(type(dates)))
    rows = len(dates.index) 
    columns = len(df.columns)
    #print("Data is a " + str(rows) + " x " + str(columns) + " dataframe")
    current_lowest = 999999
    lowest_index =0 
    for index, rows in dates.iterrows():
        diff = abs(compare_time(rows['Time'],auto_on_time))
        if diff < current_lowest:
            #      print("New lowest at: " + str(rows['Index']),end=",")
            #      print("Time was: " + rows['Time'])
            current_lowest = diff
            lowest_index = index
            # else:
            #    print("Diff: " + str(diff) + " was not less than " + str(current_lowest) + " at " + str(lowest_index))
    #print("Final current lowest was: " + str(current_lowest))
    #print("Final time was: " + df.iloc[[lowest_index]]['Time'])
    return lowest_index


def get_df(csv):
    with open(csv, "r") as csv:
        df = pd.read_csv(csv)
        return df
def get_auto_end(df):
    date_col = df['Date']
    time_col = df['Time']
    index_col = df['Index']
    index = 0
    dates = date_col.values
    times = time_col.values
    indexes = index_col.values
    tuple_list =[]
    while index < len(indexes)- 1:
        if index_col[index] == 0:
            tuple_list.append((dates[index],times[index],indexes[index],index))
        index += 1
    return tuple_list





#Auto_start_indexes (Date,time, Real_CGM_Index, CMG_Index_Col, Insulin_Real_Index, Insulin_Index_Col)
#Auto_end_indexes(Date, Time, Real_CGM_Index, CMG_Index_col, Insulin_Real_index, Insulin_Index_Col)

if __name__ == "__main__":
    CGM = get_df(sys.argv[1])
    Insulin = get_df(sys.argv[2])
    date_time_tuples = split_modes(Insulin)
    print(date_time_tuples)
    auto_start_indexes_list = []
    auto_end_indexes_list = []
    for tup in date_time_tuples:
        CGM_index = sync_modes_inclusive(CGM, tup[0],tup[1])
        Insulin_index = tup[2]
        auto_start_indexes_list.append((tup[0],tup[1],CGM_index,CGM.iloc[[CGM_index]]['Index'].values[0],Insulin_index,Insulin.iloc[[Insulin_index]]['Index'].values[0]))
    auto_end_date_time = get_auto_end(Insulin)
    for tup in auto_end_date_time:
        CMG_index = sync_modes_inclusive(CGM, tup[0],tup[1])
        Insulin_index = tup[3]
        auto_end_indexes_list.append((tup[0],tup[1],CGM_index,CGM.iloc[[CMG_index]]['Index'].values[0],Insulin_index,Insulin.iloc[[Insulin_index]]['Index'].values[0]))
    print("Date, Time, Real_CMG_index, CMG_Index_col, Real_Insulin_index, Insulin_Index_col\n-----------------------------------------------------------------")
    print("Starts")
    for tup in auto_start_indexes_list:
        print(tup)
    print("---------------------------------------------------------")
    print("Ends")
    for tup in auto_end_indexes_list:
        print(tup)
    list_unique(Insulin,"Alarm")


    



