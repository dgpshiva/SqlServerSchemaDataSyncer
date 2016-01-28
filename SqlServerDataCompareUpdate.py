import os
import pyodbc
import subprocess
import sys
import time

try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk


#Getting TimeStamp
currDateTime = (time.strftime("%d/%m/%Y %H:%M:%S")).replace('/', '').replace(':', '').replace(' ', '_')

#Getting location where script has been placed
scriptLoc = os.path.dirname(os.path.abspath(__file__))

#Creating a logging file for this script
scriptLogFile = open(scriptLoc+"\\ScriptLogs\\SqlServerDataCompareUpdateLog"+currDateTime+".log", 'w')

#Initial Settings
schemaUpateScriptName = "SqlServerSchemaUpdateLocal.bat"
tableDiffLoc = "C:\\Program Files\\Microsoft SQL Server\\110\\COM"
sqlCmdLoc = "C:\\Program Files\\Microsoft SQL Server\\110\\Tools\\Binn"
sourceServer = "source server name"
sourceDBName = "source db name"
targetServer = "target server name"
targetDBName = "target db name"
scriptLogFile.write("Initial settings:\n\n")
scriptLogFile.write("Schema Update Script Name: "+schemaUpateScriptName)
scriptLogFile.write("tablediff.exe location: "+tableDiffLoc)
scriptLogFile.write("splcmd.exe location: "+sqlCmdLoc)
scriptLogFile.write("Source server: "+sourceServer+"\n\n")
scriptLogFile.write("Source Database: "+sourceDBName+"\n\n")
scriptLogFile.write("Target server: "+targetServer+"\n\n")
scriptLogFile.write("Target Database: "+targetDBName+"\n\n")





#Creating required directory structure if it has been disturbed
if not os.path.exists("./ScriptLogs"):
	os.makedirs("./ScriptLogs")

if not os.path.exists("./SchemaUpdateReports"):
	os.makedirs("./SchemaUpdateReports")
if not os.path.exists("./SchemaUpdateLogs"):
	os.makedirs("./SchemaUpdateLogs")

if not os.path.exists("./DataCompare"):
	os.makedirs("./DataCompare")
if not os.path.exists("./DataCompare/Logs"):
	os.makedirs("./DataCompare/Logs")
if not os.path.exists("./DataCompare/LogsBkp"):
	os.makedirs("./DataCompare/LogsBkp")
if not os.path.exists("./DataCompare/Sqls"):
	os.makedirs("./DataCompare/Sqls")
if not os.path.exists("./DataCompare/SqlsBkp"):
	os.makedirs("./DataCompare/SqlsBkp")

if not os.path.exists("./DataUpdate"):
	os.makedirs("./DataUpdate")
if not os.path.exists("./DataUpdate/Logs"):
	os.makedirs("./DataUpdate/Logs")
if not os.path.exists("./DataUpdate/LogsBkp"):
	os.makedirs("./DataUpdate/LogsBkp")





#Schema Update
#Getting path to required folders
schemaUpdateReportFileName = scriptLoc+"\\SchemaUpdateReports\\SchemaUpdateReport"+currDateTime+".xml"
schemaUpdateLogFileName = scriptLoc+"\\SchemaUpdateLogs\\SchemaUpdateLog"+currDateTime+".log"

scriptLogFile.write("Schema Update Script Name: "+schemaUpateScriptName+"\n\n")
if not os.path.exists(scriptLoc+"\\"+schemaUpateScriptName):
	scriptLogFile.write("Missing "+schemaUpateScriptName+" script!\n\n")
	sys.exit()
else:
	scriptLogFile.write("Schema Update Script "+schemaUpateScriptName+" found!\n\n")
s = subprocess.Popen(scriptLoc+"\\"+schemaUpateScriptName+" "+schemaUpdateReportFileName+" "+schemaUpdateLogFileName, shell=True, stdout=subprocess.PIPE)
stdout, stderr = s.communicate()
scriptLogFile.write(schemaUpateScriptName+" has been executed! Check its log file to verify all went well!\n\n")





#Data Compare and Update
#Connection to target server
DBcnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+targetServer+';DATABASE='+targetDBName+';Trusted_Connection=yes')
DBcursor = DBcnxn.cursor()
DBcnxnForAltTbl = pyodbc.connect('DRIVER={SQL Server};SERVER='+targetServer+';DATABASE='+targetDBName+';Trusted_Connection=yes')
DBcursorForAltTbl = DBcnxnForAltTbl.cursor()
scriptLogFile.write("Connection to target SQL server established!\n\n")



#Data Compare
#Getting path to tablediff.exe
scriptLogFile.write("TableDiff.exe location: "+tableDiffLoc+"\n\n")
if not os.path.exists(tableDiffLoc+'\\tablediff.exe'):
	scriptLogFile.write("tablediff.exe not found at the specified location!\n\n")
	sys.exit()

