#use python3
import requests
import json
import logging
import base64
import contextlib
import urllib.parse
import sys
import zipfile
import io
import re
import os


from http.client import HTTPConnection # py3

g_loggingLevel = logging.DEBUG #default logging level

# logging.basicConfig(
#     #filename='HISTORYlistener.log',
#     level=g_loggingLevel,
#     format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )



#logging.info("starting...")
g_debugJiraRequests=False
# cfg_maxAgeInDaysOfInsertedJira=2 #if the jira ticket was created more than 2 days ago we do not insert it

# #which components do we care about
# g_componentImpact={"Application": { "useFieldName":"applicationImpact" },
#     "Search":{ "useFieldName":"searchImpact"},
#     "Reports": { "useFieldName":"reportsImpact"}
#     }



def debug_requests_on():
    '''Switches on logging of the requests module.'''
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def debug_requests_off():
    '''Switches off logging of the requests module, might be some side-effects'''
    global g_loggingLevel
    HTTPConnection.debuglevel = 0
    #logging.info("Here1")
    root_logger = logging.getLogger()
    root_logger.setLevel(g_loggingLevel) #Was warn - but was killing the process so I had to change to info
    root_logger.handlers = []
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.WARNING)
    requests_log.propagate = False
    
@contextlib.contextmanager
def debug_requests(enableDebug=True):
    '''Use with 'with'!'''
    if enableDebug:
        debug_requests_on()
    yield
    if enableDebug:
        debug_requests_off()


jCfg = os.getenv("jirautil_config", None)
if jCfg is None:
    raise AssertionError("you must have an environment variable named jirautil_config with apiUrl and apiAuth")
jCfg = json.loads(jCfg)
for n in ["apiUrl","apiAuth"]:
    if not n in jCfg:
        raise AssertionError("%s must exist in config" % (n))

#encode this for submission should be in form user:password
jCfg["apiAuth"] = (base64.b64encode(jCfg["apiAuth"].encode('utf-8'))).decode('utf-8') 


def jsonField(jsonObj, fieldPath, createIfDNE=False, errorIfDNE=False, defaultIfDNE=None, setInd=False, setValue=None):
    jRef = jsonObj
    if isinstance(fieldPath, list):
        pathSteps=fieldPath
    else: 
        pathSteps=fieldPath.split('.')
    pathStepQty=len(pathSteps)
    if not setValue is None: #if we are setting a value - then we automatically create if DNE
        setInd=True
        createIfDNE=True

    lastStep=False
    for i in range(0,pathStepQty):
        s = pathSteps[i]
        logging.debug("at step %s string=[%s]", i, s)
        #logging.info("jref=%s", jRef)
        if s.startswith("[") and s.endswith("]"): #deal with an array reference
            s = int(s[1:-1])
            #logging.info("new string=[%s]", s)
        try:
            if pathStepQty-1==i and setInd:
                jRef[s]=setValue
            jRef = jRef[s]
        except:
            if errorIfDNE:
                #logging.info("json snippet = %s", jRef)
                raise Exception('expected path does not exist: [%s] - at [%s]' % (fieldPath, s))
            if not createIfDNE:
                return defaultIfDNE            
            if pathStepQty-1==i: # at ultimate value
                jRef[s] = defaultIfDNE
            else:
                jRef[s] = {} #create a stub
            jRef = jRef[s]
    return jRef #return our value

def jiraRequest(method, url, headers={}, data=None, json=None, files=None, convertResponseToJson=True):
    global jCfg, g_debugJiraRequests 
    headers["Authorization"]="Basic %s" % (jCfg["apiAuth"])
    #headers["Content-Type"]="application/json"
    url = jCfg["apiUrl"] + url
    logging.debug("url = %s; auth=%s; data=%s, json=%s", url, headers["Authorization"], data, json)
    resp=None

    with debug_requests(g_debugJiraRequests):
        #sys.exit(0)
        resp =  requests.request(method=method, headers=headers, url=url, data=data, json=json, files=files)
        logging.info("resp=%s", resp.content)
        resp.raise_for_status()
    if not convertResponseToJson:
        return resp.content
    return resp.json()

