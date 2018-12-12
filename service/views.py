import json
import socket
import io
import ftplib
from django.shortcuts import render
from main.models import accountRegistration
from background_task import background
from io import BytesIO


@background(schedule=300)
def tcpRequest():
    accounts = accountRegistration.objects.all()
    for account in accounts:
        # print("translating files of account " + account.ipHost)
        global host, ftp
        byteReading = BytesIO()

        ftp = ftplib.FTP(account.ipHost, account.userName, account.password)

        files = []
        innerDirectory = account.input_path
        files = ftp.nlst(innerDirectory)
        print(files)
        files.remove(".")
        files.remove("..")
        print("file array Ready!")
        for file in files:
            if (file == "notSucessful"):
                files.remove("notSucessful")

            elif (file == "sucessful"):
                files.remove("sucessful")

            elif(file.split('.')[1] == "edi"):
                fileName = file.split('.')[0]
                filepath = innerDirectory+"/"+file
                ftp.retrbinary('RETR ' + filepath, byteReading.write)
                readingFile = byteReading.getvalue().decode("utf-8")
                #readingCurrentFile(account, readingFile, innerDirectory, fileName)


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
    url = "https://api.coldwhere.com/load/companyloadnumbers"
    payload = json.dumps(data)
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer "+request.session['token'],
        'cache-control': "no-cache",
    
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    python_dict =  json.loads(response.text)
    if (python_dict.get("status", "empty") == "Success"):
        movingCurrentInputFile(filepath, fileName, "sucessful")
        creatingDirectories(filepath, "notSucessful")
        outputFile(fileName)
    else:
        movingCurrentInputFile(filepath, fileName, "notSucessful")
        creatingDirectories(filepath, "sucessful")
        outputFile(fileName, accountDetails)


def movingCurrentInputFile(filePath, fileName, directoryName):
    inputDirectory = filePath+"/"+directoryName
    if directoryName in ftp.nlst(filePath):
        ftp.rename(filePath+"/"+fileName+".edi", inputDirectory + "/"+fileName+".edi")
    else:
        ftp.mkd(inputDirectory)
        ftp.rename(filePath+"/"+fileName+".edi", inputDirectory + "/"+fileName+".edi")


def creatingDirectories(filePath, fileName, directoryName):
    inputDirectory = filePath+"/"+directoryName
    if not directoryName in ftp.nlst(filePath):
        ftp.mkd(inputDirectory)


def outputFile(filename, account):
    ftp_out = ftplib.FTP(account.ip_hostOut, account.user_nameOut, account.passwordOut)
    ftp_out.cwd(account.output_path)
    output = io.BytesIO(b"""ISA*01*0000000000*01*0000000000*ZZ*ABCDEFGHIJKLMNO*ZZ*123456789012345*101127*1719*U*00400*000003438*0*P*>
    GS*GF*4405197800*999999999*20111219*1742*000000003*X*004010
    ST*990*000000003
    B1*XXXX*9999919860*20111218*A
    N9*CN*9999919860
    SE*4*000000003
    GE*1*000000003
    IEA*1*000000003""")
    ftp_out.storbinary('STOR ' + filename+".edi", output)
    print("output stored !")
