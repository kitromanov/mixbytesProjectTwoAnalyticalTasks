import json
from re import X
from matplotlib import pyplot as plt 
import numpy as np  
from sklearn.linear_model import LinearRegression
from pycoingecko import CoinGeckoAPI
from scipy import stats
from scipy import interpolate

deposit_hash = '0x2da466a7b24304f47e87fa2e1e5a81b9831ce54fec19055ce277c'
redeem_hash = '0x4896181ff8f4543cc00db9fe9b6fb7e6f032b7eb772c72ab1ec1b4d2e03b9369' 
st_DOT = '0xFA36Fe1dA08C89eC72Ea1F0143a35bFd5DAea108'

day_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
dot_exchange_rate_in_dollars = {'5-5-2022': 16.292368065665716 ,
'6-5-2022': 14.598846299024533 ,
'10-5-2022': 10.801429785440924 ,
'16-5-2022': 11.800640817629374 ,
'17-5-2022': 10.661734977316367 ,
'18-5-2022': 11.053819427499075 ,
'19-5-2022': 9.517212484127024 ,
'20-5-2022': 10.07163545677334 ,
'21-5-2022': 9.695758499813333 ,
'23-5-2022': 10.189629881421922 ,
'25-5-2022': 10.197008650448218 ,
'26-5-2022': 9.855449944611918 ,
'27-5-2022': 9.198261981785189 ,
'30-5-2022': 9.986166924880612 ,
'1-6-2022': 10.448283148141524 ,
'2-6-2022': 9.484222468578501 ,
'3-6-2022': 9.896299945398498 ,
'4-6-2022': 9.372006368573782 ,
'5-6-2022': 9.436263733449623 ,
'6-6-2022': 9.338347728064072 ,
'7-6-2022': 9.472049966781283 ,
'8-6-2022': 9.245287369128352 ,
'9-6-2022': 9.000860375425932 ,
'10-6-2022': 9.224408429940054 ,
'11-6-2022': 8.656938948250048 ,
'12-6-2022': 8.007773894291699 ,
'13-6-2022': 7.450027957000497 ,
'14-6-2022': 7.001810875279709 ,
'15-6-2022': 7.379032716449845 ,
'16-6-2022': 8.516714356116118 ,
'17-6-2022': 7.105844592665794 ,
'18-6-2022': 7.325464174931059 ,
'19-6-2022': 7.068027828135199 ,
'20-6-2022': 7.504558358292622 ,
'21-6-2022': 7.894626280316918 ,
'22-6-2022': 7.736855254831152 ,
'23-6-2022': 7.419624804433869 ,
'24-6-2022': 7.806285623861093 ,
'25-6-2022': 8.21567426052568 ,
'26-6-2022': 8.135501883565913 ,
'27-6-2022': 7.861850137967533 ,
'28-6-2022': 7.72479055629487 ,
'29-6-2022': 7.29512308847008 ,
'30-6-2022': 7.002323505207497 ,
'1-7-2022': 6.970042715539203 ,
'2-7-2022': 6.789762340578334 ,
'3-7-2022': 6.827235670454218 ,
'4-7-2022': 6.849241180089714 ,
'5-7-2022': 7.169210518110505 ,
'6-7-2022': 6.840206443166161 ,
'7-7-2022': 6.932599081682027 ,
'8-7-2022': 7.320223383970988 ,
'9-7-2022': 7.138690731338326 ,
'10-7-2022': 7.2620836518951455 ,
'11-7-2022': 6.853636299733879 ,
'12-7-2022': 6.548562170533149 ,
'13-7-2022': 6.299920689741761 ,
'14-7-2022': 6.466718030554244 ,}

def emission_function(x_0, t):
    return (0.02 * x_0 * 1.1*t) / (365 * 24 * 60 * 60)

