from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from main.models import accountRegistration
import threading
import queue
import ftplib
import time
import json
import socket
import io
import requests
import json


# it is used to fetch all the companies on the reqyuest of the super admin .
def fetchingCompanies(request):
    url = "https://api.coldwhere.com/company/allcompanies"

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

    url = "https://api.coldwhere.com/load/companyloadnumbers"

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

    active_connections = accountRegistration.objects.count()
    request.session[session_name] = active_connections


def ConnectedConnections(request, session_name,  accounts):

    connected_connections = 0
    for account in accounts:
        try:
            ftp = ftplib.FTP(account.ipHost, account.userName, account.password)
            if (is_connected):
                connected_connections += 1
        except Exception as e:
            pass
    request.session[session_name] = connected_connections


def decryptedFiles(request, session_name,  accounts):

    decrypted_files = []
    decrypted_files_number = 0
    for account in accounts:
        ftp = ftplib.FTP(account.ipHost, account.userName, account.password)
        folderpath = account.output_path
        decrypted_files = ftp.nlst(folderpath)
        decrypted_files_number = decrypted_files_number + len(decrypted_files)
    request.session[session_name] = decrypted_files_number


def sucessfulFiles(request, session_name,  accounts):

    sucessful_files = []
    sucessful_files_number = 0
    accounts = accountRegistration.objects.all()
    for account in accounts:
        ftp = ftplib.FTP(account.ipHost, account.userName, account.password)
        folderpath = account.input_path + "/sucessful"
        sucessful_files = ftp.nlst(folderpath)
        sucessful_files_number = sucessful_files_number + len(sucessful_files)
    request.session[session_name] = sucessful_files_number


def company_FtpAccounts(request, session_name, accountDetail):
    try:
        if(accountDetail.ipHost == accountDetail.ip_hostOut):
            request.session[session_name] = "1"
        elif(accountDetail.ipHost != accountDetail.ip_hostOut):
            request.session[session_name] = "2"
    except Exception as e:
        request.session[session_name] = "0"

# def companySucessfulFiles (request, accountDetail):
#     try:
#         ftp = ftplib.FTP(accountDetail.ipHost, accountDetail.userName,
#                          accountDetail.password)

     
#         folderpath = accountDetail.input_path + "/sucessful"
        

#         files = ftp.nlst(folderpath)
#         request.session["sucessful"] = len(files)
#         return  request.session["sucessful"]

       
#     except Exception as e:
#         request.session["sucessful"] = "0"   
#         return  HttpResponse(request.session["sucessful"]) 


def company_files(request, accountDetail, folder):
    try:
        ftp = ftplib.FTP(accountDetail.ipHost, accountDetail.userName,
                         accountDetail.password)

        if (folder == "output"):
            folderpath = accountDetail.output_path
        elif (folder == "sucessful"):
            folderpath = accountDetail.input_path + "/sucessful"
        elif (folder == "notSucessful"):
            folderpath = accountDetail.input_path + "/notSucessful"

        files = ftp.nlst(folderpath)
        request.session[folder] = len(files)
        output_files = []
        for file in files:
            output_files.append(file)

        request.session["output_files"] = output_files
        request.session["ftp_username"] = accountDetail.userName
        request.session["output_path"] = accountDetail.output_path
    except Exception as e:
        request.session[folder] = "0"

def fetchingStatus(request):
    url = "https://api.coldwhere.com/user/me"

    payload = ""
    headers = {
        'Authorization': "Bearer "+request.session['token'],
        'cache-control': "no-cache",
        
        }

    response = requests.request("GET", url, data=payload, headers=headers)
    python_dict =  json.loads(response.text)
    if (python_dict.get("status", "empty") == "Success"):
        return (python_dict.get("details", "empty").get("role"))
    else:
        return ("INVALID CREDENTIALS")
	


