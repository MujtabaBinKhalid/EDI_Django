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


def fetchingCompaniesAndLoads(ip_address, port_number, bufferSize, messageType, jsonKey, jsonValue):
    data = {}
    TCP_IP = ip_address
    TCP_PORT = port_number
    BUFFER_SIZE = bufferSize
    data['message_type'] = messageType
    data[jsonKey] = jsonValue
    json_data = json.dumps(data)
    MESSAGE = json_data
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((TCP_IP, TCP_PORT))
    tcp_socket.sendto(MESSAGE.encode(), (TCP_IP, TCP_PORT))
    data = tcp_socket.recv(BUFFER_SIZE)
    tcp_socket.close()
    responseInstring = data.decode("utf-8")
    json_acceptable_string = responseInstring.replace("'", "\"")
    dictionary = json.loads(json_acceptable_string)
    return dictionary["details"]


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


def company_files(out_queue, accountDetail, folder):
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
    except Exception as e:
        request.session[folder] = "0"


def index(request):
    # """ Index page, after login """

    if request.method == "GET":
        # try:
        if (request.session['userStatus'] == "login_company"):
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
        elif(request.session['userStatus'] == "login_user"):

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
        # except Exception as e:
        #     return render(request, 'Login/index.html')


def accountCreation(request):
    if request.is_ajax() or request.method == 'POST':
        if(request.session['userStatus'] == "login_company"):
            edi_account = accountRegistration.objects.create(ipHost=request.POST['iphost'], userName=request.POST['username'],
                                                             password=request.POST['password'], input_path=request.POST['inputpath'],
                                                             output_path=request.POST['outputpath'], ip_hostOut=request.POST['iphostOut'],
                                                             passwordOut=request.POST['passwordOut'],  user_nameOut=request.POST['usernameOut'],
                                                             email=request.session['name'])
            edi_account.save()
        elif(request.session['userStatus'] == "login_user"):
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
            if (request.session['userStatus'] == "login_company"):
                return render(request, 'main/edi_registration.html', {'cookie_email':  request.COOKIES.get('user_email')})
            elif(request.session['userStatus'] == "login_user"):
                 # IP AND THE EMAIL ADDRESS WILL BE CHANGED LATER. IT HAS BEEN USED
                 # AS THE LAT-LONG API GIVE  RESULT ON THE PRODUCTION API LIST.
                dropdown_data = fetchingCompaniesAndLoads('34.213.95.106', 9991, 1024, 'get_all_companies_names',
                                                          'email', 'hassan.farrukh@casadetech.com')
                return render(request, 'main/edi_registration_SuperUser.html', {"dropdown": dropdown_data})

        except Exception as e:
            return render(request, 'Login/index.html')


def activeLoads(request):
      # fetching loads of the logged in
    if request.session['userStatus'] == "login_company":
        if request.is_ajax() or request.method == 'POST' and request.session['userStatus'] == "login_company":
                # return HttpResponse(request.session['name'])
            dropdown_data = fetchingCompaniesAndLoads('35.161.234.96', 9991, 1024, 'get_company_current_load_numbers',
                                                      'company_email', request.session['name'])

            return JsonResponse({'dropdown': dropdown_data})


def statusReport(request):
    # fetching loads of a company .
    if request.is_ajax() or request.method == 'POST' and request.session['userStatus'] == "login_company":
        dropdown_data = fetchingCompaniesAndLoads('34.213.95.106', 9991, 1024, 'get_company_current_load_numbers',
                                                  'company_email', request.POST['company_email'])
        request.session['company_email'] = request.POST['company_email']
        return JsonResponse({'dropdown': dropdown_data})
    elif request.method == "GET":
        dropdown_data = fetchingCompaniesAndLoads('34.213.95.106', 9991, 1024, 'get_all_companies_names',
                                                  'email', 'hassan.farrukh@casadetech.com')
        return render(request, 'main/allStatusReports.html', {"dropdown": dropdown_data})


def generatingReport(request):
    result = fetchingLatLong(request)
    output = creatingOutputFile(ftp_companyLogin, request, result.get('location_lat'),
                                result.get('location_long'),  str(request.POST['file_name']))
    # return HttpResponse(ftp_companyLogin.getwelcome())
    return HttpResponse(output)


def establishingConnection(request):
    global ftp_companyLogin, accountDetail
    if(request.session['userStatus'] == "login_user"):
        try:
            accountDetail = accountRegistration.objects.get(email=request.session['company_email'])
            if accountDetail:
                ftp_companyLogin = ftplib.FTP(
                    accountDetail.ipHost, accountDetail.userName, accountDetail.password)
                return JsonResponse({'result': "its connected !"})
        except Exception as e:
            ftp_companyLogin = "No Ftp Account is associated with it."
    elif(request.session['userStatus'] == "login_company"):
        try:
            accountDetail = accountRegistration.objects.get(email=request.session['name'])
            if accountDetail:
                ftp_companyLogin = ftplib.FTP(
                    accountDetail.ipHost, accountDetail.userName, accountDetail.password)
                return JsonResponse({'result': "its connected !"})
        except Exception as e:
            ftp_companyLogin = "No Ftp Account is associated with it."


def fetchingLatLong(request):
    TCP_IP = "34.213.95.106"
    TCP_PORT = 9991
    BUFFER_SIZE = 1024
    data = {}
    data['message_type'] = 'current_load_info'
    data['id_device_load_record'] = str(request.POST['device_record'])
    json_data = json.dumps(data)
    MESSAGE = json_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.sendto(MESSAGE.encode(), (TCP_IP, TCP_PORT))
    data = s.recv(BUFFER_SIZE)
    s.close()
    responseInstring = data.decode("utf-8")
    json_acceptable_string = responseInstring.replace("'", "\"")
    dictionary = json.loads(json_acceptable_string)
    if (dictionary['status'] == "Success"):
        lat = (dictionary["details"].get('location_lat'))
        long = (dictionary["details"].get('location_long'))
        return dictionary['details']
    else:
        return (dictionary['status'])


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
        #
        thread_decrypted_files = threading.Thread(
            target=company_files, args=(input_queue, accountDetail, "output"))

        thread_sucessful_files = threading.Thread(
            target=company_files, args=(input_queue, accountDetail,  "sucessful"))

        thread_un_sucessful_files = threading.Thread(
            target=company_files, args=(input_queue, accountDetail,  "notSucessful"))

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