g_IssueFields = {"issueLinks":{"jiraName":"fields.issuelinks", "jiraDesc":"Related Issues", "required":False, "restrictValues":["Blocks","is blocked by"] },
    "SHA":{
        "key":{"jiraName":"key","jiraDesc":"Issue Key", "required":False, "excludeFromUpdate":True},
        "id":{"jiraName":"id","jiraDesc":"Issue ID", "required":False, "excludeFromUpdate":True},
        "created":{"jiraName":"fields.created","jiraDesc":"Created", "required":False, "excludeFromUpdate":True},
        "updated":{"jiraName":"fields.updated","jiraDesc":"Updated", "required":False, "excludeFromUpdate":True},
        "project":{"jiraName":"fields.project.key","jiraDesc":"Project", "required":True, "default":"SHA", "excludeFromUpdate":True},
        "issueType":{"jiraName":"fields.issuetype.name", "jiraDesc":"Issue Type","required":True, "default":"Fairhair Ticket", "excludeFromUpdate":True},
        "summary":{"jiraName":"fields.summary","jiraDesc":"Summary", "required":True},
        "description":{"jiraName":"fields.description","jiraDesc":"Description", "required":True},
        "emailNotifications":{"jiraName":"fields.customfield_10382", "jiraDesc":"Email Notifications", "required":False },
        "assignee":{"jiraName":"fields.assignee","jiraDesc":"Assignee", "required":False, "excludeFromUpdate":True},
        "superadminLink":{"jiraName":"fields.customfield_13491", "jiraDesc":"Account/Opportunity URL", "required":False },
        "companyName":{"jiraName":"fields.customfield_10000", "jiraDesc":"Company", "required":False , "excludeFromUpdate":True},
        "fbUser":{"jiraName":"fields.customfield_10123","jiraDesc":"FB User", "required":False , "excludeFromUpdate":True},
        "ssiRequestType":{"jiraName":"fields.customfield_14380.id","jiraDesc":"SSI Request Type", "required":False, "default":"-1"},
        "icmPlanRequired":{"jiraName":"fields.customfield_13485.id","jiraDesc":"ICM Plan Required", "required":False, "default":"-1"},
        "entitlementsBeyondContract":{"jiraName":"fields.customfield_12681.id","jiraDesc":"Entitlements Beyond Contract", "required":False, "default":"-1"},
        "socialInfluencerPackageDetails":{"jiraName":"fields.customfield_14585.id","jiraDesc":"Social Influencer Package Details", "required":False, "default":"-1"},
        "issueLinks":{"jiraName":"fields.issuelinks", "jiraDesc":"Related Issues", "required":False, "restrictValues":["Blocks","is blocked by"] }
    },
    "MWTR":{ "key":{"jiraName":"key","jiraDesc":"Issue Key", "required":False, "excludeFromUpdate":True},
        "id":{"jiraName":"id","jiraDesc":"Issue ID", "required":False, "excludeFromUpdate":True},
        "created":{"jiraName":"fields.created","jiraDesc":"Created", "required":False, "excludeFromUpdate":True},
        "updated":{"jiraName":"fields.updated","jiraDesc":"Updated", "required":False, "excludeFromUpdate":True},
        "project":{"jiraName":"fields.project.key","jiraDesc":"Project", "required":True, "default":"ENT", "excludeFromUpdate":True},
        "issueType":{"jiraName":"fields.issuetype.name", "jiraDesc":"Issue Type","required":True, "default":"Fairhair Ticket", "excludeFromUpdate":True},
        "summary":{"jiraName":"fields.summary","jiraDesc":"Summary", "required":True},
        "description":{"jiraName":"fields.description","jiraDesc":"Description", "required":True},
        "emailNotifications":{"jiraName":"fields.customfield_10145", "jiraDesc":"Email Notifications", "required":False },
        "assignee":{"jiraName":"fields.assignee","jiraDesc":"Assignee", "required":False, "excludeFromUpdate":True},
        "superadminLink":{"jiraName":"fields.customfield_10040", "jiraDesc":"Account/Opportunity URL", "required":False },
        "companyName":{"jiraName":"fields.customfield_10163", "jiraDesc":"Company", "required":False , "excludeFromUpdate":True},
        "fbUser":{"jiraName":"fields.customfield_10301","jiraDesc":"FB User", "required":False , "excludeFromUpdate":True},
        #"ssiRequestType":{"jiraName":"fields.customfield_14380.id","jiraDesc":"SSI Request Type", "required":False, "default":"-1"},
        #"socialInfluencerPackageDetails":{"jiraName":"fields.customfield_14585.id","jiraDesc":"Social Influencer Package Details", "required":False, "default":"-1"},
        "issueLinks":{"jiraName":"fields.issuelinks", "jiraDesc":"Related Issues", "required":False, "restrictValues":["Blocks","is blocked by"] },
        "requestType":{"jiraName":"fields.customfield_10010", "jiraDesc:":"Request Type", "required":True}, 
        "contentSubRequestType":{"jiraName":"fields.customfield_10993", "jiraDesc:":"Content Sub Request Type", "required":False}
    }
}

