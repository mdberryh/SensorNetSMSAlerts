# we import the Twilio client from the dependency we just installed

import json
import urllib.request
import time

class smslog:
    def __init__(self, datetime, to, msg):
        self.datetime = datetime
        self.to = to
        self.msg = msg

logfile = list() #list of smslog objects

#one way to define sort function...
# def GetDateTimeObj(custom):
#     return custom['datetime']
# print(sorted(logs, key=GetDateTimeObj,reverse=True))

def SendSMS(accountID,token, toNumber, fromNumber, msg):
    from twilio.rest import Client
    client = Client(accountID,token)
    client.messages.create(to=toNumber, from_=fromNumber, body=msg)
    return

#for time stamp file...should have log with json objects...
# each line will have {"datetime":"", "from":"","to":"","msg":""}
# write a new line appended to the file with the above JSON
# to read...read the last line in the file.

# create date time from now - throttleInMinutes
# create date time from the json datetime
# check if the datetime is older than the throttle datetime..return true/false
# if no date in the file then return true...throttle time expired.
def IsStoveLowTemp(stoveInC,weatherInC):
    # if throttle time has expired and wood stove is < 68.3333 (155F)
    #  AND wood stove is > 46.1111 AND outsideTemp is < 12 (54F)
    stoveIsRunning = float(stoveInC) > 46.11 and float(weatherInC) < 12
    stoveIsLowTemp = float(stoveInC) < 68.33

    if(stoveIsRunning and stoveIsLowTemp):
        return True
    return False

def IsStoveHighTemp(stoveInC,weatherInC):
    # if throttle time has expired and wood stove is < 68.3333 (155F)
    #  AND wood stove is > 46.1111 AND outsideTemp is < 12 (54F)
    stoveIsTooHigh = float(stoveInC) > 98.55
    return stoveIsTooHigh

# then wood stove is still in operation and we should send an alert to Fill it.

# if throttle time has expired and wood stove is > 96.11 (205F) then we need to dump some heat

def HasAlreadySentMessage(toNumber, throttleInMinutes):
    import datetime
    lastdatetime = FindLastTimestampFromNumber(toNumber)

    #print(lastdatetime.strftime('%Y-%m-%d-%H-%M-%S'))
    if(lastdatetime is None):
        return False # message has not been sent.
    # now we know we have a datetime list last text was sent...
    #print(lastdatetime.strftime('%Y-%m-%d-%H-%M-%S'))
    throttledate = datetime.datetime.now() - datetime.timedelta(minutes=int(throttleInMinutes))
    #print(throttledate.strftime('%Y-%m-%d-%H-%M-%S'))
    return lastdatetime > throttledate

def LogMessageSentDetails(lto,lmsg):
    import datetime
    obj = {}
    obj['datetime'] = datetime.datetime.now()
    obj['to'] = lto
    obj['msg'] = lmsg
    logfile.append(obj)
    return


def FindLastTimestampFromNumber(number):
    logs = logfile

    if(len(logs)<=0):
        print("no logs added yet")
        return None

    #print(logs)
    logs = sorted(logs, key=lambda o:o['datetime'],reverse=True)

    for item in logs:
        #print("item:" + item["to"])
        #print("number:" +number)
        if(item['to']==number):
            print("found number " + str(number) + " in logs. datetime: " +  item['datetime'].strftime('%Y-%m-%d-%H-%M-%S'))
            #print(item['datetime'].strftime('%Y-%m-%d-%H-%M-%S'))
            return item['datetime']
    return None # not found

def SendAlert(configs,secrets,msg):
    for number in configs['to']:
        if HasAlreadySentMessage(number,configs['ThrottleInMinutes']) is True:
            print("Already sent message to: " + number)
            continue
        else:
            print("sending text to: " + number + ": " + msg)
            SendSMS(secrets['account'],secrets['token'], number, configs['from'], msg)
            LogMessageSentDetails(number,msg)

configs =''
with open('sms.conf') as json_data:
    configs = json.load(json_data)

#print(configs)

secrets = ''

with open('sms.secrets') as json_data:
    secrets = json.load(json_data)

while True:

    try:
        # get request to get wood stove temp.
        stoveTempInC = float(json.loads(urllib.request.urlopen("http://192.168.1.3/api/getLatestWoodStoveDataRow.php?numRows=1").read())[0]['temp'])

        weatherTempInC = float(json.loads(urllib.request.urlopen("http://192.168.1.3/api/getLatestWeatherDataRow.php?numRows=1").read())[0]['temp'])
        #print(stoveTempInC)
        #print(weatherTempInC)

        if IsStoveHighTemp(stoveTempInC, weatherTempInC):
            # send message to all phone numbers if not already sent with in throttle limit
            tempinF= float(stoveTempInC) *1.8 + 32
            SendAlert(configs, secrets, "WoodStove Too HOT! Temp: " + str(tempinF))
        elif IsStoveLowTemp(stoveTempInC, weatherTempInC):
            # send message to all phone numbers if not already sent with in throttle limit
            tempinF= float(stoveTempInC) *1.8 + 32
            SendAlert(configs, secrets, "WoodStove Needs wood! Temp: " + str(tempinF))
    except ValueError:
        print("fetching data may have returned none...")
          
    time.sleep(60*5) # check temps every 5 minutes
