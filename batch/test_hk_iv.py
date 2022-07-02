
import pandas as pd
import datetime
import calendar

def main():
    f = open("../db/job/4 hk stock option iv/statistics_hv_iv.csv", "r", encoding='UTF-8')

    state = 0
    header = "Trading date, IV (%), HV10 (%), HV30 (%), HV60 (%), HV90 (%)"
    
    df = pd.DataFrame(columns=["Trading date", "IV (%)", "HV10 (%)", "HV30 (%)", "HV60 (%)", "HV90 (%)"])
    data_list = []
    cnt = 0
    linesep = f.readlines()
    for line in linesep:
        line = line.strip()
        cnt += 1

        if state == 0:
            if line == header:
                state = 1
                continue

        if state == 1:
            dd = line.split(",")
            #print("x" + dd[0])
            t_date = datetime.datetime.strptime(dd[0], '%d/%m/%Y')
            data = {"Trading date": t_date ,"IV (%)" : dd[1], "HV10 (%)": dd[2],
                "HV30 (%)": dd[3],"HV60 (%)": dd[4],"HV90 (%)": dd[5]}
            data_list.append(data)

    df = df.append(data_list, ignore_index=True)

    return df

if __name__ == '__main__':
    
    df = main()
    print(df)