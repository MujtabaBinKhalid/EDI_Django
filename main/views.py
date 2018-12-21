from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
import threading
import queue
import ftplib
import time
import json
import socket
import io
import requests
import json
from service.views import tcpRequest
from statusService.views import statusReports
from viewLoads.views import viewLoads
from background_task import background


@background(schedule=3)
def startingThreads():
    print ("inside here")
    thread_loadService = threading.Thread(
            target=loadServices)
    thread_statusSerivce = threading.Thread(
            target=statusSerivces)
    thread_viewLoad = threading.Thread(
            target=viewAllLoads)

    
    thread_loadService.start()
    thread_statusSerivce.start()
    thread_viewLoad.start()
    
    thread_loadService.join()
    thread_viewLoad.join()
    thread_statusSerivce.join()
    
def loadServices():
    tcpRequest()

def statusSerivces():
    statusReports()

def viewAllLoads():
    viewLoads()

# it is used to fetch all the companies on the reqyuest of the super admin .

def countingAccounts(request):
    url = "http://54.245.173.223:3000/account/countingCompanies"
    payload = ""
    headers = {
        'cache-control': "no-cache",
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    return python_dict.get("dataCount", "empty")


def accountDetails(request):
  
    url = "http://54.245.173.223:3000/account/"

    payload = ""
    headers = {
        'cache-control': "no-cache",
        }

    response = requests.request("GET", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    return python_dict.get("data", "empty")     
    

def fetchingCompanies(request):
    url = "http://35.167.129.201:8081/company/allcompanies"

    payload = ""
    headers = {
        'Authorization': "Bearer "+request.session['token'],
        'cache-control': "no-cache",
        'Content-Type': "application/json",
        
        }

    response = requests.request("GET", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    
    if (python_dict.get("status", "empty") == "Success"):
        return python_dict.get("details", "empty")
		
	
    # it is used to fetch the loads of a specfic company
def fetchingLoads(request , companyEmail):

    url = "http://35.167.129.201:8081/load/companyloadnumbers"

    data = {'company_email': companyEmail }
    payload = json.dumps(data)
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer "+request.session['token'],
        'cache-control': "no-cache",
        
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    python_dict =  json.loads(response.text)


    if (python_dict.get("status", "empty") == "Success"):
        return python_dict.get("details", "empty")
     
	
def activeConnections(request, session_name):
    url = "http://54.245.173.223:3000/account/countingCompanies"
    payload = ""
    headers = {
        'cache-control': "no-cache",
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    request.session[session_name] = python_dict.get("dataCount", "empty")

    

def ConnectedConnections(request, session_name,  accounts):

    connected_connections = 0
    for i in range(len(accounts.get("data", "empty"))):
        try:
            ftp = ftplib.FTP((accounts.get("data", "empty"))[i].get ("ipHost"),
            (accounts.get("data", "empty"))[i].get ("userName"), 
            (accounts.get("data", "empty"))[i].get ("password"))
            if  (is_connected):
                connected_connections += 1
        except Exception as e:
            pass
    request.session[session_name] = connected_connections


def decryptedFiles(request, session_name,  accounts):
    decrypted_files_number = 0
    for i in range(len(accounts.get("data", "empty"))):
        ftp = ftplib.FTP((accounts.get("data", "empty"))[i].get ("ipHost"),
        (accounts.get("data", "empty"))[i].get ("userName"), 
        (accounts.get("data", "empty"))[i].get ("password"))

        folderpath = (accounts.get("data", "empty"))[i].get ("output_path")
        files = checkingDirectory(ftp, folderpath)
        # decrypted_files = ftp.nlst(folderpath)
        # decrypted_files.remove(".")
        # decrypted_files.remove("..")
        decrypted_files_number = decrypted_files_number + files
    request.session[session_name] = decrypted_files_number 


def sucessfulFiles(request, session_name,  accounts):
    sucessful_files_number = 0
    try:
        for i in range(len(accounts.get("data", "empty"))):
            ftp = ftplib.FTP((accounts.get("data", "empty"))[i].get ("ipHost"),
            (accounts.get("data", "empty"))[i].get ("userName"), 
            (accounts.get("data", "empty"))[i].get ("password"))     
            folderpath = (accounts.get("data", "empty"))[i].get ("input_path") + "/sucessful"
            files = checkingDirectory(ftp, folderpath)
            sucessful_files_number = sucessful_files_number + files
        request.session[session_name] = sucessful_files_number 
    except Exception as e:
        request.session[session_name] = "0"
    
def checkingDirectory(ftp,folderpath):

    files = []
    try:
        files = ftp.nlst(folderpath)
        files.remove(".")
        files.remove("..")
        return len(files)      
    except Exception as e:
        return 0
    
def company_FtpAccounts(request, session_name, accountDetail):
    try:
        if(accountDetail.get("ipHost", "empty") == accountDetail.get("ip_hostOut", "empty")):
            request.session[session_name] = "1"
        elif(accountDetail.get("ipHost", "empty") != accountDetail.get("ip_hostOut", "empty")):
            request.session[session_name] = "2"
    except Exception as e:
        request.session[session_name] = "0"


def company_files(request, accountDetail, folder):
    try:
        ftp = ftplib.FTP(accountDetail.get("ipHost", "empty"), accountDetail.get("userName", "empty"),
                         accountDetail.get("password", "empty"))

        if (folder == "output"):
            folderpath = accountDetail.get("output_path", "empty")
        elif (folder == "sucessful"):
            folderpath = accountDetail.get("input_path", "empty") + "/sucessful"
        elif (folder == "notSucessful"):
            folderpath = accountDetail.get("input_path", "empty") + "/notSucessful"

        files = ftp.nlst(folderpath)
        files.remove(".")
        files.remove("..")
        request.session[folder] = len(files) 
        output_files = []
        for file in files:
            output_files.append(file)

        request.session["output_files"] = output_files
        request.session["ftp_username"] = accountDetail.get("userName", "empty")
        request.session["output_path"] = accountDetail.get("output_path", "empty")
    except Exception as e:
        request.session[folder] = "0"

def fetchingStatus(request):
    url = "http://35.167.129.201:8081/user/me"

    payload = ""
    headers = {
        'Authorization': "Bearer "+request.session['token'],
        'cache-control': "no-cache",
        
        }

    response = requests.request("GET", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    if (python_dict.get("status", "empty") == "Success"):
        if(python_dict.get("details", "empty").get("role") == "user"):
            request.session['name'] = python_dict.get("details", "empty").get("company_email")
        
        return (python_dict.get("details", "empty").get("role"))
    else:
        return ("INVALID CREDENTIALS")
	


def index(request):
    # """ Index page, after login """

    if request.method == "GET":
      try:   
        request.session['role'] = fetchingStatus(request)
    
        if ((request.session['role'] == "company") or ((request.session['role'] == "user"))):
           
            response = fetchingCompanyTilesData(request)
            if (response == "noerror"):
                comapny_tiles_data = {
                    "ftp_accounts": request.session["ftpAccounts"],
                    "decrypted_files": request.session["output"],
                    "sucessful_files": request.session["sucessful"],
                    "unSucessful_files": request.session["notSucessful"],
                }
            elif(response == "error"):
                comapny_tiles_data = {
                    "ftp_accounts": "0",
                    "decrypted_files": "0",
                    "sucessful_files": "0",
                    "unSucessful_files": "0",
                }

            return render(request, 'main/edi_indexCompany.html', {'tiles_data':  comapny_tiles_data})
        elif(request.session['role'] == "super_admin"):
             
            response = fetchingUserTilesData(request)
            dropdown_data = fetchingCompanies(request)
            
            if (response == "noerror"):
                tiles_data = {
                    "alive_connections": request.session["activeConnection"],
                    "connected_connections": request.session["connectedConnection"],
                    "decrypted_files": request.session["decryptedFiles"],
                    "sucessful_files": request.session["sucessful_files"],
                    "accounts_detail": accountDetails(request),
                    "accounts_count":  countingAccounts(request)
                  
                   
                }
            elif(response == "error"):
                tiles_data = {
                    "alive_connections": "0",
                    "connected_connections": "0",
                    "decrypted_files": "0",
                    "sucessful_files": "0",
                    "accounts_detail": null,
                    "accounts_count": countingAccounts(request)
                }

            return render(request, 'main/edi_index.html', {'tiles_data':  tiles_data , "dropdown": dropdown_data})
      except Exception as e:
            return render(request, 'Login/index.html')
   



def accountCreation(request):
    
    if request.is_ajax() or request.method == 'POST':
        url = "http://54.245.173.223:3000/account/"
        headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache",
        }

        if ((request.session['role'] == "company") or ((request.session['role'] == "user"))):
            data = {"ipHost": request.POST['iphost'],"userName":request.POST['username'],"password":request.POST['password'],"email":request.session['name'],
            "input_path":request.POST['inputpath'],"output_path":request.POST['outputpath'],
            "ip_hostOut": request.POST['iphostOut'],
            "user_nameOut":request.POST['usernameOut'],"passwordOut": request.POST['passwordOut']}

         
        elif(request.session['role'] == "super_admin"):
            data = {"ipHost": request.POST['iphost'],"userName":request.POST['username'],"password":request.POST['password'],"email":request.POST['email'],
            "input_path":request.POST['inputpath'],"output_path":request.POST['outputpath'],
            "ip_hostOut": request.POST['iphostOut'],
            "user_nameOut":request.POST['usernameOut'],"passwordOut": request.POST['passwordOut']}

        
        payload = json.dumps(data)
        response = requests.request("POST", url, data=payload, headers=headers)
        python_dict =  json.loads(response.text)
        return HttpResponse(python_dict.get("status", "empty"))
               
        
    elif request.method == "GET":
        try:
            sessionData = request.session['name']
            if ((request.session['role'] == "company") or ((request.session['role'] == "user"))):
                return render(request, 'main/edi_registration.html', {'cookie_email':  request.COOKIES.get('user_email')})
            elif(request.session['role'] == "super_admin"):
                 # IP AND THE EMAIL ADDRESS WILL BE CHANGED LATER. IT HAS BEEN USED
                 # AS THE LAT-LONG API GIVE  RESULT ON THE PRODUCTION API LIST.
                dropdown_data = fetchingCompanies(request)
                return render(request, 'main/edi_registration_SuperUser.html', {"dropdown": dropdown_data})

        except Exception as e:
            return render(request, 'Login/index.html')


def activeLoads(request):
      # fetching loads of the logged in
    if ((request.session['role'] == "company") or ((request.session['role'] == "user"))):
        if request.is_ajax() or request.method == 'POST' and request.session['role'] == "company":
            
            dropdown_data = fetchingLoads(request , request.session['name'])

            return JsonResponse({'dropdown': dropdown_data})


def statusReport(request):
    # fetching loads of a company .
    if request.is_ajax() or request.method == 'POST' and request.session['role'] == "super_admin":
        dropdown_data = fetchingLoads(request , request.POST['company_email'])
        request.session['company_email'] = request.POST['company_email']
        return JsonResponse({'dropdown': dropdown_data})
    elif request.method == "GET":
        dropdown_data = fetchingCompanies(request)
        return render(request, 'main/allStatusReports.html', {"dropdown": dropdown_data})


def generatingReport(request):
    result = fetchingLatLong(request) 
    output = creatingOutputFile(ftp_companyLogin, request, result.get('location_lat'),
                                 result.get('location_long'),  str(request.POST['file_name']))

    return HttpResponse(request.POST['device_record'])


def establishingConnection(request):
                                                   
    global ftp_companyLogin, accountDetail
    if(request.session['role'] == "super_admin"):
        try:
            accountDetail = fetchingAccountInfo(request, request.POST['email'])
            if accountDetail:
                ftp_companyLogin = ftplib.FTP(accountDetail.get("ipHost", "empty"), accountDetail.get("userName", "empty"),
                         accountDetail.get("password", "empty"))
                request.session['name'] = request.POST['email']    
                return JsonResponse({'result': "its connected jani !"})
        except Exception as e:
            ftp_companyLogin = "No Ftp Account is associated with it."
    elif ((request.session['role'] == "company") or ((request.session['role'] == "user"))):
        try:
            accountDetail = fetchingAccountInfo(request, request.session['name'])  
            if accountDetail:
                ftp_companyLogin = ftplib.FTP(accountDetail.get("ipHost", "empty"), accountDetail.get("userName", "empty"),
                         accountDetail.get("password", "empty"))
                return JsonResponse({'result': "its connected !"})
        except Exception as e:
            ftp_companyLogin = "No Ftp Account is associated with it."
            return HttpResponse("ftp_companyLogin")


def fetchingLatLong(request):
    url = "http://35.167.129.201:8081/load/minloadinfo"
    data = {'id_device_load_record': request.POST['device_record'] }
    
    payload = json.dumps(data)
   
    headers = {
    'Content-Type': "application/json",
    'Authorization': "Bearer "+request.session['token'] ,
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    if (python_dict.get("status", "empty") == "Success"):
        return python_dict.get("details", "empty")
    else: 
        return  python_dict.get("status", "empty")

   

def logout(request):
    """ It is used to make use logout of their accout."""
    del request.session['name']
    return render(request, 'Login/index.html')

def is_connected(ftp_conn):
    try:
        ftp_conn.retrlines('LIST')
    except (socket.timeout, OSError):
        return False
    return True




def fetchingUserTilesData(request):
    try: 
        url = "http://54.245.173.223:3000/account/"
        payload = ""
        headers = {
            'cache-control': "no-cache",
            }
        response = requests.request("GET", url, data=payload, headers=headers)
        accounts =  json.loads(response.text)  
        thread_activeConnection = threading.Thread(
            target=activeConnections, args=(request, "activeConnection"))
        thread_connectedConnection = threading.Thread(
            target=ConnectedConnections, args=(request, "connectedConnection", accounts))

        thread_decryptedfiles = threading.Thread(
            target=decryptedFiles, args=(request, "decryptedFiles", accounts,))
        thread_sucessfulfiles = threading.Thread(
            target=sucessfulFiles, args=(request, "sucessful_files", accounts,))

        thread_activeConnection.start()
        thread_connectedConnection.start()
        thread_decryptedfiles.start()
        thread_sucessfulfiles.start()

        thread_activeConnection.join()
        thread_connectedConnection.join()
        thread_decryptedfiles.join()
        thread_sucessfulfiles.join()
        return "noerror"
    except Exception as e:
        return "error"


def creatingStatusPaths(request):
    url = "http://54.245.173.223:3000/status/"
    data = {'email':request.session['name'],
     "input_path": request.POST['inputpath'], "output_path": request.POST['outputpath']}
    payload = json.dumps(data)
    headers = {
    'Content-Type': "application/json",
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    return HttpResponse(python_dict.get("status", "empty"))
   
def creatingLoadPaths(request):
    url = "http://54.245.173.223:3000/load/"
    data = {'email':request.session['name'],
     "output_path": request.POST['outputpath']}
    payload = json.dumps(data)
    headers = {
    'Content-Type': "application/json",
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    return HttpResponse(python_dict.get("status", "empty"))
    
def fetchingAccountInfo(request , name):
    url = "http://54.245.173.223:3000/account/fetchingCompany"
    data = {'email': name }
    payload = json.dumps(data)

    headers = {
    'Content-Type': "application/json",
    'cache-control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    accountDetail = python_dict.get("data", "empty")
    return accountDetail
        
def fetchingCompanyTilesData(request):
    try:
        accountDetail = fetchingAccountInfo(request, request.session['name'])
        thread_ftp_accounts = threading.Thread(
            target=company_FtpAccounts, args=(request, "ftpAccounts", accountDetail))

        thread_decrypted_files = threading.Thread(
            target=company_files, args=(request, accountDetail, "output"))

        thread_sucessful_files = threading.Thread(
            target=company_files, args=(request, accountDetail,  "sucessful"))

        thread_un_sucessful_files = threading.Thread(
            target=company_files, args=(request, accountDetail,  "notSucessful"))

        thread_ftp_accounts.start()
        thread_decrypted_files.start()
        thread_sucessful_files.start()
        thread_un_sucessful_files.start()

        thread_ftp_accounts.join()
        thread_decrypted_files.join()
        return "noerror"
    except Exception as e:
        return "error"


def creatingOutputFile(ftp_companyLogin, request, lat, longitude, filename):
    ftp_companyLogin.cwd(request.POST['file_path'])
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
    ftp_companyLogin.storbinary('STOR ' + filename + ".edi", output)
    return "output stored !"
    
