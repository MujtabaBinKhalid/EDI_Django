from django.shortcuts import render
import json
import io
import ftplib
from django.shortcuts import render
from io import BytesIO
import requests

       
def viewLoads(): 
    print ("Pikabuu-2")
    try:
        url = "http://54.245.173.223:3000/account/"
        payload = ""
        headers = {
            'cache-control': "no-cache",
            }
        response = requests.request("GET", url, data=payload, headers=headers)
        accounts =  json.loads(response.text)
        for account in range(len(accounts.get("data", "empty"))):
            global host, ftp, loadOutputPath
            ftp = ftplib.FTP((accounts.get("data", "empty"))[account].get ("ipHost"),
            (accounts.get("data", "empty"))[account].get ("userName"), 
            (accounts.get("data", "empty"))[account].get ("password"))
            paths = fetchingPaths ((accounts.get("data", "empty"))[account].get ("email"))
            if not (is_empty(paths)):
                loadOutputPath = paths.get("output_path") 
                fetchingAllLoads((accounts.get("data", "empty"))[account])           
            else:
                pass    
    except Exception as e:   
        print ("Connection refused")
def fetchingAllLoads(account):
    print ("fetchingAllLoads")
    print (account.get("email"))
    print ("Printing after account")

    try:
        print ("its coming in TRY")   
        url = "http://35.167.129.201:8081/load/companyloadnumbers"
        allloads =  ""
        data = {'company_email': account.get("email")}
        payload = json.dumps(data)
        print (generatingToken())
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Bearer "+ generatingToken(),
            }

        print ("R U HERE? ****")    
        response = requests.request("POST", url, data=payload, headers=headers)
        print ("R U HERE?")
        print (response.text)
        python_dict =  json.loads(response.text)
        print ("R U HERE? ______" )
        # print (response)
        for i in range(len(python_dict.get("details", "empty"))):
                allloads += """AT7~X6~T1~~~""" + (python_dict.get("details", "empty"))[i].get ("id_device_load_record") +"""~""" + (python_dict.get("details", "empty"))[i].get ("load_number")+ """~LT \n""" 
	
        outputFile (account , allloads)    
    except Exception as e:   
        print ("its coming in EXCEPT")
        pass 
    
 
def outputFile(account,allloads):
    try:
        head = """ST~240~000161510
BGN~00~QVD~20180305
LX~1
L11~1Z059WX20355823320~2I~A4
LS~2710
MAN~CP~DS~~CP~NA
L11~4500155536AA~CR~SHPREF1/
L11~75163~CR~SHPREF2/ """

        tail = """CD3~~~~~CG \n LE~2710 \n SE~21~000161510 """
        all_loads = head + allloads +tail          
        ftp_out = ftplib.FTP(account.get("ip_hostOut"),account.get("user_nameOut"), account.get("passwordOut"))
        ftp_out.cwd(loadOutputPath)
        output = io.BytesIO(str.encode(all_loads))
        ftp_out.storbinary('STOR ' + "allLoads"+".edi", output)
        print("output stored LOADS !")
    except Exception as e:   
        print("Error !")
    
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
    url = "http://54.245.173.223:3000/load/fetchingPath"    
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