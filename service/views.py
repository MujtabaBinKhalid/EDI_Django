import json
import socket
import io
import ftplib
from django.shortcuts import render
from main.models import accountRegistration
from background_task import background
from io import BytesIO
import requests
from django.contrib.sessions.backends.db import SessionStore


@background(schedule=300)
def tcpRequest(): 
    url = "http://54.245.173.223:3000/account/"
    payload = ""
    headers = {
        'cache-control': "no-cache",
        }
    response = requests.request("GET", url, data=payload, headers=headers)
    accounts =  json.loads(response.text)
    for account in range(len(accounts.get("data", "empty"))):
        global host, ftp
        ftp = ftplib.FTP((accounts.get("data", "empty"))[account].get ("ipHost"),
        (accounts.get("data", "empty"))[account].get ("userName"), 
        (accounts.get("data", "empty"))[account].get ("password"))
        # print("translating files of account " + account.ipHost)
        byteReading = BytesIO()

        
        files = []
        innerDirectory = (accounts.get("data", "empty"))[account].get ("input_path")
        files = ftp.nlst(innerDirectory)
        print(files)
        files.remove(".")
        files.remove("..")
        print("file array Ready!")
        for file_name in files:
            if (file_name == "notSucessful"):
                files.remove("notSucessful")

            elif (file_name == "sucessful"):
                files.remove("sucessful")

            elif(file_name.split('.')[1] == "edi"):
                fileName = file_name.split('.')[0]
                filepath = innerDirectory+"/"+file_name
                ftp.retrbinary('RETR ' + filepath, byteReading.write)
                readingFile = byteReading.getvalue().decode("utf-8")
                # print ((accounts.get("data", "empty"))[account])
                # print (readingFile)
                # print (innerDirectory)
                # print (fileName)
                readingCurrentFile((accounts.get("data", "empty"))[account], readingFile, innerDirectory, fileName)


def readingCurrentFile(accountDetails, readingFile, filepath, fileName):
    data = {}
    loadNumber = readingFile.split('*')[2].split("G")[0]
    rdate = readingFile.split('*')[4] + " " + readingFile.split('*')[6]
    senderNumber = readingFile.split('*')[34].split("A")[0]
    weight = readingFile.split('*')[37]
    ssdate = readingFile.split('*')[26] + " "+readingFile.split('*')[28]
    userEmail = readingFile.split('*')[12]
    deviceserial = readingFile.split('*')[15].split(":")[1]
    mcnumber = readingFile.split('*')[18].split(":")[1]
    senderName = readingFile.split("*")[21]
    ssaddress = readingFile.split("*")[23]
    ai = readingFile.split('*')[40].split(":")[1]
    aa = readingFile.split('*')[43].split(":")[1]
    maxp = readingFile.split('*')[49].split(":")[1]
    minp = readingFile.split('*')[46].split(":")[1]
    minh = readingFile.split('*')[52].split(":")[1]
    maxh = readingFile.split('*')[55].split(":")[1]
    mint = readingFile.split('*')[58].split(":")[1]
    maxt = readingFile.split('*')[61].split(":")[1]
    trucknumber = readingFile.split('*')[64].split(":")[1]
    trailernumber = readingFile.split('*')[67].split(":")[1]
    trailersize = readingFile.split('*')[70].split(":")[1]
    commodity = readingFile.split('*')[73]
    pallet = readingFile.split('*')[75]
    receiverName = readingFile.split("*")[78]
    sraddress = readingFile.split("*")[80]
    sddate = readingFile.split("*")[83]+" "+readingFile.split("*")[85]
    receiverNumber = readingFile.split('*')[90]

    data['commodities'] = commodity
    data['weight'] = float(weight)
    data['mc_number'] = mcnumber
    data['trucking_company_name'] = senderName
    data['active_insurance'] = bool(ai)
    data['active_authority'] = bool(aa)
    data['min_temperature'] = int(mint)
    data['max_temperature'] = int(maxt)
    data['truck_number'] = trucknumber
    data['trailer_number'] = int(trailernumber)
    data['trailer_size'] = trailersize
    data['driver_number'] = senderNumber
    data['min_pressure'] = int(minp)
    data['max_pressure'] = int(maxp)
    data['min_humidity'] = int(minh)
    data['max_humidity'] = int(maxh)
    data['pallet'] = int(pallet)
    data['shippment_to_name'] = receiverName
    data['shippment_to_phone'] = receiverNumber
    data['device_serial'] = deviceserial
    data['user_email'] = userEmail
    data['load_number'] = loadNumber
    data['pickup_location'] = ssaddress
    data['dropoff_location'] = sraddress
    data['shipment_start_time'] = ssdate
    data['estimated_dropoff_time'] = sddate
    data['required_dropoff_time'] = rdate
    sendingData(accountDetails, data, filepath, fileName)