#Getting paths to required folders
baseLocCompare = scriptLoc+"\\DataCompare"
dataCompareSqlLoc = baseLocCompare+"\\Sqls\\"
dataCompareSqlBkpLoc = baseLocCompare+"\\SqlsBkp\\"
dataCompareLogLoc = baseLocCompare+"\\Logs\\"
dataCompareLogBkpLoc = baseLocCompare+"\\LogsBkp\\"

#Clearing the Sqls and Logs folder
for entry in scandir(dataCompareSqlLoc):
	if os.path.isfile(dataCompareSqlLoc+"\\"+entry.name):
		os.remove(dataCompareSqlLoc+"\\"+entry.name)
	elif os.path.isdir(dataCompareSqlLoc+"\\"+entry.name):
		shutil.rmtree(dataCompareSqlLoc+"\\"+entry.name)
for entry in scandir(dataCompareLogLoc):
	if os.path.isfile(dataCompareLogLoc+"\\"+entry.name):
		os.remove(dataCompareLogLoc+"\\"+entry.name)
	elif os.path.isdir(dataCompareLogLoc+"\\"+entry.name):
		shutil.rmtree(dataCompareLogLoc+"\\"+entry.name)
scriptLogFile.write("The Sqls and Logs folders have been cleared.\n\n")

#Creating a file to record table names in current schema
if os.path.exists(baseLocCompare+'\\TableNames.txt'):
	os.remove(baseLocCompare+'\\TableNames.txt')
tableNamesFile = open(baseLocCompare+'\\TableNames.txt', 'w')

#Creating the TableDiffScriptFile.bat file
if os.path.exists(baseLocCompare+'\\TableDiffScriptFile.bat'):
	os.remove(baseLocCompare+'\\TableDiffScriptFile.bat')
tableDiffScriptFile = open(baseLocCompare+'\\TableDiffScriptFile.bat', 'w')

#Writing into the TableDiffScriptFile.bat file
for row in DBcursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG= ? AND TABLE_TYPE='BASE TABLE'", targetDBName):
	tableNamesFile.write("SELECT * FROM "+sourceDBName+".dbo.["+row.TABLE_NAME+"] EXCEPT SELECT * FROM "+targetDBName+".dbo.["+row.TABLE_NAME+"];\n");
	tableDiffScriptFile.write("\""+tableDiffLoc+"\\tablediff.exe"+"\" -sourceserver "+sourceServer+" -sourcedatabase "+sourceDBName+" -sourcetable "+row.TABLE_NAME+" -destinationserver "+targetServer+" -destinationdatabase "+targetDBName+" -destinationtable "+row.TABLE_NAME+" -f "+dataCompareSqlLoc+row.TABLE_NAME+".sql"+" -o "+dataCompareLogLoc+row.TABLE_NAME+".log\n")
tableDiffScriptFile.close()
scriptLogFile.write(baseLocCompare+"\\TableDiffScriptFile.bat has been created!\n\n")

#Executing the TableDiffScriptFile.bat script
if tableDiffScriptFile.closed:
	p = subprocess.Popen(baseLocCompare+'\\TableDiffScriptFile.bat', shell=True, stdout=subprocess.PIPE)
	stdout, stderr = p.communicate()
if p.returncode == 0:
	tableDiffScriptStatus = "Success"
else:
	tableDiffScriptStatus = "Fail"
scriptLogFile.write(baseLocCompare+"\\TableDiffScriptFile.bat has been executed! Status: "+str(p.returncode)+tableDiffScriptStatus+"\n\n")

#Backing up Data Compare log files
for entry in scandir(dataCompareLogBkpLoc):
	if os.path.isfile(dataCompareLogBkpLoc+"\\"+entry.name):
		os.remove(dataCompareLogBkpLoc+"\\"+entry.name)
	elif os.path.isdir(dataCompareLogBkpLoc+"\\"+entry.name):
		shutil.rmtree(dataCompareLogBkpLoc+"\\"+entry.name)
for entry in scandir(dataCompareLogLoc):
	import shutil
	shutil.move(dataCompareLogLoc+"\\"+entry.name, dataCompareLogBkpLoc+"\\"+entry.name.replace(".log", "")+currDateTime+".log")
scriptLogFile.write("The Data Compare log files have been backed up.\n\n")




#Data Update
#Getting path to sqlcmd.exe
scriptLogFile.write("sqlcmd.exe location: "+sqlCmdLoc+"\n\n")
if not os.path.exists(sqlCmdLoc+'\\sqlcmd.exe'):
	scriptLogFile.write("sqlCmdLoc.exe not found at the specified location!\n\n")
	sys.exit()

#Getting path to required folders
baseLocUpdate = scriptLoc+"\\DataUpdate"
dataUpdateLogLoc = baseLocUpdate+"\\Logs\\"
dataUpdateLogBkpLoc = baseLocUpdate+"\\LogsBkp\\"