def jiraIncidentsJql(jql):
    
    jql = {"jql":jql}
    #jql = {"fields":",".join(g_jiraFieldNames), "expand":"renderedFields", "jql":jql}

    jqlEncoded=urllib.parse.urlencode(jql)
    url = "search?"+jqlEncoded
    return jiraRequest(method="get", url=url)

def jiraIssueInfo(issueKey):
    url = "issue/%s" % (issueKey)
    return jiraRequest(method="get", url=url)

def jiraLinkIssue(issueKey, jLinks):
    global g_IssueFields
    fInfo = g_IssueFields["issueLinks"]
    jReqs=[]
    for j in jLinks:
        if j["name"] not in fInfo["restrictValues"]:
            raise AssertionError("link type [%s] is not permitted - %s sorry" % (j["name"],fInfo["restrictValues"]))
        jReq={ "outwardIssue":{"key":issueKey}, "inwardIssue":{"key":j["key"] },"type":{"name":j["name"]}}
        jReqs.append(jReq)
    for jReq in jReqs:
        logging.info('linking [%s] with [%s]...', jReq["outwardIssue"]["key"],jReq["inwardIssue"]["key"])
        resp = jiraRequest(method="post",url="issueLink", json=jReq, convertResponseToJson=False)
def cleanAttachmentName(attachmentNameToClean):
    sRet = re.sub(r'[^a-zA-Z0-9 ]', '_', attachmentNameToClean)
    return sRet
def jiraAttachFile(issueKey, attachmentName, attachmentData, zipFile=True):
    url = "issue/%s/attachments" % (issueKey)
    if zipFile:
        origAttachmentName=attachmentName
        origAttachmentData=attachmentData
        attachmentName+=".zip" #append the zip extension to the file name
        mem_zip=io.BytesIO()
        with io.BytesIO() as mem_zip:
            with zipfile.ZipFile(file=mem_zip,mode="w",compression=zipfile.ZIP_DEFLATED, allowZip64=False) as zf:
                zf.writestr(origAttachmentName, origAttachmentData)
                # Mark the files as having been created on Windows so that
                # Unix permissions are not inferred as 0000
                # for zfile in zf.filelist:
                #     zfile.create_system = 0 
            mem_zip.seek(0) #move to the first
            attachmentData=mem_zip.read() #replace our data with a zip version
    files={"file":(attachmentName,attachmentData)}
    resp = jiraRequest(method="post",url=url, headers={"X-Atlassian-Token": "no-check"}, files=files, convertResponseToJson=True)
def jsonIssueJiraToFriendly(jJira):
    """takes a jira issue json and parses it into friendly format
    """
    jFriendly={}
    global g_IssueFields
    projectKey = jsonField(g_IssueFields, "fields.project.key")
    for key,val in g_IssueFields[projectKey].items():
        fVal = jsonField(jJira, val["jiraName"])
        if fVal is None:
            continue
        jsonField(jFriendly,key,setValue=fVal)
    return jFriendly

