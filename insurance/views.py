from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from django.contrib import auth,messages
from django.core.files.storage import FileSystemStorage
# Create your views here.
import array as arr
from django.contrib import messages
import requests,json
import cx_Oracle
import datetime
## PDF CODE ###
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
import random
from django.contrib.auth.models import User
### Email ###
from django.conf import settings
from django.core.mail import send_mail



companyName=BranchInformationM.objects.all()[:1]


def loginV(request):
    return render(request,'pages/admin/login/logings.html',{'companyName':companyName})



def otpV(request):
    if request.method=='POST':
        name=request.POST.get('name')
        password=request.POST.get('password')
        user = auth.authenticate(username=name, password=password)
        if user is not None:
            # auth.login(request, user)
            users = UserProfileM.objects.filter(user=user.id).first()
            otps = str(random.randint(1000, 9999))
            users.otp = otps
            users.save()
            request.session['name']=name
            request.session['password']=password

            subject = 'OTP From Paramount Insurance'
            message = f'Hi {user.username}, thank you for Trying to Login. Your OTP number is {otps}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [users.Email ]
            send_mail(subject, message, email_from, recipient_list)
            return render(request,'pages/admin/login/otppages.html')
        messages.info(request, 'User is not valid')
    return redirect('login')

def finalloginV(request):
    name=request.session['name']
    password=request.session['password']
    otpf = request.POST.get('otps')
    user = auth.authenticate(username=name, password=password)
    users = UserProfileM.objects.filter(user=user.id).first()
    if otpf == users.otp:
        user = User.objects.get(id=users.user.id)
        auth.login(request, user)
        return redirect('/')
    else:
        messages.info(request, 'OTP NUMBER IS WRONG')
        return render(request,'pages/admin/login/otppages.html')




def logoutV(request):
    auth.logout(request)
    return redirect('/umpapi/login/')

@login_required(login_url='/umpapi/login/')
def index(request):
    userprofile = UserProfileM.objects.filter(id=request.user.id)
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    abc = cnx.cursor()
    abc.execute("""select count(*) as a from ump_mr where RESPONSE is null """)
    send = abc.fetchall()
    sended = cnx.cursor()
    sended.execute("""select count(*) as a from ump_mr where RESPONSE is not null """)
    previously = sended.fetchall()
    if request.user.is_superuser:
        chat = chatM.objects.all().order_by('-dates')
    else:
        chat=chatM.objects.filter(users=request.user).order_by('-dates')
    return render(request,'dashboard.html',{'companyName':companyName,'userprofile':userprofile,'send':send,'previously':previously,'chat':chat})

@login_required(login_url='/umpapi/login/')
def maindashboardV(request):
    userprofile = UserProfileM.objects.filter(id=request.user.id)
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    abc = cnx.cursor()
    abc.execute("""select count(*) as a from ump_mr where sendate is null and depositdate is null """)
    send = abc.fetchall()
    depo = cnx.cursor()
    depo.execute("""select count(*) as a from ump_mr where RESPONSE is null and depositdate is not null """)
    dep = depo.fetchall()
    sended = cnx.cursor()
    sended.execute("""select count(*) as a from ump_mr where RESPONSE is not null """)
    previously=sended.fetchall()
    return render(request,'pages/maindashboard.html',{'companyName':companyName,'userprofile':userprofile,'send':send,'previously':previously,'dep':dep})

@login_required(login_url='/umpapi/login/')
def admindashboardV(request):
    return render(request,'pages/admin/admindashboard.html')

@login_required(login_url='/umpapi/login/')
def companyandbranchV(request):
    Coinfo=BranchInformationM.objects.all()[:1]
    return render(request,'pages/admin/forms/companyandbranch.html',{'Coinfo':Coinfo})

@login_required(login_url='/umpapi/login/')
def CompanySaveV(request):

    if request.method == 'POST' and request.FILES:
        cname = request.POST.get('cname')
        names = request.POST.get('bname')
        addresss = request.POST.get('baddress')
        snames = request.POST.get('sname')
        phones = request.POST.get('pnumber')
        faxs = request.POST.get('fnumber')
        emails = request.POST.get('enumber')
        bcodes = request.POST.get('bcode')
        image = request.FILES['clogo']
        store = FileSystemStorage()
        filename = store.save(image.name, image)
        profile_pic_url = store.url(filename)
        data = BranchInformationM(Branch_Name=names, Address=addresss, Short_Name=snames, Phone=phones, Fax=faxs,
                                  Email=emails, Branch_Code=bcodes, BranchLogo=filename, Company_Name=cname)
        data.save()
        messages.info(request, 'Data Saved')
    else:
        cname = request.POST.get('cname')
        names = request.POST.get('bname')
        addresss = request.POST.get('baddress')
        snames = request.POST.get('sname')
        phones = request.POST.get('pnumber')
        faxs = request.POST.get('fnumber')
        emails = request.POST.get('enumber')
        bcodes = request.POST.get('bcode')
        data = BranchInformationM(Branch_Name=names, Address=addresss, Short_Name=snames, Phone=phones, Fax=faxs,
                                  Email=emails, Branch_Code=bcodes, Company_Name=cname)
        data.save()
        messages.info(request, 'Data Saved')

    Coinfo = BranchInformationM.objects.all()[:1]
    return render(request,'pages/admin/report/company.html',{'Coinfo':Coinfo})

    # return HttpResponse('abc')

