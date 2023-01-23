#SPS CLAIM/STAKER BitcoinJake09 11/15/2022

import json
import requests
from requests.auth import HTTPBasicAuth
from requests_html import AsyncHTMLSession
import asyncio
import time
import datetime
import random, string
from beem import Hive
from beem.account import Account
from beem.transactionbuilder import TransactionBuilder
from beembase import operations
from beembase.operations import Custom_json

sleepTime = 60*1 # 1 minute

#ONLY CHANGE VARIABLES IN THIS SECTION!!!
hiveName = 'bitcoinjake09' #replace my name with your HIVE name
wif = "POSTINGKEYHERE" #posting key here
#change below to greater times for less RC use
#claimTime is how often you want script to claim, numbers below represented in minutes
claimTime = sleepTime*15 # 15 minutes
#stakeTime is how often you want to stake
stakeTime = sleepTime*15 # 15 minutes
#THANK YOU

async def keyGen():
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return x


def timeNow(): #gets current time function
    #thank https://peakd.com/@zimos for time suggestion
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time

def getSPSPbalance(): #gets claimable SPS/SPSP balance
    r = requests.get('https://api.splinterlands.io/players/balances?username='+hiveName)
    jsonData = json.loads(r.text)
    balanceBool = False
    #print(str(jsonData))
    for datas in jsonData:
        for key, value in datas.items():
                #print("Key: " + str(key) + " Value: " + str(value))
                if balanceBool is True:
                    if (str(key) == "balance"):
                        return value
                if (str(key) == "token") and (str(value) == "SPSP"):
                    balanceBool = True
    return 0

def getSPSbalance(): #get liquid balance/stakable
    r = requests.get('https://api.splinterlands.io/players/balances?username='+hiveName)
    jsonData = json.loads(r.text)
    balanceBool = False
    #print(str(jsonData))
    for datas in jsonData:
        for key, value in datas.items():
                #print("Key: " + str(key) + " Value: " + str(value))
                if balanceBool is True:
                    if (str(key) == "balance"):
                        return value
                if (str(key) == "token") and (str(value) == "SPS"):
                    balanceBool = True
    return 0

isRunning = False #for main loop check
balance24 = getSPSPbalance() #for 24 hour snapshot to show balance increase
time24 = datetime.datetime.now() #used for the balance snapshot
staked24 = 0 #used for balance snapshot

async def main():
    #main event loop
    global isRunning #make sure we only run once
    if isRunning is False:
        print("Started") #shows we are about to start tasks
        #before we start, lets print balances:
        print(str(timeNow()) + ": CanStake: " + str(getSPSbalance()))
        print(str(timeNow()) + ": totalBalance: " + str(getSPSPbalance()))
        asyncio.create_task(claimNow()) #claim loop
        asyncio.create_task(stakeNow()) #stake loop
        asyncio.create_task(update24()) #balance snap loop
        print("Working...") #done with main function since loops are running after :D
        isRunning = True
    await asyncio.sleep(100000 * 60) #really long sleep or main stops

async def claimNow():
    while True:
        print(str(timeNow()) + ": totalBalance: " + str(getSPSPbalance()))
        tx = TransactionBuilder() #lets build a tx
        #[ [ "custom_json", { "id": "sm_stake_tokens", "json": "{\"token\":\"SPS\",\"qty\":0,\"app\":\"splinterlands/0.7.139\",\"n\":\"59pbaxZtuS\"}", "required_auths": [], "required_posting_auths": [ "bitcoinjake09" ] } ] ]
        payload = {"token":"sps","qty":0,"app":"CryptoFam-sps-autocompunder", "n":await keyGen()} #payload basically what the tx says to do
        new_json = { #found these in the hive explorer after i did my first few tx's and just put in right code format
              "required_auths": [],
              "required_posting_auths": [hiveName],
              "id": "sm_stake_tokens",
              "json": payload
            }
        tx.appendOps(Custom_json(new_json)) #add ops to tx
        tx.appendWif(wif) #add key
        tx.sign() #sign
        tx.broadcast() #broadcast
        await asyncio.sleep(claimTime) #wait for next time

async def stakeNow():
    global staked24
    await asyncio.sleep(30) #sleep for 30 seconds at start to offset stakes 30 seconds after claims :D
    while True:
        canStake = getSPSbalance()
        staked24 = staked24 + canStake
        tx = TransactionBuilder()
        #[ [ "custom_json", { "id": "sm_stake_tokens", "json": "{\"token\":\"SPS\",\"qty\":5,\"app\":\"splinterlands/0.7.139\",\"n\":\"LEimOFwwIW\"}", "required_auths": [], "required_posting_auths": [ "bitcoinjake09" ] } ] ]
        payload = {"token":"SPS","qty":canStake, "app":"CryptoFam-sps-autocompunder", "n":await keyGen()}
        new_json = {
              "required_auths": [],
              "required_posting_auths": [hiveName],
              "id": "sm_stake_tokens",
              "json": payload
            }
        tx.appendOps(Custom_json(new_json))
        tx.appendWif(wif)
        tx.sign()
        tx.broadcast()
        print(str(timeNow()) + ": " + str(canStake) + " STAKED!")
        await asyncio.sleep(stakeTime)

async def update24():
    global time24, staked24, balance24
    while True: #every 24 hours this should spit out some numbers xD
        t24 = time24 + datetime.timedelta(hours = 24)
        if t24 < datetime.datetime.now():
            print(str(timeNow()) + ": " + str(str("{0:.3f}".format(staked24))) + " STAKED in 24 hours!! \n Balance increased from: " + str("{0:.3f}".format(balance24)) + " to: " +str("{0:.3f}".format(getSPSPbalance())) + " SPS!")

            balance24 = getSPSPbalance()
            staked24 = 0
            time24 = datetime.datetime.now()
        await asyncio.sleep(sleepTime)

if __name__ == "__main__":
    asyncio.run(main())
