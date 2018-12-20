from django.shortcuts import render
import json
import io
import ftplib
from django.shortcuts import render
from io import BytesIO
import requests

       
def statusReports(): 
    print ("Pikabuu")
    try:
        url = "http://54.245.173.223:3000/account/"
        payload = ""
        headers = {
            'cache-control': "no-cache",
            }
        response = requests.request("GET", url, data=payload, headers=headers)
        accounts =  json.loads(response.text)
        for account in range(len(accounts.get("data", "empty"))):
            global host, ftp, statusInputPath, statusOutputPath
            ftp = ftplib.FTP((accounts.get("data", "empty"))[account].get ("ipHost"),
            (accounts.get("data", "empty"))[account].get ("userName"), 
            (accounts.get("data", "empty"))[account].get ("password"))
            print("translating files of account ")
            paths = fetchingPaths ((accounts.get("data", "empty"))[account].get ("email"))
            if not (is_empty(paths)):
                statusInputPath = paths.get("input_path")
                statusOutputPath = paths.get("output_path")
                print (statusInputPath)
                print (statusOutputPath)
                byteReading = BytesIO()

                files = []
                files = ftp.nlst(statusInputPath)
                print(files)
                files.remove(".")
                files.remove("..")
                for file_name in files:
                    if(file_name.split('.')[1] == "edi"):
                        fileName = file_name.split('.')[0]
                        filepath = statusInputPath+"/"+file_name
                        ftp.retrbinary('RETR ' + filepath, byteReading.write)
                        readingFile = byteReading.getvalue().decode("utf-8")
                        print (readingFile)
                        readingCurrentFile((accounts.get("data", "empty"))[account], readingFile, statusInputPath, fileName)
            else:
                pass    
    except requests.exceptions.ConnectionError:
        print ("Connection refused")
def readingCurrentFile(accountDetails, readingFile, filepath, fileName):
    try: 
        id_device_load_record = readingFile.split('*')[2].split(":")[1]
        print (id_device_load_record)
        result = fetchingLatLong(id_device_load_record)
        print (result.get('location_lat'))
        print (statusOutputPath)
        outputFile(fileName, accountDetails, result.get('location_lat'), result.get('location_long') )

    except Exception as e:   
        pass 
    

def fetchingLatLong(id_device_load_record): 
    url = "http://35.167.129.201:8081/load/currentlocationinfo"
    data = {'id_device_load_record': id_device_load_record}
    print (generatingToken())
    print ("generatingToken")
    payload = json.dumps(data)
    headers = {
    'Content-Type': "application/json",
    'Authorization': "Bearer "+ generatingToken(),
    }   
    response = requests.request("POST", url, data=payload, headers=headers)
    print ("generatingToken======")
    print (response.text)
    python_dict =  json.loads(response.text)
    
    return python_dict.get("details", "empty")
    
def outputFile(filename,account,lat,longitude):
    ftp_out = ftplib.FTP(account.get("ip_hostOut"),account.get("user_nameOut"), account.get("passwordOut"))
    ftp_out.cwd(statusOutputPath)
    stautusMessage = """ISA*00* *00* *02*SCAC *02*RBINTEST
    *100819*1851*U*00401*100110046*0*P*:
    GS*QM*SCAC*RBINTEST*20100819*1851*214060250*X*004010
    ST*214*0001
    B10*3766*9924017*SCAC
    MS1***""" + lat + "-"+longitude+ """
    *SE*10*0002
    GE*2*214060250
    IEA*1*100110046"""
    output = io.BytesIO(str.encode(stautusMessage))
    ftp_out.storbinary('STOR ' + filename+".edi", output)
    print("output stored !")
   
def generatingToken():
    # It is used to authenticate the user/company and returns the request status.
    url = "http://35.167.129.201:8081/oauth/token"
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
    
def fetchingPaths(email):
    url = "http://localhost:3000/status/fetchingPath"    
    data = {'email':email}
    payload = json.dumps(data)
    headers = {
        'Content-Type': "application/json",
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    data = python_dict.get("data")
    return data 
    
def is_empty(any_structure):
    if any_structure:
        print('Structure is not empty.')
        return False
    else:
        print('Structure is empty.')
        return True