#Clearing the Logs folder
for entry in scandir(dataUpdateLogLoc):
	if os.path.isfile(dataUpdateLogLoc+"\\"+entry.name):
		os.remove(dataUpdateLogLoc+"\\"+entry.name)
	elif os.path.isdir(dataUpdateLogLoc+"\\"+entry.name):
		shutil.rmtree(dataUpdateLogLoc+"\\"+entry.name)
scriptLogFile.write("The Logs folder has been cleared.\n\n")

#Creating the DataUpdateScriptFile.bat file
if os.path.exists(baseLocUpdate+'\\DataUpdateScriptFile.bat'):
	os.remove(baseLocUpdate+'\\DataUpdateScriptFile.bat')
DataUpdateScriptFile = open(baseLocUpdate+'\\DataUpdateScriptFile.bat', 'w')

#Writing into the DataUpdateScriptFile.bat file
for entry in scandir(dataCompareSqlLoc):
	if entry.is_file() and os.path.splitext(entry.name)[1].lower()==".sql":
		DataUpdateScriptFile.write("\""+sqlCmdLoc+"\\sqlcmd.exe\" -S "+targetServer+" -d "+targetDBName+" -i "+dataCompareSqlLoc+entry.name+" -o "+dataUpdateLogLoc+os.path.splitext(entry.name)[0]+".log\n")
DataUpdateScriptFile.close()
scriptLogFile.write(baseLocUpdate+"\\DataUpdateScriptFile.bat has been created!\n\n")

#Removing constraints from tables so that update scripts can run properly
for row in DBcursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG= ? AND TABLE_TYPE='BASE TABLE'", targetDBName):
	sqlCmd = "ALTER TABLE ["+row.TABLE_NAME+"] nocheck constraint all"
	DBcursorForAltTbl.execute(sqlCmd)
DBcnxnForAltTbl.commit()

#Executing the DataUpdateScriptFile.bat script
if DataUpdateScriptFile.closed:
	q = subprocess.Popen(baseLocUpdate+'\\DataUpdateScriptFile.bat', shell=True, stdout=subprocess.PIPE)
	stdout, stderr = q.communicate()
if q.returncode == 0:
	dataUpdateScriptStatus = "Success"
else:
	dataUpdateScriptStatus = "Fail"
scriptLogFile.write(baseLocUpdate+"\\DataUpdateScriptFile.bat has been executed! Status: "+dataUpdateScriptStatus+"\n\n")
scriptLogFile.write("Script has successfully completed running!!\n\n")

#Reapplying constraints on the tables
for row in DBcursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG= ? AND TABLE_TYPE='BASE TABLE'", targetDBName):
	sqlCmd = "ALTER TABLE ["+row.TABLE_NAME+"] check constraint all"
	DBcursorForAltTbl.execute(sqlCmd)

#Backing up Data Update log files created
for entry in scandir(dataUpdateLogBkpLoc):
	if os.path.isfile(dataUpdateLogBkpLoc+"\\"+entry.name):
		os.remove(dataUpdateLogBkpLoc+"\\"+entry.name)
	elif os.path.isdir(dataUpdateLogBkpLoc+"\\"+entry.name):
		shutil.rmtree(dataUpdateLogBkpLoc+"\\"+entry.name)
for entry in scandir(dataUpdateLogLoc):
	import shutil
	shutil.move(dataUpdateLogLoc+"\\"+entry.name, dataUpdateLogBkpLoc+"\\"+entry.name.replace(".log", "")+currDateTime+".log")
scriptLogFile.write("The Data Update log files have been backed up.\n\n")

#Backing up Data Compare sql files created
for entry in scandir(dataCompareSqlBkpLoc):
	if os.path.isfile(dataCompareSqlBkpLoc+"\\"+entry.name):
		os.remove(dataCompareSqlBkpLoc+"\\"+entry.name)
	elif os.path.isdir(dataCompareSqlBkpLoc+"\\"+entry.name):
		shutil.rmtree(dataCompareSqlBkpLoc+"\\"+entry.name)
for entry in scandir(dataCompareSqlLoc):
	import shutil
	shutil.move(dataCompareSqlLoc+"\\"+entry.name, dataCompareSqlBkpLoc+"\\"+entry.name.replace(".sql", "")+currDateTime+".sql")
scriptLogFile.write("The Data Compare sql files have been backed up.\n\n")





scriptLogFile.write("End of script. Script has run successfully. Have a good day! \n\n")


#Closing open files
tableNamesFile.close()
scriptLogFile.close()

#Deleting the sql cursor, commiting and closing the SQL server connection
DBcursorForAltTbl.close()
del DBcursorForAltTbl
DBcnxnForAltTbl.commit()
DBcnxnForAltTbl.close()

DBcursor.close()
del DBcursor
DBcnxn.commit()
DBcnxn.close()