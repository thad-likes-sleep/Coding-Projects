import requests
import datetime
import re

#Before Use Instruction:
#Create a txt file titled apikey.txt and key in your API key for Alpha Vantage

datadaily = {}
dataweekly = {}
currentp = float(0.0)
yesterday = ''
apikey = ''


def main():
    global yesterday
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterdaystr = yesterday.isoformat()
    symbol = input('Symbol: ')

    with open("apikey.txt", "r") as file:
        global apikey
        apikey = file.read()

    url1 = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={apikey}'
    r1 = requests.get(url1)
    data1 = r1.json()

    try:
        global datadaily
        datadaily = data1['Time Series (Daily)']
    except KeyError:
        raise ValueError('Invalid Symbol or Invalid Key')

    global currentp
    currentp = float(datadaily[yesterdaystr]["4. close"])
    print(f'{currentp}USD as of {yesterdaystr}')

    while True:
        func = input('Average/Change From/Change Since High or Low/Exit: ').lower()
        if func == 'average':
            time = input('1W/1M/3M/6M/1Y: ').lower()
            print(function_average(symbol, time))
            continue
        elif func == 'change from':
            date_ = input('Date(YYYY-MM-DD): ')
            print(function_change_from(symbol, date_))
            continue
        elif func == 'change since high or low':
            time = input('1W/1M/3M/6M/1Y/2Y/5Y: ').lower()
            hol = input('High/Low: ').lower()
            print(function_cshol(symbol, time, hol))
            continue
        elif func == 'exit':
            break
        else:
            print('Invalid function')
            continue


def function_average(symbol, time):
    total = float(0)
    global dataweekly
    ii = list(datadaily.values())
    if time == '1w':
        for _ in range(7):
            daydata = ii[_]
            total += float(daydata['4. close'])
        return f'1 week average is {total / 7}USD'
    elif time == '1m':
        for _ in range(30):
            daydata = ii[_]
            total += float(daydata['4. close'])
        return f'1 month average is {total / 30}USD'
    elif time == '3m':
        for _ in range(90):
            daydata = ii[_]
            total += float(daydata['4. close'])
        return f'3 month average is {total / 90}USD'
    elif time == '6m':
        checkweekly(symbol)
        iiweek = list(dataweekly.values())
        for _ in range(26):
            weekdata = iiweek[_]
            total += float(weekdata['4. close'])
        return f'6 month average is {total / 26}USD'
    elif time == '1y':
        checkweekly(symbol)
        iiweek = list(dataweekly.values())
        for _ in range(52):
            weekdata = iiweek[_]
            total += float(weekdata['4. close'])
        return f'1 year average is {total / 52}USD'
    else:
        return 'Invalid time frame'


def function_change_from(symbol, date_):
    if re.search(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', date_):
        year, month, day = date_.split('-')
        startdate = datetime.date(int(year), int(month), int(day))
    else:
        return 'Invalid Date'
    difference = yesterday - startdate
    daysdiff = difference.days
    if daysdiff <= 99:
        startprice = datadaily[date_]["4. close"]
    elif daysdiff > 99:
        checkweekly(symbol)
        daystofriday = 4 - startdate.weekday()
        startdatefriday = startdate + datetime.timedelta(days=daystofriday)
        strstartdatefriday = startdatefriday.strftime("%Y-%m-%d")
        if daystofriday >= 2:
            startprice = dataweekly[strstartdatefriday]['1. open']
        elif daystofriday < 2:
            startprice = dataweekly[strstartdatefriday]['4. close']
    difference = currentp - float(startprice)
    pdiff = difference / float(startprice) * 100
    if difference >= 0:
        return f'{symbol} was at {startprice}USD and has increased by {pdiff}% to current price of {currentp}USD'
    elif difference < 0:
        return f'{symbol} was at {startprice}USD and has decreased by {pdiff * -1}% to current price of {currentp}USD'


def function_cshol(symbol, time, hol):
    dict_ = {'1w': 1, '1m': 4, '3m': 13, '6m': 26, '1y': 52, '2y': 104, '5y': 260}
    try:
        numofw = dict_[time]
    except KeyError:
        return 'Invalid time range'
    checkweekly(symbol)
    ii = list(dataweekly.values())
    if hol == 'high':
        highestp = 0
        for _ in range(numofw):
            if float(ii[_]['2. high']) >= highestp:
                highestp = float(ii[_]['2. high'])
        pdiff = (highestp - currentp) / highestp * 100
        return f'{symbol} has decreased from high of {highestp}USD by {pdiff}% to a current price of {currentp}USD'
    elif hol == 'low':
        for _ in range(numofw):
            if _ == 0:
                lowestp = float(ii[_]['3. low'])
            if float(ii[_]['3. low']) <= lowestp:
                lowestp = float(ii[_]['3. low'])
        pdiff = (currentp - lowestp) / lowestp * 100
        return f'{symbol} has increased from low of {lowestp}USD by {pdiff}% to a current price of {currentp}USD'
    else:
        return 'Invalid high or low'


def checkweekly(symbol):
    global dataweekly
    if not dataweekly:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey={apikey}'
        r = requests.get(url)
        data = r.json()
        dataweekly = data['Weekly Time Series']


if __name__ == "__main__":
    main()