@login_required(login_url='/umpapi/login/')
def UMP_APIV(request):
    userprofile = UserProfileM.objects.filter(id=request.user.id)
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    mycursor = cnx.cursor()
    mycursor.execute("""BEGIN LOAD_MONEY_RECEIPT(); END;""")
    cnx.commit()
    mycursor.execute("""SELECT
        mrSerialNumber,
        officeBranchCode,
        officeBranchName,
        mrNumber,
        mrDate,
        classInsurance,
        insuredName,
        insuredAddress,
        insuredMobile,
        insuredEmail,
        modeOfPayment,
        paymentDetail ,
        coverNoteNumber,
        policyNumber,
        addendumNumber,
        endorsementNumber,
        netPremium,
        vat,
        stamp,
        others,
        totalPremium,
        chequeDrawnOn,
        chequeDate,
        depositDate,
        depositedToBank,
        depositedToBranch,
        depositedToAccountNumber,
        mfs,
        mfsAccountNumber,
        isCoInsurance,
        isLeader,
        financingBankName,
        financingBankAddress,
        financingBankEmail,
        financingBankMobile,
        isMultiDocument,
        multiDocuments,
        currency,
        leaderDocument,
        paymentReceivedFrom,
        serviceCharge,
        coInsurerPremiumAmount,
        bankGuaranteeNumber,
        requeston ,
        responseon,
        response,
        mrURL,
        umpStatus,
        depositStatus from ump_mr where sendate is null and depositdate is null
        """)
    myresults = mycursor.fetchall()

    return render(request,'pages/admin/api.html',{'myresults':myresults,'companyName':companyName,'userprofile':userprofile})