def get_dot_tvl(first_day, first_month, start_time, current_time, total_supply):
    cg = CoinGeckoAPI()
    past_days = (current_time - start_time)//(60 * 60 * 24)
    current_day = (first_day + past_days)
    current_month = first_month
    for i in range(first_month, 13):
        if current_day > day_in_month[i]:
            current_day -= day_in_month[i]
            current_month += 1
    current_day = str(current_day) + '-' + str(current_month) + '-2022'
    if dot_exchange_rate_in_dollars.get(current_day) != None:
        # print(current_day, dot_exchange_rate_in_dollars.get(current_day))
        return dot_exchange_rate_in_dollars.get(current_day) * total_supply
    else:
        # never go here as all data was saved after the last launch 
        exchange_rate = cg.get_coin_history_by_id('polkadot', date=current_day)['market_data']['current_price']['usd']
        print('\'' + str(current_day) + '\'' + ':', exchange_rate, ',')
        dot_exchange_rate_in_dollars[current_day] = exchange_rate
        return exchange_rate * total_supply

with open("deposit_events.json", "r") as read_file1, open("redeem_events.json", "r") as read_file2:
    data_of_deposit = json.load(read_file1)
    data_of_redeem = json.load(read_file2)
deposit_result = data_of_deposit['result']
redeem_result = data_of_redeem['result']
total_supply_changes = []
for tr in deposit_result:
    total_supply_update = []
    total_supply_update.append(int(tr['timeStamp'][2:], 16))
    total_supply_update.append(int(tr['data'], 16))
    total_supply_changes.append(total_supply_update)
for tr in redeem_result:
    total_supply_update = []
    total_supply_update.append(int(tr['timeStamp'][2:], 16))
    total_supply_update.append((-1) * int(tr['data'], 16))
    total_supply_changes.append(total_supply_update)

total_supply_changes.sort()
balance_in_time = [0]
dot_tvl_in_time = [0]
time_stamps = [0]
start_time = total_supply_changes[0][0]
day_of_first_tr = 5
month_of_first_tr = 5
for tr in total_supply_changes:
    cur_index = len(balance_in_time)
    current_balance = balance_in_time[cur_index - 1] + tr[1]/10**10
    balance_in_time.append(current_balance)
    current_time = tr[0]
    time_stamps.append(current_time)
    dollar_price = get_dot_tvl(day_of_first_tr, month_of_first_tr, start_time, current_time, current_balance)
    dot_tvl_in_time.append(dollar_price)

print("Amount of Deposit and Redeem:", len(total_supply_changes))
print("Current balance:", balance_in_time[len(balance_in_time) - 1])

# plt.plot(time_stamps[210:], dot_tvl_in_time[210:])
# plt.xlabel('TimeStamp, sec')
# plt.ylabel('TVL, $')
# plt.grid(True)
# plt.show()

print(balance_in_time[1:10])
print(time_stamps[1:10])
print('=====')
print(time_stamps[len(time_stamps) - 1])
# print(int(result[0]['timeStamp'][2:], 16))
# print(int(result[0]['data'], 16))
# print(time_stamps)

# Add linear regression
x = np.array(time_stamps[210:])
y = np.array(dot_tvl_in_time[210:])
res = stats.linregress(x, y)
plt.plot(x, y, label='TVL')
plt.plot(x, res.intercept + res.slope*x, 'r', label='Linear regression of TVL')


# Add emission graph
emission_x = [time_stamps[len(time_stamps) - 1]]
emission_y = [dot_tvl_in_time[len(dot_tvl_in_time) - 1]]
current_balance = balance_in_time[len(balance_in_time) - 1]

for i in range(10000):
    emission_x.append(emission_x[len(emission_x) - 1] + 1)
    emission_y.append(emission_function(current_balance, 1) * 10**10)
    current_balance = current_balance + current_balance *0.1 / (365 * 24 * 60 * 60)
plt.plot(np.array(emission_x), np.array(emission_y), 'g', label='2% of emission')
plt.grid(True)
plt.legend()
plt.show()

print("=======================")
# print(emission_x[:10])
# print(emission_y[:10])