def jsonIssueFriendlyToJira(jParams, isUpdate=False):
    """converts the friendly names into a jira post
    """
    global g_IssueFields
    jReq={}
    jLinks=[]
    projectKey = jsonField(jParams, "project")
    for key,val in jParams.items():
        if key not in g_IssueFields[projectKey]:
            raise AssertionError("field [%s] is not defined in this process (yet)" % (key))
        fInfo=g_IssueFields[projectKey][key]
        if key=="issueLinks":
            #special handling for links
            jLinks=val
            for v in val: #validate these here for better error checking...
                if not v["name"] in fInfo["restrictValues"]:
                    raise AssertionError("link type [%s] is not permitted" % (v["name"]))
            continue #we don't pass the issue links to the main issue call - it happens later
        jsonField(jReq,fInfo["jiraName"],setValue=val)

    for key,fInfo in g_IssueFields[projectKey].items():
        if isUpdate and "excludeFromUpdate" in fInfo and fInfo["excludeFromUpdate"]:
            continue #skip this field when we are updating a ticket (can't be modified)
        #validation
        if "default" in fInfo and jsonField(jReq, fInfo["jiraName"]) is None:
            jsonField(jReq, fInfo["jiraName"],setValue=fInfo["default"])
        #logging.info("jReq=%s", jReq)
        if "required" in fInfo and fInfo["required"]:
            if jsonField(jReq, fInfo["jiraName"]) in [None,""]:
                raise AssertionError("field is required and was not provided: %s, %s" % (key, fInfo))
    return {"jReq":jReq, "jLinks":jLinks}
# def jiraIssuePost(jParams, issueKey=""):
#     isUpdate=False
#     method="post"
#     if issueKey is None:
#         issueKey=""
#     if issueKey!="":
#         isUpdate=True
#         method="put"
#     url = "issue/%s" % (issueKey)
#     r=jsonIssueFriendlyToJira(jParams, isUpdate)
#     jReq=r["jReq"]
#     jLinks=r["jLinks"]
#     logging.debug("request = %s", jReq)
#     jResp = jiraRequest(method=method,url=url, json=jReq)
#     logging.debug("resp=%s", jResp)
#     key=jResp["key"]
#     jiraLinkIssue(key,jLinks) #this call doesn't return anything  
#     return jResp

def jiraUpdateIssue(jParams, issueKey):
    url = "issue/%s" % (issueKey)
    r=jsonIssueFriendlyToJira(jParams, isUpdate=True)
    jReq=r["jReq"]
    jLinks=r["jLinks"]
    jiraRequest(method="put",url=url, json=jReq, convertResponseToJson=False) #this call doesn't return anything
    jiraLinkIssue(issueKey,jLinks) #this call doesn't return anything  
    jResp=jiraIssueInfo(issueKey) #return the issue info
    return jResp

def jiraAddIssue(jParams):
    url = "issue/"
    r=jsonIssueFriendlyToJira(jParams, isUpdate=False)
    logging.info("r=%s",r)
    jReq=r["jReq"]
    jLinks=r["jLinks"]
    jResp=jiraRequest(method="post",url=url, json=jReq) 
    key=jResp["key"]
    jiraLinkIssue(key,jLinks) #this call doesn't return anything  
    return jResp
    
# jParams={
#     "summary":"test summary",
#     "description":"test description",
#     "companyName":"test company",
#     "assignee":"fred.brown",
#     "issueLinks":[{"key":"T3-1538","name":"blocks"}]
#     # ,
#     # "assignee":"fred.brown@meltwater.com"
# }

# logging.info("calling...")
# # resp = jiraIncidentsJql(jql="key in ('SHA-185172')")
# #files = {"file":open("test_file.txt","rb")}
# #files = {"file":("test4_file.txt","this is a fake file from memory😍 with special characters"*10000)}
# jiraAttachFile("SHA-185232",attachmentName="test5_file.txt",attachmentData="this is a fake file from memory😍 with special characters"*10000)
# #jiraLinkIssue("SHA-185232", [{"key":"T3-1538","name":"blocks"}])

# sys.exit(0)
# # logging.info("resp=%s", resp)
# resp = jiraAddIssue(jParams)
# logging.info("resp=%s", resp)
# logging.info("finished!")