@login_required(login_url='/umpapi/login/')
def UMP_APIsV(request):
    mr=request.POST.getlist('vehicle1')
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    mycursor = cnx.cursor()
    mycursor.execute("BEGIN LOAD_MONEY_RECEIPT(); END;")
    cnx.commit()
    c = min([len(mr)])
    for i in range(c):
        mycursor.execute("""SELECT
                mrSerialNumber,
                officeBranchCode,
                officeBranchName,
                mrNumber,
                to_char(mrDate, 'YYYY-MM-DD') as mrDate,
                classInsurance,
                insuredName,
                insuredAddress,
                insuredMobile,
                insuredEmail,
                modeOfPayment,
                paymentDetail ,
                coverNoteNumber,
                policyNumber,
                addendumNumber,
                endorsementNumber,
                netPremium,
                vat,
                stamp,
                others,
                totalPremium,
                chequeDrawnOn,
                to_char(chequeDate, 'YYYY-MM-DD') as chequeDate,
                to_char(depositDate, 'YYYY-MM-DD') as depositDate,
                depositedToBank,
                depositedToBranch,
                depositedToAccountNumber,
                mfs,
                mfsAccountNumber,
                isCoInsurance,
                isLeader,
                financingBankName,
                financingBankAddress,
                financingBankEmail,
                financingBankMobile,
                isMultiDocument,
                multiDocuments,
                currency,
                leaderDocument,
                paymentReceivedFrom,
                serviceCharge,
                coInsurerPremiumAmount,
                bankGuaranteeNumber,
                requeston ,
                responseon,
                response,
                mrURL,
                umpStatus,
                depositStatus from ump_mr where mrnumber in (:mr)
                """,[mr[i]])
        myresultss = mycursor.fetchall()
        for (mrSerialNumber,
             officeBranchCode,
             officeBranchName,
             mrNumber,
             mrDate,
             classInsurance,
             insuredName,
             insuredAddress,
             insuredMobile,
             insuredEmail,
             modeOfPayment,
             paymentDetail,
             coverNoteNumber,
             policyNumber,
             addendumNumber,
             endorsementNumber,
             netPremium,
             vat,
             stamp,
             others,
             totalPremium,
             chequeDrawnOn,
             chequeDate,
             depositDate,
             depositedToBank,
             depositedToBranch,
             depositedToAccountNumber,
             mfs,
             mfsAccountNumber,
             isCoInsurance,
             isLeader,
             financingBankName,
             financingBankAddress,
             financingBankEmail,
             financingBankMobile,
             isMultiDocument,
             multiDocuments,
             currency,
             leaderDocument,
             paymentReceivedFrom,
             serviceCharge,
             coInsurerPremiumAmount,
             bankGuaranteeNumber,
             requeston,
             responseon,
             response,
             mrURL,
             umpStatus,
             depositStatus) in myresultss:
            payload = {'client_id': 'paramount', 'client_secret': 'aNtJHwAGCh'}
            r = requests.post('https://idra-ump.com/test/app/extern/v1/authenticate', json=payload)
            print(r)
            access_para = json.loads(r.text)
            access_tokenpara = access_para['access_token']
            print(access_tokenpara)
            refresh_para = json.loads(r.text)
            refresh_tokenpara = refresh_para['refresh_token']
            token_para = json.loads(r.text)
            token_typepara = token_para['token_type']
            payloads = {"mrSerialNumber": mrSerialNumber,
                        "officeBranchCode": str(officeBranchCode),
                        "officeBranchName": officeBranchName,
                        "mrNumber": mrNumber,
                        "mrDate": mrDate,
                        "classInsurance": classInsurance,
                        "insuredName": insuredName,
                        "insuredAddress": insuredAddress,
                        "insuredMobile": insuredMobile,
                        "insuredEmail": insuredEmail,
                        "modeOfPayment": modeOfPayment,
                        "paymentDetail": paymentDetail,
                        "coverNoteNumber": coverNoteNumber,
                        "policyNumber": policyNumber,
                        "addendumNumber": addendumNumber,
                        "endorsementNumber": endorsementNumber,
                        "netPremium": netPremium,
                        "vat": vat,
                        "stamp": stamp,
                        "others": others,
                        "totalPremium": totalPremium,
                        "chequeDrawnOn": chequeDrawnOn,
                        "chequeDate": chequeDate,
                        "depositDate": depositDate,
                        "depositedToBank": depositedToBank,
                        "depositedToBranch": depositedToBranch,
                        "depositedToAccountNumber": depositedToAccountNumber,
                        "mfs": mfs,
                        "mfsAccountNumber": mfsAccountNumber,
                        "isCoInsurance": isCoInsurance,
                        "isLeader": isLeader,
                        "financingBankName": financingBankName,
                        "financingBankAddress": financingBankAddress,
                        "financingBankEmail": financingBankEmail,
                        "financingBankMobile": financingBankMobile,
                        "bankGuaranteeNumber": bankGuaranteeNumber,
                        "isMultiDocument": isMultiDocument,
                        "currency": currency,
                        "serviceCharge": serviceCharge,
                        "leaderDocument": leaderDocument,
                        "paymentReceivedFrom": paymentReceivedFrom,
                        "coInsurerPremiumAmount": coInsurerPremiumAmount,
                        "multiDocuments": multiDocuments}

            # print(payloads)
            ab = requests.post('https://idra-ump.com/test/app/extern/v1/money-receipt', json=payloads,headers={'Authorization': f"Bearer {access_tokenpara}"})
            print(ab.json())
            ur = json.loads(ab.text)
            statuss = ur['status']
            if statuss != 'False':
                try:
                    cdate=datetime.datetime.now().date()

                    mrur = ur["url"]
                    mycursor.execute("update ump_mr set mrurl=:mrur , umpStatus='Y', sendate=:cdate where mrNumber =:mrNumber", [mrur,cdate, mr[i]])
                    cnx.commit()
                    mycursor.execute("update ump_mr set RESPONSE='Y' where mrNumber =:mrNumber and DEPOSITSTATUS ='N'",[mr[i]])
                    cnx.commit()
                    messages.info(request, "Data sended")
                except:
                    messages.info(request,f"Data Not sended {ur}")

            mycur = cnx.cursor()
            for x in range(c):
                mycur.execute("""SELECT
                        mrSerialNumber,
                        officeBranchCode,
                        officeBranchName,
                        mrNumber,
                        mrDate,
                        classInsurance,
                        insuredName,
                        insuredAddress,
                        insuredMobile,
                        insuredEmail,
                        modeOfPayment,
                        paymentDetail ,
                        coverNoteNumber,
                        policyNumber,
                        addendumNumber,
                        endorsementNumber,
                        netPremium,
                        vat,
                        stamp,
                        others,
                        totalPremium,
                        chequeDrawnOn,
                        chequeDate,
                        depositDate,
                        depositedToBank,
                        depositedToBranch,
                        depositedToAccountNumber,
                        mfs,
                        mfsAccountNumber,
                        isCoInsurance,
                        isLeader,
                        financingBankName,
                        financingBankAddress,
                        financingBankEmail,
                        financingBankMobile,
                        isMultiDocument,
                        multiDocuments,
                        currency,
                        leaderDocument,
                        paymentReceivedFrom,
                        serviceCharge,
                        coInsurerPremiumAmount,
                        bankGuaranteeNumber,
                        requeston ,
                        responseon,
                        response,
                        mrURL,
                        umpStatus,
                        depositStatus from ump_mr where sendate is null and depositdate is null
                        """)
                myresults = mycur.fetchall()
            return render(request,'pages/admin/apis.html',{'myresults':myresults})

