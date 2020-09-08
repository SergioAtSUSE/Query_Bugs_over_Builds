#!/usr/bin/python3

#Status:UNCONFIRMED,NEW,CONFIRMED,IN_PROGRESS,REOPENED,RESOLVED,VERIFIED
#Resolution:FIXED,INVALID,WONTFIX,NORESPONSE,UPSTREAM,FEATURE,DUPLICATE,WORKSFORME,MOVED
#Test data:
#bugs_rows.append(['227', '1234567', 'test', 'test', 'NEW', '123', '456'])
#bugs_rows.append(['227', '1234577', 'tfsdest', 'tsfest', 'NEW', 'sf123', '42356'])
#bugs_rows.append(['227', '1234587', 'tessft', 'tesfst', 'CONFIRMED', '1sfd23', '43456'])
#bugs_rows.append(['227', '1234597', 'tessft', 'tessft', 'CONFIRMED', '1fs23', '45326'])
#bugs_rows.append(['228.2', '2234568', 'test', 'test', 'VERIFIED', '123', '456'])
#bugs_rows.append(['228.2', '2234578', 'tfsdest', 'tsfest', 'VERIFIED', 'sf123', '42356'])
#bugs_rows.append(['228.2', '2234588', 'tessft', 'tesfst', 'RESOLVED', '1sfd23', '43456'])
#bugs_rows.append(['228.2', '2234598', 'tessft', 'tessft', 'RESOLVED', '1fs23', '45326'])

import sys
import getopt
import re
import time
import bugzilla as bz
import pandas as pd
import numpy as np
import datetime
import random

product_query = 'Beta SUSE Linux Enterprise Server 15 SP1'
#product_query = 'Public Beta SUSE Linux Enterprise Server 15 SP2'
component_query = ''
status_query = ''
resolution_query = ''
version_query = ''
target_milestone_query = ''
priority_query = 'P5 - None'
#priority_query = 'P1 - Urgent'
severity_query = ''
hardware_query = ''
os_query = ''
include_query = ['ID', 'summary', 'Component', 'Status', 'URL']

def replaceMultiple(mainString, toBeReplaces, newString):
    # Iterate over the strings to be replaced
    for elem in toBeReplaces :
        # Check if string is in the main string
        if elem in mainString :
            # Replace the string
            mainString = mainString.replace(elem, newString)
    return  mainString     

