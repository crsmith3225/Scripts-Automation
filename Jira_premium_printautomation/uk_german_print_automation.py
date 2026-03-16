import sys
import jiraUtil
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#Setup Logger
g_loggingLevel = logging.getLevelName("INFO") #default logging level
logging.basicConfig(
    level=g_loggingLevel,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

#Global Variables
logger = logging.getLogger()
cfg_DryRun = False
cfg_EmptyRowDetectThreshold=1 #if we find this many rows with fewer than expected columns, we stop processing

# use credentials in client_secret to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)



#start script
logger.info("starting...")

def escapeChars(strings,escapeChar, inVal):
    outVal=inVal
    for s in strings:
        outVal=outVal.replace(s,escapeChar+s)
    return outVal

def escapeJML(inVal):
    return escapeChars("|{}[]", "\\", inVal)

def createUkMwtr(opportunityId, customerName, repEmail, articleCount, startDate, endDate, boolean, superAdminLink, sources, repName, orderNumber, location, boolean_2, sources_2, sourceSelection_2, sourceSelectionList_2): 
    global cfg_DryRun
      
    summary = "Activate UK Premium Print for Account %s" % (escapeJML(customerName))
    description="Please enable UK Print for the following Account: \n"
    description+="Account Name: %s \n" % (escapeJML(customerName))
    description+="Opportunity ID: %s \n" % (escapeJML(opportunityId))
    description+="Order Number: %s \n" % (escapeJML(orderNumber))
    description+="Client Account Link: %s \n" % (escapeJML(superAdminLink))
    description+="Sales Rep Email Address: %s \n" % (escapeJML(repEmail))
    description+="Name: %s \n" % (escapeJML(repName))
    description+="Article Count Remaining: %s \n" % (escapeJML(articleCount))
    description+="Contract Start Date: %s \n" % (escapeJML(startDate))
    description+="Contract End Date: %s \n" % (escapeJML(endDate))
    description+="Boolean Query: %s \n" % (escapeJML(boolean))
    description+="Article Type: %s \n" % (escapeJML(sources))
    description+="Location (UK or International): %s \n" % (escapeJML(location))
    description+="Do they want a custom Source Selection created?: %s \n" % (escapeJML(sourceSelection))
    description+="List of Custom Source Selection sources (if blank then no SS): %s \n" % (escapeJML(sourceSelectionList))
    description+="2nd Boolean Query (if applicable): %s \n" % (escapeJML(boolean_2))
    description+="2nd Boolean Article Type (if applicable): %s \n" % (escapeJML(sources_2))
    description+="2nd Boolean custom Source Selection? (if applicable): %s \n" % (escapeJML(sourceSelection_2))
    description+="List of 2nd Boolean Custom Source Selection sources (if blank then no SS): %s \n" % (escapeJML(sourceSelectionList_2))      
    description+="UK Print Activiation Details Here: https://docs.google.com/presentation/d/1ZoguqkIlWkGO1GoRFvoYd8i-edrKw7O6N-7-fxvuKrM/edit#slide=id.gfe17a91b6a_0_83"

    jParams = {
            "summary":summary,
            "description":description,
            "companyName":customerName,
            "superadminLink":superAdminLink,
            "emailNotifications":repEmail,
            "project":"MWTR",
            "issueType":"Support",
            "requestType":"mwtr/9ba57fc8-9a7f-4828-8d34-74774bf4248d", #Creating ticket as Request type "Content" based off this ID
            "contentSubRequestType":{"id":"32368"} # Trying to set Uk Print Content as the subrequest type
            }
    #Print out ticket details before creating
    logger.info("jParams=%s", jParams)


    if cfg_DryRun:
        logger.info("stopping early... dry run..")
        return #sys.exit(0)
    jResp={}
    issueKey=""
    logger.info('creating issue...')
    jResp = jiraUtil.jiraAddIssue(jParams)
    
    issueKey=jResp["key"]
    logger.info("response key= %s", issueKey)
    logger.debug("jResp=%s", jResp)
    return jResp

def createGermanMwtr(opportunityId, customerName, repEmail, articleCount, startDate, endDate, boolean, superAdminLink, sources, repName, pmgContractId, boolean_2, sources_2, sourceSelection_2, sourceSelectionList_2): 
    global cfg_DryRun
   
    summary = "Activate German Premium Print for Account %s" % (escapeJML(customerName))
    description="Please enable German Print for the following Account: \n"
    description+="Account Name: %s \n" % (escapeJML(customerName))
    description+="Opportunity ID: %s \n" % (escapeJML(opportunityId))
    description+="PMG Customer ID: %s \n" % (escapeJML(pmgContractId))
    description+="Client Account Link: %s \n" % (escapeJML(superAdminLink))
    description+="Sales Rep Email Address: %s \n" % (escapeJML(repEmail))
    description+="Name: %s \n" % (escapeJML(repName))
    description+="Article Count Remaining: %s \n" % (escapeJML(articleCount))
    description+="Contract Start Date: %s \n" % (escapeJML(startDate))
    description+="Contract End Date: %s \n" % (escapeJML(endDate))
    description+="Boolean Query: %s \n" % (escapeJML(boolean))
    description+="Article Type: %s \n" % (escapeJML(sources))
    description+="Do they want a custom Source Selection?: %s \n" % (escapeJML(sourceSelection))
    description+="List of Custom Source Selection sources (if blank then no SS): %s \n" % (escapeJML(sourceSelectionList))   
    description+="2nd Boolean Query (if applicable): %s \n" % (escapeJML(boolean_2))
    description+="2nd Boolean Article Type (if applicable): %s \n" % (escapeJML(sources_2))
    description+="2nd Boolean custom Source Selection? (if applicable): %s \n" % (escapeJML(sourceSelection_2))
    description+="List of 2nd Boolean Custom Source Selection sources (if blank then no SS): %s \n" % (escapeJML(sourceSelectionList_2))   
    description+="German Print Activiation Details Here: https://docs.google.com/presentation/d/1c3G7ZCdFpLYsnjaAs4fYs1t4QKubLNawAPUXn0Xniyc/edit#slide=id.g1447decc8bb_0_0" #NEED DOCUMENTATION FROM VINCENT

    jParams = {
            "summary":summary,
            "description":description,
            "companyName":customerName,
            "superadminLink":superAdminLink,
            "emailNotifications":repEmail,
            "project":"MWTR",
            "issueType":"Support",
            "requestType":"mwtr/9ba57fc8-9a7f-4828-8d34-74774bf4248d", #Creating ticket as Request type "Content" based off this ID
            "contentSubRequestType":{"id":"32369"} # Setting German Print Content as the subrequest type
            }
    #Print out ticket details before creating
    logger.info("jParams=%s", jParams)

    if cfg_DryRun:
        logger.info("stopping early... dry run..")
        return #sys.exit(0)
    jResp={}
    issueKey=""
    logger.info('creating issue...')
    jResp = jiraUtil.jiraAddIssue(jParams)
    
    issueKey=jResp["key"]
    logger.info("response key= %s", issueKey)
    logger.debug("jResp=%s", jResp)
    return jResp


# Find the UK Print workbook by name and open the first sheet
sheet = client.open("UK Print Order Form (Responses)").worksheet('Order confirmations')

# Extract and print values from sheet 1
index = 0 #starting at 0 will start at 1
row_count = int(sheet.row_count)
empty_row_sequential=0

#Begin scrolling through Uk Print Response sheet
logger.info("Starting UK Print Activation")
while True:
    index+=1 #increment our row index
    if index<=1: #skip header
        logger.info("skipping header row index #%s", index)
        continue
    if index>row_count: #detect that we are past the very end of the table... 
        logger.info("end of table detected at row index #%s (over row_count) - exiting loop", index)
        break #exit loop
    logger.info("reading row index #%s...",index)    
    row = sheet.row_values(index) #read the row
    #logger.info(row)
    logger.info(len(row))
    if len(row) < 10: #detect empty row situation - or just too few columns
        empty_row_sequential+=1
        logger.info("skipping row index #%s with no data (seq #%s)", index, empty_row_sequential) 
        if empty_row_sequential>=cfg_EmptyRowDetectThreshold:
            logger.info("end of table detected at row index #%s (blank sequential rows) - exiting loop", index)
            break
        continue #move to the next row
    #below this line we have a non-empty row...
    empty_row_sequential=0 #reset our sequential empty row counter
    if len(row)>=23 and len(row[22])>0: #detect completed row (i.e. has at least 22 columns and the 22nd column is not empty)
        logger.info(row[21])
        logger.info("skipping completed row index #%s", index)
        continue

    #Read in the next request where we have a non-empty, incomplete row...
    logger.info("processing row index #%s...", index)
    repName = row[1]
    opportunityId = row[3]
    customerName = row[4]
    orderNumber = row[5]
    articleCount = row[6]
    startDate = row[7]
    endDate = row[8]
    boolean = row[9]
    superAdminLink = row[10]
    sources = row[11]
    sourceSelection = row[12]
    sourceSelectionList = row[13]
    repEmail = row[15]
    location = row[21]
    boolean_2 = row[17]
    sources_2 = row[18]
    sourceSelection_2 = row[19]
    sourceSelectionList_2 = row[20]
    logger.info("calling jira createUkMwtr for index #%s...", index)
    response = createUkMwtr(opportunityId=opportunityId, customerName=customerName, orderNumber=orderNumber, repEmail=repEmail, articleCount=articleCount, startDate=startDate, endDate=endDate, boolean=boolean, superAdminLink=superAdminLink, sources=sources, repName=repName, location=location, boolean_2=boolean_2, sources_2=sources_2, sourceSelection_2=sourceSelection_2, sourceSelectionList_2=sourceSelectionList_2)
    logger.info("jira response for row index #%s = %s", index, response)
    issueKey=response["key"]
    completed_message = 'Ticket - %s' % (issueKey)
    logger.info("setting completed message for index #%s as %s", index, completed_message)
    sheet.update_cell(index, 23, completed_message)
    logger.info("completed row index #%s", index)

# Find the German Print Google workbook by name and open the first sheet
sheet = client.open("German Premium Content Order Form (Responses)").worksheet('Form Responses 1')

# Extract and print values from German Sheet
index = 0 #starting at 0 will start at 1
row_count = int(sheet.row_count)
empty_row_sequential=0

#Begin scrolling through German Print Response sheet
logger.info("Starting German Print Activation")
while True:
     index+=1 #increment our row index
     if index<=1: #skip header
         logger.info("skipping header row index #%s", index)
         continue
     if index>row_count: #detect that we are past the very end of the table... 
         logger.info("end of table detected at row index #%s (over row_count) - exiting loop", index)
         break #exit the loop
     logger.info("reading row index #%s...",index)    
     row = sheet.row_values(index) #read the row
     if len(row) < 17: #detect empty row situation - or just too few columns
         empty_row_sequential+=1
         logger.info("skipping row index #%s with no data (seq #%s)", index, empty_row_sequential) 
         if empty_row_sequential>=cfg_EmptyRowDetectThreshold:
             logger.info("end of table detected at row index #%s (blank sequential rows) - exiting loop", index)
             break #outa here
         continue #move to the next row
     #below this line we have a non-empty row...
     empty_row_sequential=0 #reset our sequential empty row counter
     if len(row)>=25 and len(row[24])>0: #detect completed row (i.e. has at least 8 columns and the 8th column is not empty)
         logger.info("skipping completed row index #%s", index)
         continue

     #below this line we have a non-empty, incomplete row...
     logger.info("processing row index #%s...", index)
     repName = row[1]
     repEmail = row[2]
     opportunityId = row[5]
     customerName = row[6]
     articleCount = row[8]
     startDate = row[9]
     endDate = row[10]
     boolean = row[11]
     superAdminLink = row[12]
     sources = row[13]
     sourceSelection = row[14]
     sourceSelectionList = row[15]
     boolean_2 = row[19]
     sources_2 = row[20]
     sourceSelection_2 = row[21]
     sourceSelectionList_2 = row[22]
     pmgContractId = row [23]
     logger.info("calling jira createGermanMwtr for index #%s...", index)
     response = createGermanMwtr(opportunityId=opportunityId, customerName=customerName, repEmail=repEmail, articleCount=articleCount, startDate=startDate, endDate=endDate, boolean=boolean, superAdminLink=superAdminLink, sources=sources, repName=repName, pmgContractId=pmgContractId, boolean_2=boolean_2, sources_2=sources_2, sourceSelection_2=sourceSelection_2, sourceSelectionList_2=sourceSelectionList_2)
     logger.info("jira response for row index #%s = %s", index, response)
     issueKey=response["key"]
     completed_message = 'Ticket - %s' % (issueKey)
     logger.info("setting completed message for German index #%s as %s", index, completed_message)
     sheet.update_cell(index, 25, completed_message)
     logger.info("completed row index #%s", index)

logger.info("completed script") 