@login_required(login_url='/umpapi/login/')
def UMP_APIsendeV(request):
    userprofile = UserProfileM.objects.filter(id=request.user.id)

    return render(request,'pages/admin/forms/dashboard.html',{'userprofile':userprofile,'companyName':companyName})

@login_required(login_url='/umpapi/login/')
def previouslysende(request):
    userprofile = UserProfileM.objects.filter(id=request.user.id)
    fromDate = request.POST.get('fdate')
    fdate = datetime.datetime.strptime(fromDate, '%Y-%m-%d')
    toDate = request.POST.get('tdate')
    tdate = datetime.datetime.strptime(toDate, '%Y-%m-%d')
    b=UserProfileM.objects.filter(user=request.user.id)
    for x in b:
        a=x.Branch_code
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    mycursor = cnx.cursor()
    mycursor.execute("""BEGIN LOAD_MONEY_RECEIPT(); END;""")
    cnx.commit()
    mycursor.execute("""SELECT
              mrSerialNumber,
              officeBranchCode,
              officeBranchName,
              mrNumber,
              mrDate,
              classInsurance,
              insuredName,
              insuredAddress,
              insuredMobile,
              insuredEmail,
              modeOfPayment,
              paymentDetail ,
              coverNoteNumber,
              policyNumber,
              addendumNumber,
              endorsementNumber,
              netPremium,
              vat,
              stamp,
              others,
              totalPremium,
              chequeDrawnOn,
              chequeDate,
              depositDate,
              depositedToBank,
              depositedToBranch,
              depositedToAccountNumber,
              mfs,
              mfsAccountNumber,
              isCoInsurance,
              isLeader,
              financingBankName,
              financingBankAddress,
              financingBankEmail,
              financingBankMobile,
              isMultiDocument,
              multiDocuments,
              currency,
              leaderDocument,
              paymentReceivedFrom,
              serviceCharge,
              coInsurerPremiumAmount,
              bankGuaranteeNumber,
              requeston ,
              responseon,
              response,
              mrURL,
              umpStatus,
              depositStatus from ump_mr where mrurl is not null and sendate between :fdate and :tdate and officeBranchCode=:bcode
              """, [fdate, tdate, a])
    myresults = mycursor.fetchall()
    return render(request,'pages/admin/report/previousreport.html',{'companyName':companyName,'userprofile':userprofile,'myresults':myresults})

