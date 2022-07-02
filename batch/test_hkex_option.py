
import pandas as pd
import datetime
import calendar

def format_date(date):
    return date.strftime("%y%m%d")

print(format_date(datetime.datetime(2022, 6,28) ))

def get_expiry_date(expiry_date):
    ed = datetime.datetime.strptime(expiry_date, '%b%y')
    last_day = calendar.monthrange(ed.year, ed.month)[1]
    return datetime.datetime(ed.year, ed.month, last_day)

print(get_expiry_date("JUN22"))

#exit(0)

# a = append and w = write
f = open("../db/job/3 hk stock option daily/dqe220628.csv", "r", encoding='UTF-8')

summary_df = pd.DataFrame(columns=["HKATS CODE","UNDERLYING STOCK","TICKER","TOTAL-TRADING","CALLSL-TRADING","PUTSL-TRADING",
    "TOTAL-OI","CALLS-OI","PUTS-OI","IV%"])
dict_df = {}

# read file - the summary
#read until this line: ,,,"SUMMARY TRADING VOLUME",,,"SUMMARY OPEN INTEREST"

summary_header = '"HKATS CODE","UNDERLYING STOCK",,"TOTAL","CALLS","PUTS","TOTAL","CALLS","PUTS","IV%*"'
contract_header = '"CONTRACT",,,"OPENING PRICE#","DAILY HIGH#","DAILY LOW#","SETTLEMENT PRICE","CHANGE IN SETTLEMENT","IV%","VOLUME","OPEN INTEREST","CHANGE IN OI"'
cnt = 0

linesep = f.readlines()
state = 0
empty_line = 0
data_list = []
for line in linesep:
    line = line.strip()
    cnt += 1

    #if cnt > 30:
    #    break

    #print("R" + str(cnt) + " " + line)

    if state == 0:
        if line == summary_header:
            #print("state 1 at " + str(cnt))
            state = 1
            data_list = []
            continue
        elif line == contract_header:
            #print("state 2 at " + str(cnt))
            state = 2
            data_list = []
            continue
    
    if state == 1:
        if(line == ""):
            summary_df = summary_df.append(data_list, ignore_index=True)
            state = 0
        else:
            dd = line.split(",")
            data = {"HKATS CODE": dd[0] ,"UNDERLYING STOCK" : dd[1], "TICKER": dd[2],
                "TOTAL-TRADING": dd[3],"CALLS-TRADING": dd[4],"PUTS-TRADING": dd[5],
                "TOTAL-OI": dd[6],"CALLS-OI": dd[7],"PUTS-OI": dd[8],"IV%": dd[9]}
            data_list.append(data)
            
    if state == 2:
        if line == "":
            empty_line +=1
        else:
            empty_line = 0

        if empty_line == 2:
            print("finish")
            call_put = call_put.append(data_list, ignore_index=True)
            dict_df[symbol] = call_put
            state = 0

        elif line.startswith('"CLASS'):
            symbol = line.split(" ")[1]
            print("x" + line)

            call_put = pd.DataFrame(columns=["CONTRACT-EXPIRY","CONTRACT-STRIKE","CONTRACT-TYPE",
                "OPENING PRICE","DAILY HIGH","DAILY LOW", "SETTLEMENT PRICE","CHANGE IN SETTLEMENT","IV%",
                "VOLUME","OPEN INTEREST","CHANGE IN OI"])
        else:
            #print("y" + line)
            dd = line.split(",")
            if dd[0] == "":
                continue

            data = {"CONTRACT-EXPIRY": dd[0],"CONTRACT-STRIKE": dd[1],"CONTRACT-TYPE": dd[2],
                "OPENING PRICE": dd[3],"DAILY HIGH": dd[4],"DAILY LOW": dd[5], "SETTLEMENT PRICE": dd[6],
                "CHANGE IN SETTLEMENT": dd[7],"IV%": dd[8],
                "VOLUME": dd[9],"OPEN INTEREST": dd[10],"CHANGE IN OI": dd[11]}
            data_list.append(data)
            

f.close()

print(summary_df)
#print(dict_df)