def query_bugzilla_bugs():
    global product_query, component_query, version_query, target_milestone_query, priority_query, include_query
    global status_query, resolution_query, severity_query, hardware_query, os_query
    URL = "https://apibugzilla.suse.com"
    bzapi = bz.Bugzilla(URL)
    bzapi.bug_autorefresh = True

    query = bzapi.build_query(
        product=product_query,
        priority=priority_query,
        include_fields=['id','summary'])
    
    if (component_query):
        query["component"] = component_query
    if (version_query):
        query["version"] = version_query
    if (target_milestone_query):
        query["target_milestone"] = target_milestone_query
    if (status_query):
        query["bug_status"] = status_query
    if (resolution_query):
        query["resolution"] = resolution_query
    if (severity_query):
        query["bug_severity"] = severity_query
    if (hardware_query):
        query["rep_platform"] = hardware_query
    if (os_query):
        query["op_sys"] = os_query

    t1 = time.time()
    bugs = bzapi.query(query)
    t2 = time.time()
    print("Found %d bugs with current query" % len(bugs))
    print(bugs)
    for bug in bugs:
        print("Bug ID: %d Bug Summary: %s" % (bug.id,bug.summary))
    print("Query processing time: %s" % (t2 - t1))
    
    if (bugs):
        bugurl_prefix="https://bugzilla.suse.com/show_bug.cgi?id="
        bugs_rows = []
        for bug in bugs:
            if (re.search(r'\[.*build.*\]', bug.summary, re.I)):
                bug_build_tag = re.search(r'\[.*build.*\]', bug.summary, re.I).group(0)
                if (re.search(r"[0-9]{1,}.*[0-9]{1,}", bug_build_tag, re.I).group(0)):
                    bug_build_num = re.search(r"[0-9]{1,}.*[0-9]{1,}", bug_build_tag, re.I).group(0)
                    bug_summary = bug.summary
                    bug_summary = replaceMultiple(bug_summary, [' ', '\'', '\"', '\`'], '_')
                    bug_item = [bug_build_num, bug.id, bug_summary, bug.component, bug.status, bug.url, bugurl_prefix + str(bug.id)]
                    bugs_rows.append(bug_item)
                else:
                    print("Build number is not provided in bug %d summary !" % bug.id)
            else:
                print("Build number is not provided in bug %d summary !" % bug.id)
        bugs_rows.append(['227', '1234567', 'test', 'test', 'NEW', '123', '456'])
        bugs_rows.append(['227', '1234577', 'tfsdest', 'tsfest', 'NEW', 'sf123', '42356'])
        bugs_rows.append(['227', '1234587', 'tessft', 'tesfst', 'CONFIRMED', '1sfd23', '43456'])
        bugs_rows.append(['227', '1234597', 'tessft', 'tessft', 'CONFIRMED', '1fs23', '45326'])
        bugs_rows.append(['228.2', '2234568', 'test', 'test', 'VERIFIED', '123', '456'])
        bugs_rows.append(['228.2', '2234578', 'tfsdest', 'tsfest', 'VERIFIED', 'sf123', '42356'])
        bugs_rows.append(['228.2', '2234588', 'tessft', 'tesfst', 'RESOLVED', '1sfd23', '43456'])
        bugs_rows.append(['228.2', '2234598', 'tessft', 'tessft', 'RESOLVED', '1fs23', '45326'])
        if (bugs_rows):
            current_date=int(round(time.time() * 1000))
            current_date=pd.Timestamp(current_date, unit='ms')
            query_dates = pd.date_range(current_date, periods=len(bugs_rows), freq='ms')
            bugs_data = pd.DataFrame(bugs_rows, columns=['Build', 'ID', 'Summary', 'Component', 'Status', 'URL', 'BUGURL'], index=query_dates)
            print("Bugs over Builds:\n%s" % bugs_data)
            bugs_data.sort_values(['Build', 'ID'], ascending=True)
            bugs_data.to_csv('/root/bugs_over_builds.csv', index=True)
            print("Data of bugs over builds is stored in /root/bugs_over_builds.csv !")
        else:
            print("No data of bugs over builds is generated !")

def main(argv):
    global product_query, component_query, version_query, target_milestone_query, priority_query, include_query
    global status_query, resolution_query, severity_query, hardware_query, os_query
    try:
        opts,args = getopt.getopt(argv,"hpcsrvtieaon",["help","product=","component=","status=","resolution=","version=","target milestone=","priority=","severity=","hardware=","os=","include="])
    except getopt.GetoptError:
        print ("Query_P1_bugs_over_builds.py -p <product> -c <component> -s <status> -r <resolution> -v <version> -t <target milestone> -i <priority> -e <severity> -a <hardware> -o <os> -n <include>")
        sys.exit(2)
    for opt,arg in opts:
        if opt in ("-h", "--help"):
           print ("Query_P1_bugs_over_builds.py -p <product> -c <component> -s <status> -r <resolution> -v <version> -t <target milestone> -i <priority> -e <severity> -a <hardware> -o <os> -n <include>")
           sys.exit()
        elif opt in ("-p", "--product"):
             product_query = arg
        elif opt in ("-c", "--component"):
             component_query = arg
        elif opt in ("-s", "--status"):
             status_query = arg
        elif opt in ("-r", "--resolution"):
             resolution_query = arg
        elif opt in ("-v", "--version"):
             version_query = arg
        elif opt in ("-t", "--target_milestone"):
             target_milestone_query = arg
        elif opt in ("-i", "--priority"):
             priority_query = arg
        elif opt in ("-e", "--severity"):
             severity_query = arg
        elif opt in ("-a", "--hardware"):
             hardware_query = arg
        elif opt in ("-o", "--os"):
             os_query = arg
        elif opt in ("-n", "--include"):
             include_query = arg
    print ("Product is", product_query)
    print ("Component is", component_query)
    print ("Status is", status_query)
    print ("Resolution is", resolution_query)
    print ("Version is", version_query)
    print ("Target Milestone is", target_milestone_query)
    print ("Priority is", priority_query)
    print ("Severity is", severity_query)
    print ("Hardware is", hardware_query)
    print ("OS is", os_query)
    print ("Incude is", include_query)
    query_bugzilla_bugs()

if __name__ == "__main__":
    main(sys.argv[1:])