@login_required(login_url='/umpapi/login/')
def previouslysendePDFV(request):
    fromDate = request.POST.get('fdate')
    fdate = datetime.datetime.strptime(fromDate, '%Y-%m-%d')
    toDate = request.POST.get('tdate')
    tdate = datetime.datetime.strptime(toDate, '%Y-%m-%d')
    b = UserProfileM.objects.filter(user=request.user.id)
    for x in b:
        a = x.Branch_code
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    mycursor = cnx.cursor()
    mycursor.execute("""BEGIN LOAD_MONEY_RECEIPT(); END;""")
    cnx.commit()
    mycursor.execute("""SELECT
                 mrSerialNumber,
                 officeBranchCode,
                 officeBranchName,
                 mrNumber,
                 mrDate,
                 classInsurance,
                 insuredName,
                 insuredAddress,
                 insuredMobile,
                 insuredEmail,
                 modeOfPayment,
                 paymentDetail ,
                 coverNoteNumber,
                 policyNumber,
                 addendumNumber,
                 endorsementNumber,
                 netPremium,
                 vat,
                 stamp,
                 others,
                 totalPremium,
                 chequeDrawnOn,
                 chequeDate,
                 depositDate,
                 depositedToBank,
                 depositedToBranch,
                 depositedToAccountNumber,
                 mfs,
                 mfsAccountNumber,
                 isCoInsurance,
                 isLeader,
                 financingBankName,
                 financingBankAddress,
                 financingBankEmail,
                 financingBankMobile,
                 isMultiDocument,
                 multiDocuments,
                 currency,
                 leaderDocument,
                 paymentReceivedFrom,
                 serviceCharge,
                 coInsurerPremiumAmount,
                 bankGuaranteeNumber,
                 requeston ,
                 responseon,
                 response,
                 mrURL,
                 umpStatus,
                 depositStatus from ump_mr where mrurl is not null and sendate between :fdate and :tdate and officeBranchCode = :bcode
                 """, [fdate, tdate, a])
    myresults = mycursor.fetchall()
    template_path = 'pages/admin/report/MRPDF.html'
    context = {'companyName':companyName,'myresults':myresults}
    response = HttpResponse(content_type='application/pdf')
    # for downlode
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def MrserarchV(request):
    userprofile = UserProfileM.objects.filter(id=request.user.id)
    mr = request.POST.get('mrno')
    b = UserProfileM.objects.filter(user=request.user.id)
    for x in b:
        a = x.Branch_code
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    mycursor = cnx.cursor()
    mycursor.execute("""BEGIN LOAD_MONEY_RECEIPT(); END;""")
    cnx.commit()
    mycursor.execute("""SELECT
                  mrSerialNumber,
                  officeBranchCode,
                  officeBranchName,
                  mrNumber,
                  mrDate,
                  classInsurance,
                  insuredName,
                  insuredAddress,
                  insuredMobile,
                  insuredEmail,
                  modeOfPayment,
                  paymentDetail ,
                  coverNoteNumber,
                  policyNumber,
                  addendumNumber,
                  endorsementNumber,
                  netPremium,
                  vat,
                  stamp,
                  others,
                  totalPremium,
                  chequeDrawnOn,
                  chequeDate,
                  depositDate,
                  depositedToBank,
                  depositedToBranch,
                  depositedToAccountNumber,
                  mfs,
                  mfsAccountNumber,
                  isCoInsurance,
                  isLeader,
                  financingBankName,
                  financingBankAddress,
                  financingBankEmail,
                  financingBankMobile,
                  isMultiDocument,
                  multiDocuments,
                  currency,
                  leaderDocument,
                  paymentReceivedFrom,
                  serviceCharge,
                  coInsurerPremiumAmount,
                  bankGuaranteeNumber,
                  requeston ,
                  responseon,
                  response,
                  mrURL,
                  umpStatus,
                  depositStatus from ump_mr where mrURL is not null and mrNumber=:mr
                  """, [mr])
    myresults = mycursor.fetchall()
    return render(request, 'pages/admin/report/mrreport.html',
                  {'companyName': companyName, 'userprofile': userprofile, 'myresults': myresults})

def AllsendedV(request):
    fromDate = request.POST.get('fdate')
    fdate = datetime.datetime.strptime(fromDate, '%Y-%m-%d')
    toDate = request.POST.get('tdate')
    tdate = datetime.datetime.strptime(toDate, '%Y-%m-%d')
    userprofile = UserProfileM.objects.filter(id=request.user.id)
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    mycursor = cnx.cursor()
    mycursor.execute("""BEGIN LOAD_MONEY_RECEIPT(); END;""")
    cnx.commit()
    mycursor.execute("""SELECT
                  mrSerialNumber,
                  officeBranchCode,
                  officeBranchName,
                  mrNumber,
                  mrDate,
                  classInsurance,
                  insuredName,
                  insuredAddress,
                  insuredMobile,
                  insuredEmail,
                  modeOfPayment,
                  paymentDetail ,
                  coverNoteNumber,
                  policyNumber,
                  addendumNumber,
                  endorsementNumber,
                  netPremium,
                  vat,
                  stamp,
                  others,
                  totalPremium,
                  chequeDrawnOn,
                  chequeDate,
                  depositDate,
                  depositedToBank,
                  depositedToBranch,
                  depositedToAccountNumber,
                  mfs,
                  mfsAccountNumber,
                  isCoInsurance,
                  isLeader,
                  financingBankName,
                  financingBankAddress,
                  financingBankEmail,
                  financingBankMobile,
                  isMultiDocument,
                  multiDocuments,
                  currency,
                  leaderDocument,
                  paymentReceivedFrom,
                  serviceCharge,
                  coInsurerPremiumAmount,
                  bankGuaranteeNumber,
                  requeston ,
                  responseon,
                  response,
                  mrURL,
                  umpStatus,
                  depositStatus from ump_mr where mrurl is not null and sendate between :fdate and :tdate
                  """,[fdate, tdate])
    myresults = mycursor.fetchall()
    return render(request, 'pages/admin/report/mrreport.html',
                  {'companyName': companyName, 'userprofile': userprofile, 'myresults': myresults})