def index(request):
    # """ Index page, after login """

    if request.method == "GET":

        request.session['role'] = fetchingStatus(request)
    #  try:
        if (request.session['role'] == "company"):
           
            response = fetchingCompanyTilesData(request)
            

            if (response == "noerror"):
                comapny_tiles_data = {
                    "ftp_accounts": request.session["ftpAccounts"],
                    "decrypted_files": request.session["output"],
                    # "sucessful_files": request.session["sucessful"],
                    "sucessful_files": "0",
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
            if (response == "noerror"):
                tiles_data = {
                    "alive_connections": request.session["activeConnection"],
                    "connected_connections": request.session["connectedConnection"],
                    "decrypted_files": request.session["decryptedFiles"],
                    "sucessful_files": request.session["sucessfulFiles"],
                    "accounts_detail": accountRegistration.objects.all(),
                    "accounts_count": accountRegistration.objects.count()
                }
            elif(response == "error"):
                tiles_data = {
                    "alive_connections": "0",
                    "connected_connections": "0",
                    "decrypted_files": "0",
                    "sucessful_files": "0",
                    "accounts_detail": null,
                    "accounts_count": accountRegistration.objects.count()
                }

            return render(request, 'main/edi_index.html', {'tiles_data':  tiles_data})
    #  except Exception as e:
         
    #     return render(request, 'Login/index.html')
   

def accountCreation(request):
    if request.is_ajax() or request.method == 'POST':
        if(request.session['role'] == "company"):
            edi_account = accountRegistration.objects.create(ipHost=request.POST['iphost'], userName=request.POST['username'],
                                                             password=request.POST['password'], input_path=request.POST['inputpath'],
                                                             output_path=request.POST['outputpath'], ip_hostOut=request.POST['iphostOut'],
                                                             passwordOut=request.POST['passwordOut'],  user_nameOut=request.POST['usernameOut'],
                                                             email=request.session['name'])
            edi_account.save()
        elif(request.session['role'] == "super_admin"):
            edi_account = accountRegistration.objects.create(ipHost=request.POST['iphost'], userName=request.POST['username'],
                                                             password=request.POST['password'], input_path=request.POST['inputpath'],
                                                             output_path=request.POST['outputpath'], ip_hostOut=request.POST['iphostOut'],
                                                             passwordOut=request.POST['passwordOut'],  user_nameOut=request.POST['usernameOut'],
                                                             email=request.POST['email'])
            edi_account.save()

        return HttpResponse(request.POST['passwordOut'])
    elif request.method == "GET":
        try:
            sessionData = request.session['name']
            if (request.session['role'] == "company"):
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
    if request.session['role'] == "company":
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
    # output = creatingOutputFile(ftp_companyLogin, request, result.get('location_lat'),
    #                             result.get('location_long'),  str(request.POST['file_name']))
    # # return HttpResponse(ftp_companyLogin.getwelcome())
    return HttpResponse(result)


def establishingConnection(request):
                                                   
    global ftp_companyLogin, accountDetail
    if(request.session['role'] == "super_admin"):
        try:
            accountDetail = accountRegistration.objects.get(email=request.session['company_email'])
            if accountDetail:
                ftp_companyLogin = ftplib.FTP(
                    accountDetail.ipHost, accountDetail.userName, accountDetail.password)
                return JsonResponse({'result': "its connected !"})
        except Exception as e:
            ftp_companyLogin = "No Ftp Account is associated with it."
    elif(request.session['role'] == "company"):
        try:
            accountDetail = accountRegistration.objects.get(email=request.session['name'])
            if accountDetail:
                ftp_companyLogin = ftplib.FTP(
                    accountDetail.ipHost, accountDetail.userName, accountDetail.password)
                return JsonResponse({'result': "its connected !"})
        except Exception as e:
            ftp_companyLogin = "No Ftp Account is associated with it."
            return HttpResponse(ftp_companyLogin)


def fetchingLatLong(request):

    data = {'id_device_load_record': request.POST['device_record'] }

    payload = json.dumps(data)
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer "+request.session['token'],
        'cache-control': "no-cache",
       
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    if (python_dict.get("status", "empty") == "Success"):
        python_dict =  json.loads(response.text)
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
        accounts = accountRegistration.objects.all()
        thread_activeConnection = threading.Thread(
            target=activeConnections, args=(request, "activeConnection"))
        thread_connectedConnection = threading.Thread(
            target=ConnectedConnections, args=(request, "connectedConnection", accounts))

        thread_decryptedfiles = threading.Thread(
            target=decryptedFiles, args=(request, "decryptedFiles", accounts,))
        thread_sucessfulfiles = threading.Thread(
            target=sucessfulFiles, args=(request, "sucessfulFiles", accounts,))

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


def fetchingCompanyTilesData(request):
    try:
        accountDetail = accountRegistration.objects.get(email=request.session['name'])
        
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


def creatingOutputFile(ftp_companyLogin, request, lat, long, filename):
    # ftp_companyLogin.cwd(request.POST['file_path'])
    stautusMessage = """ISA*00* *00* *02*SCAC *02*RBINTEST
        *100819*1851*U*00401*100110046*0*P*:
        GS*QM*SCAC*RBINTEST*20100819*1851*214060250*X*004010
        ST*214*0001
        B10*3766*9924017*SCAC
        MS1***""" + "lat"+" " + "long" + """*
        SE*10*0002
        GE*2*214060250
        IEA*1*100110046"""
    output = io.BytesIO(str.encode(stautusMessage))
    ftp_companyLogin.storbinary('STOR ' + filename + ".edi", output)
    return ftp_companyLogin.getwelcome()