def sendingData(accountDetails, data, filepath, fileName):
    url = "http://35.167.129.201:8081/load/companyloadnumbers"
      
    payload = json.dumps(data)
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer "+ generatingToken(),
        'cache-control': "no-cache",
    
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    python_dict =  json.loads(response.text)
    print(python_dict)
    if (python_dict.get("status", "empty") == "Success"):
        movingCurrentInputFile(filepath, fileName, "sucessful")
        creatingDirectories(filepath, "notSucessful")
        outputFile(fileName,accountDetails, "A")
    else:
        movingCurrentInputFile(filepath, fileName, "notSucessful")
        creatingDirectories(filepath, "sucessful")
        outputFile(fileName, accountDetails, "R")


def movingCurrentInputFile(filePath, fileName, directoryName):
    inputDirectory = filePath+"/"+directoryName
    if directoryName in ftp.nlst(filePath):
        ftp.rename(filePath+"/"+fileName+".edi", inputDirectory + "/"+fileName+".edi")
    else:
        ftp.mkd(inputDirectory)
        ftp.rename(filePath+"/"+fileName+".edi", inputDirectory + "/"+fileName+".edi")


def creatingDirectories(filePath, directoryName):
    inputDirectory = filePath+"/"+directoryName
    if not directoryName in ftp.nlst(filePath):
        ftp.mkd(inputDirectory)


def outputFile(filename, account, status):
    ftp_out = ftplib.FTP(account.get("ip_hostOut"),account.get("user_nameOut"), account.get("passwordOut"))
    ftp_out.cwd(account.get("output_path"))
    outputMessage = """ISA*01*0000000000*01*0000000000*ZZ*ABCDEFGHIJKLMNO*ZZ*123456789012345*101127*1719*U*00400*000003438*0*P*>
    GS*GF*4405197800*999999999*20111219*1742*000000003*X*004010
    ST*990*000000003
    B1*XXXX*9999919860*20111218*"""+ status + """
    N9*CN*9999919860
    SE*4*000000003
    GE*1*000000003
    IEA*1*000000003"""
    output = io.BytesIO(str.encode(outputMessage))
    ftp_out.storbinary('STOR ' + filename+".edi", output)
    print("output stored !")

def generatingToken():
    # It is used to authenticate the user/company and returns the request status.
    url = "https://api.coldwhere.com/oauth/token"
    username= "ftp@coldwhere.com"
    password = "3tpfkLEZCobJgOJP9O96"
    payload = "grant_type=password&username=" + username + "&password=" + password + "&client_id=spring-security-oauth2-read-write-client&undefined="
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Authorization': "Basic c3ByaW5nLXNlY3VyaXR5LW9hdXRoMi1yZWFkLXdyaXRlLWNsaWVudDpzcHJpbmctc2VjdXJpdHktb2F1dGgyLXJlYWQtd3JpdGUtY2xpZW50LXBhc3N3b3JkMTIzNA==",
        'cache-control': "no-cache",
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    return  python_dict.get("access_token", "empty")
    