def chatV(request):
    if request.user.is_superuser:
        chat = chatM.objects.all().order_by('-dates')
    else:
        chat=chatM.objects.filter(users=request.user).order_by('-dates')
    tex=request.POST.get('texs')
    mr=request.POST.get('mrs')
    us=User.objects.get(username=request.user)
    pro=UserProfileM.objects.get(user=us)
    data=chatM(chat_box=tex,mrno=mr,users=us,branch=pro)
    data.save()
    return render(request,'pages/admin/report/chat.html',{'chat':chat})

def searchV(request):
    mrs=request.GET.get('searchs')
    if request.user.is_superuser:
        chat = chatM.objects.filter(mrno=mrs).order_by('-dates')
    else:
        chat=chatM.objects.filter(users=request.user).order_by('-dates')
    return render(request, 'pages/admin/report/chat.html', {'chat': chat})

def AcommentV(request,id=0):
    if id != 0:
        data=chatM.objects.filter(pk=id).order_by('-dates')
    return render(request,'pages/admin/forms/admincomment.html',{'data':data})

def AcommenteditV(request,id=0):
    if request.user.is_superuser:
        chat = chatM.objects.all().order_by('-dates')
    else:
        chat=chatM.objects.filter(users=request.user).order_by('-dates')
    if id !=0:
        com=request.POST.get('comment')
        data=chatM.objects.get(pk=id)
        data.comment=com
        data.save()
    return render(request, 'pages/admin/report/chat.html', {'chat': chat})


@login_required(login_url='/umpapi/login/')
def UMP_APIMRV(request):
    amr=request.GET.get('mrserch')
    userprofile = UserProfileM.objects.filter(id=request.user.id)
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    mycursor = cnx.cursor()
    mycursor.execute("""BEGIN LOAD_MONEY_RECEIPT(); END;""")
    cnx.commit()
    mycursor.execute("""SELECT
        mrSerialNumber,
        officeBranchCode,
        officeBranchName,
        mrNumber,
        mrDate,
        classInsurance,
        insuredName,
        insuredAddress,
        insuredMobile,
        insuredEmail,
        modeOfPayment,
        paymentDetail ,
        coverNoteNumber,
        policyNumber,
        addendumNumber,
        endorsementNumber,
        netPremium,
        vat,
        stamp,
        others,
        totalPremium,
        chequeDrawnOn,
        chequeDate,
        depositDate,
        depositedToBank,
        depositedToBranch,
        depositedToAccountNumber,
        mfs,
        mfsAccountNumber,
        isCoInsurance,
        isLeader,
        financingBankName,
        financingBankAddress,
        financingBankEmail,
        financingBankMobile,
        isMultiDocument,
        multiDocuments,
        currency,
        leaderDocument,
        paymentReceivedFrom,
        serviceCharge,
        coInsurerPremiumAmount,
        bankGuaranteeNumber,
        requeston ,
        responseon,
        response,
        mrURL,
        umpStatus,
        depositStatus from ump_mr where sendate is null and depositdate is null and mrNumber=:mr
        """,[amr])
    myresults = mycursor.fetchall()

    return render(request,'pages/admin/apis.html',{'myresults':myresults,'companyName':companyName,'userprofile':userprofile})




def UMP_deposit(request):
    userprofile = UserProfileM.objects.filter(id=request.user.id)
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    mycursor = cnx.cursor()
    mycursor.execute("""BEGIN LOAD_MONEY_RECEIPT(); END;""")
    cnx.commit()
    mycursor.execute("""SELECT
        mrSerialNumber,
        officeBranchCode,
        officeBranchName,
        mrNumber,
        mrDate,
        classInsurance,
        insuredName,
        insuredAddress,
        insuredMobile,
        insuredEmail,
        modeOfPayment,
        paymentDetail ,
        coverNoteNumber,
        policyNumber,
        addendumNumber,
        endorsementNumber,
        netPremium,
        vat,
        stamp,
        others,
        totalPremium,
        chequeDrawnOn,
        chequeDate,
        depositDate,
        depositedToBank,
        depositedToBranch,
        depositedToAccountNumber,
        mfs,
        mfsAccountNumber,
        isCoInsurance,
        isLeader,
        financingBankName,
        financingBankAddress,
        financingBankEmail,
        financingBankMobile,
        isMultiDocument,
        multiDocuments,
        currency,
        leaderDocument,
        paymentReceivedFrom,
        serviceCharge,
        coInsurerPremiumAmount,
        bankGuaranteeNumber,
        requeston ,
        responseon,
        response,
        mrURL,
        umpStatus,
        depositStatus from ump_mr where RESPONSE is null and depositdate is not null
        """)
    myresults = mycursor.fetchall()

    return render(request,'pages/admin/forms/deposid.html',{'myresults':myresults,'companyName':companyName,'userprofile':userprofile})




def UMP_depositedV(request):
    mr=request.POST.getlist('vehicle1')
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    mycursor = cnx.cursor()
    mycursor.execute("BEGIN LOAD_MONEY_RECEIPT(); END;")
    cnx.commit()
    c = min([len(mr)])
    for i in range(c):
        mycursor.execute("""SELECT
                mrSerialNumber,
                officeBranchCode,
                officeBranchName,
                mrNumber,
                to_char(mrDate, 'YYYY-MM-DD') as mrDate,
                classInsurance,
                insuredName,
                insuredAddress,
                insuredMobile,
                insuredEmail,
                modeOfPayment,
                paymentDetail ,
                coverNoteNumber,
                policyNumber,
                addendumNumber,
                endorsementNumber,
                netPremium,
                vat,
                stamp,
                others,
                totalPremium,
                chequeDrawnOn,
                to_char(chequeDate, 'YYYY-MM-DD') as chequeDate,
                to_char(depositDate, 'YYYY-MM-DD') as depositDate,
                depositedToBank,
                depositedToBranch,
                depositedToAccountNumber,
                mfs,
                mfsAccountNumber,
                isCoInsurance,
                isLeader,
                financingBankName,
                financingBankAddress,
                financingBankEmail,
                financingBankMobile,
                isMultiDocument,
                multiDocuments,
                currency,
                leaderDocument,
                paymentReceivedFrom,
                serviceCharge,
                coInsurerPremiumAmount,
                bankGuaranteeNumber,
                requeston ,
                responseon,
                response,
                mrURL,
                umpStatus,
                depositStatus from ump_mr where mrnumber in (:mr)
                """,[mr[i]])
        myresultss = mycursor.fetchall()
        for (mrSerialNumber,
             officeBranchCode,
             officeBranchName,
             mrNumber,
             mrDate,
             classInsurance,
             insuredName,
             insuredAddress,
             insuredMobile,
             insuredEmail,
             modeOfPayment,
             paymentDetail,
             coverNoteNumber,
             policyNumber,
             addendumNumber,
             endorsementNumber,
             netPremium,
             vat,
             stamp,
             others,
             totalPremium,
             chequeDrawnOn,
             chequeDate,
             depositDate,
             depositedToBank,
             depositedToBranch,
             depositedToAccountNumber,
             mfs,
             mfsAccountNumber,
             isCoInsurance,
             isLeader,
             financingBankName,
             financingBankAddress,
             financingBankEmail,
             financingBankMobile,
             isMultiDocument,
             multiDocuments,
             currency,
             leaderDocument,
             paymentReceivedFrom,
             serviceCharge,
             coInsurerPremiumAmount,
             bankGuaranteeNumber,
             requeston,
             responseon,
             response,
             mrURL,
             umpStatus,
             depositStatus) in myresultss:
            payload = {'client_id': 'paramount', 'client_secret': 'aNtJHwAGCh'}
            r = requests.post('https://idra-ump.com/test/app/extern/v1/authenticate', json=payload)
            print(r)
            access_para = json.loads(r.text)
            access_tokenpara = access_para['access_token']
            print(access_tokenpara)
            refresh_para = json.loads(r.text)
            refresh_tokenpara = refresh_para['refresh_token']
            token_para = json.loads(r.text)
            token_typepara = token_para['token_type']
            payloads = {"mrSerialNumber": mrSerialNumber,
                        "officeBranchCode": str(officeBranchCode),
                        "officeBranchName": officeBranchName,
                        "mrNumber": mrNumber,
                        "mrDate": mrDate,
                        "classInsurance": classInsurance,
                        "insuredName": insuredName,
                        "insuredAddress": insuredAddress,
                        "insuredMobile": insuredMobile,
                        "insuredEmail": insuredEmail,
                        "modeOfPayment": modeOfPayment,
                        "paymentDetail": paymentDetail,
                        "coverNoteNumber": coverNoteNumber,
                        "policyNumber": policyNumber,
                        "addendumNumber": addendumNumber,
                        "endorsementNumber": endorsementNumber,
                        "netPremium": netPremium,
                        "vat": vat,
                        "stamp": stamp,
                        "others": others,
                        "totalPremium": totalPremium,
                        "chequeDrawnOn": chequeDrawnOn,
                        "chequeDate": chequeDate,
                        "depositDate": depositDate,
                        "depositedToBank": depositedToBank,
                        "depositedToBranch": depositedToBranch,
                        "depositedToAccountNumber": depositedToAccountNumber,
                        "mfs": mfs,
                        "mfsAccountNumber": mfsAccountNumber,
                        "isCoInsurance": isCoInsurance,
                        "isLeader": isLeader,
                        "financingBankName": financingBankName,
                        "financingBankAddress": financingBankAddress,
                        "financingBankEmail": financingBankEmail,
                        "financingBankMobile": financingBankMobile,
                        "bankGuaranteeNumber": bankGuaranteeNumber,
                        "isMultiDocument": isMultiDocument,
                        "currency": currency,
                        "serviceCharge": serviceCharge,
                        "leaderDocument": leaderDocument,
                        "paymentReceivedFrom": paymentReceivedFrom,
                        "coInsurerPremiumAmount": coInsurerPremiumAmount,
                        "multiDocuments": multiDocuments}

            # print(payloads)
            ab = requests.post('https://idra-ump.com/test/app/extern/v1/money-receipt', json=payloads,headers={'Authorization': f"Bearer {access_tokenpara}"})
            print(ab.json())
            ur = json.loads(ab.text)
            statuss = ur['status']
            if statuss != 'False':
                try:
                    cdate=datetime.datetime.now().date()

                    mrur = ur["url"]
                    mycursor.execute("update ump_mr set mrurl=:mrur , umpStatus='Y', sendate=:cdate where mrNumber =:mrNumber", [mrur,cdate, mr[i]])
                    cnx.commit()
                    mycursor.execute("update ump_mr set RESPONSE='Y' where mrNumber =:mrNumber and DEPOSITSTATUS ='N'",[mr[i]])
                    cnx.commit()
                    messages.info(request, "Data sended")
                except:
                    messages.info(request,f"Data Not sended {ur}")

            mycur = cnx.cursor()
            for x in range(c):
                mycur.execute("""SELECT
                        mrSerialNumber,
                        officeBranchCode,
                        officeBranchName,
                        mrNumber,
                        mrDate,
                        classInsurance,
                        insuredName,
                        insuredAddress,
                        insuredMobile,
                        insuredEmail,
                        modeOfPayment,
                        paymentDetail ,
                        coverNoteNumber,
                        policyNumber,
                        addendumNumber,
                        endorsementNumber,
                        netPremium,
                        vat,
                        stamp,
                        others,
                        totalPremium,
                        chequeDrawnOn,
                        chequeDate,
                        depositDate,
                        depositedToBank,
                        depositedToBranch,
                        depositedToAccountNumber,
                        mfs,
                        mfsAccountNumber,
                        isCoInsurance,
                        isLeader,
                        financingBankName,
                        financingBankAddress,
                        financingBankEmail,
                        financingBankMobile,
                        isMultiDocument,
                        multiDocuments,
                        currency,
                        leaderDocument,
                        paymentReceivedFrom,
                        serviceCharge,
                        coInsurerPremiumAmount,
                        bankGuaranteeNumber,
                        requeston ,
                        responseon,
                        response,
                        mrURL,
                        umpStatus,
                        depositStatus from ump_mr where RESPONSE is null and depositdate is not null
                        """)
                myresults = mycur.fetchall()
            return render(request,'pages/admin/deposidsend.html',{'myresults':myresults})


def UMP_APdepositV(request):
    amr=request.GET.get('mrserch')
    userprofile = UserProfileM.objects.filter(id=request.user.id)
    cnx = cx_Oracle.connect('PICLNEW/PICLNEW@//192.168.100.22:1521/pmdb')
    mycursor = cnx.cursor()
    mycursor.execute("""BEGIN LOAD_MONEY_RECEIPT(); END;""")
    cnx.commit()
    mycursor.execute("""SELECT
        mrSerialNumber,
        officeBranchCode,
        officeBranchName,
        mrNumber,
        mrDate,
        classInsurance,
        insuredName,
        insuredAddress,
        insuredMobile,
        insuredEmail,
        modeOfPayment,
        paymentDetail ,
        coverNoteNumber,
        policyNumber,
        addendumNumber,
        endorsementNumber,
        netPremium,
        vat,
        stamp,
        others,
        totalPremium,
        chequeDrawnOn,
        chequeDate,
        depositDate,
        depositedToBank,
        depositedToBranch,
        depositedToAccountNumber,
        mfs,
        mfsAccountNumber,
        isCoInsurance,
        isLeader,
        financingBankName,
        financingBankAddress,
        financingBankEmail,
        financingBankMobile,
        isMultiDocument,
        multiDocuments,
        currency,
        leaderDocument,
        paymentReceivedFrom,
        serviceCharge,
        coInsurerPremiumAmount,
        bankGuaranteeNumber,
        requeston ,
        responseon,
        response,
        mrURL,
        umpStatus,
        depositStatus from ump_mr where RESPONSE is null and depositdate is not null and mrNumber=:mr
        """,[amr])
    myresults = mycursor.fetchall()

    return render(request,'pages/admin/deposidsend.html',{'myresults':myresults,'companyName':companyName,'userprofile':userprofile})
