import os
import pyodbc
import shutil
import subprocess
import sys
import time

try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk


# Current DateTime
currDateTime = (time.strftime("%d/%m/%Y %H:%M:%S")).replace('/', '').replace(':', '').replace(' ', '_')

# Path to current dir
scriptLoc = os.path.dirname(os.path.abspath(__file__))

# Creating a logging file for this script
if not os.path.exists("./ScriptLogs"):
	os.makedirs("./ScriptLogs")
scriptLogFile = open(scriptLoc+"\\ScriptLogs\\SqlServerDataCompareUpdateLog"+currDateTime+".log", 'w')

scriptLogFile.write("Start time: " + currDateTime + "\n\n")

# Initial Settings
schemaUpateScriptName = "SqlServerDataCompareUpdate.bat"
tableDiffLoc = "C:\\Program Files\\Microsoft SQL Server\\110\\COM"
sqlCmdLoc = "C:\\Program Files\\Microsoft SQL Server\\110\\Tools\\Binn"
sourceServer = "<source_server_name>"
sourceDBName = "<source_db_name>"
targetServer = "<target_server_name>"
targetDBName = "<target_db_name>"
scriptLogFile.write("Initial settings:\n\n")
scriptLogFile.write("Schema Update Script Name: "+schemaUpateScriptName+"\n")
scriptLogFile.write("tablediff.exe location: "+tableDiffLoc+"\n")
scriptLogFile.write("sqlcmd.exe location: "+sqlCmdLoc+"\n")
scriptLogFile.write("Source server: "+sourceServer+"\n")
scriptLogFile.write("Source Database: "+sourceDBName+"\n")
scriptLogFile.write("Target server: "+targetServer+"\n")
scriptLogFile.write("Target Database: "+targetDBName+"\n\n")

# Creating required directory structure
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


# Schema Update
schemaUpdateReportFileName = scriptLoc+"\\SchemaUpdateReports\\SchemaUpdateReport"+currDateTime+".xml"
schemaUpdateLogFileName = scriptLoc+"\\SchemaUpdateLogs\\SchemaUpdateLog"+currDateTime+".log"
if not os.path.exists(scriptLoc+"\\"+schemaUpateScriptName):
	scriptLogFile.write("Missing "+schemaUpateScriptName+" script!\n\n")
	sys.exit()
s = subprocess.Popen(scriptLoc+"\\"+schemaUpateScriptName+" "+schemaUpdateReportFileName+" "+schemaUpdateLogFileName, shell=True, stdout=subprocess.PIPE)
stdout, stderr = s.communicate()
scriptLogFile.write(schemaUpateScriptName+" has been executed!\nCheck " + schemaUpdateLogFileName + " logs to verify all went well.\n\n")


# Data Compare and Update
try:
	DBcnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+targetServer+';DATABASE='+targetDBName+';Trusted_Connection=yes')
	DBcursor = DBcnxn.cursor()
	DBcnxnForAltTbl = pyodbc.connect('DRIVER={SQL Server};SERVER='+targetServer+';DATABASE='+targetDBName+';Trusted_Connection=yes')
	DBcursorForAltTbl = DBcnxnForAltTbl.cursor()
except Exception, ex:
	scriptLogFile.write("Failed to connect to target server.\nError message: " + str(ex) + "\n\n")
	sys.exit()

# Data Compare
if not os.path.exists(tableDiffLoc+'\\tablediff.exe'):
	scriptLogFile.write("tablediff.exe not found at the specified location!\n\n")
	sys.exit()

baseLocCompare = scriptLoc+"\\DataCompare"
dataCompareSqlLoc = baseLocCompare+"\\Sqls\\"
dataCompareSqlBkpLoc = baseLocCompare+"\\SqlsBkp\\"
dataCompareLogLoc = baseLocCompare+"\\Logs\\"
dataCompareLogBkpLoc = baseLocCompare+"\\LogsBkp\\"

# Clearing the Sqls and Logs folder
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

#  Creating a file to record table names in current schema
if os.path.exists(baseLocCompare+'\\TableNames.txt'):
	os.remove(baseLocCompare+'\\TableNames.txt')
tableNamesFile = open(baseLocCompare+'\\TableNames.txt', 'w')

if os.path.exists(baseLocCompare+'\\TableDiffScriptFile.bat'):
	os.remove(baseLocCompare+'\\TableDiffScriptFile.bat')
TableDiffScriptFile = open(baseLocCompare+'\\TableDiffScriptFile.bat', 'w')

for row in DBcursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG= ? AND TABLE_TYPE='BASE TABLE'", targetDBName):
	tableNamesFile.write("SELECT * FROM "+sourceDBName+".dbo.["+row.TABLE_NAME+"] EXCEPT SELECT * FROM "+targetDBName+".dbo.["+row.TABLE_NAME+"];\n")
	TableDiffScriptFile.write("\""+tableDiffLoc+"\\tablediff.exe"+"\" -sourceserver "+sourceServer+" -sourcedatabase "+sourceDBName+" -sourcetable "+row.TABLE_NAME+" -destinationserver "+targetServer+" -destinationdatabase "+targetDBName+" -destinationtable "+row.TABLE_NAME+" -f "+dataCompareSqlLoc+row.TABLE_NAME+".sql"+" -o "+dataCompareLogLoc+row.TABLE_NAME+".log\n")
TableDiffScriptFile.close()

if TableDiffScriptFile.closed:
	p = subprocess.Popen(baseLocCompare+'\\TableDiffScriptFile.bat', shell=True, stdout=subprocess.PIPE)
	stdout, stderr = p.communicate()
if p.returncode == 0:
	tableDiffScriptStatus = "Success"
else:
	tableDiffScriptStatus = "Fail"
	scriptLogFile.write("Diff for one or more tables might not have executed properly.\nCheck " + dataCompareLogBkpLoc + " logs for details.\n\n")

# Backing up Log files
for entry in scandir(dataCompareLogBkpLoc):
	if os.path.isfile(dataCompareLogBkpLoc+"\\"+entry.name):
		os.remove(dataCompareLogBkpLoc+"\\"+entry.name)
	elif os.path.isdir(dataCompareLogBkpLoc+"\\"+entry.name):
		shutil.rmtree(dataCompareLogBkpLoc+"\\"+entry.name)
for entry in scandir(dataCompareLogLoc):
	shutil.move(dataCompareLogLoc+"\\"+entry.name, dataCompareLogBkpLoc+"\\"+entry.name.replace(".log", "")+currDateTime+".log")



# Data Update
if not os.path.exists(sqlCmdLoc+'\\sqlcmd.exe'):
	scriptLogFile.write("sqlCmdLoc.exe not found at the specified location!\n\n")
	sys.exit()

baseLocUpdate = scriptLoc+"\\DataUpdate"
dataUpdateLogLoc = baseLocUpdate+"\\Logs\\"
dataUpdateLogBkpLoc = baseLocUpdate+"\\LogsBkp\\"

# Clearing the Logs folder
for entry in scandir(dataUpdateLogLoc):
	if os.path.isfile(dataUpdateLogLoc+"\\"+entry.name):
		os.remove(dataUpdateLogLoc+"\\"+entry.name)
	elif os.path.isdir(dataUpdateLogLoc+"\\"+entry.name):
		shutil.rmtree(dataUpdateLogLoc+"\\"+entry.name)

if os.path.exists(baseLocUpdate+'\\DataUpdateScriptFile.bat'):
	os.remove(baseLocUpdate+'\\DataUpdateScriptFile.bat')
DataUpdateScriptFile = open(baseLocUpdate+'\\DataUpdateScriptFile.bat', 'w')

for entry in scandir(dataCompareSqlLoc):
	if entry.is_file() and os.path.splitext(entry.name)[1].lower()==".sql":
		DataUpdateScriptFile.write("\""+sqlCmdLoc+"\\sqlcmd.exe\" -S "+targetServer+" -d "+targetDBName+" -i "+dataCompareSqlLoc+entry.name+" -o "+dataUpdateLogLoc+os.path.splitext(entry.name)[0]+".log\n")
DataUpdateScriptFile.close()

# Temporarily disabling constraints on tables so that update scripts can update the data
for row in DBcursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG= ? AND TABLE_TYPE='BASE TABLE'", targetDBName):
	sqlCmd = "ALTER TABLE ["+row.TABLE_NAME+"] nocheck constraint all"
	DBcursorForAltTbl.execute(sqlCmd)
DBcnxnForAltTbl.commit()

if DataUpdateScriptFile.closed:
	q = subprocess.Popen(baseLocUpdate+'\\DataUpdateScriptFile.bat', shell=True, stdout=subprocess.PIPE)
	stdout, stderr = q.communicate()
if q.returncode == 0:
	dataUpdateScriptStatus = "Success"
else:
	dataUpdateScriptStatus = "Fail"
	scriptLogFile.write("One or more table data might not have updated properly\nCheck " + dataUpdateLogBkpLoc + " logs for details.\n\n")

# Re-enabling constraints on the tables
for row in DBcursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG= ? AND TABLE_TYPE='BASE TABLE'", targetDBName):
	sqlCmd = "ALTER TABLE ["+row.TABLE_NAME+"] check constraint all"
	DBcursorForAltTbl.execute(sqlCmd)

# Backing up Log files
for entry in scandir(dataUpdateLogBkpLoc):
	if os.path.isfile(dataUpdateLogBkpLoc+"\\"+entry.name):
		os.remove(dataUpdateLogBkpLoc+"\\"+entry.name)
	elif os.path.isdir(dataUpdateLogBkpLoc+"\\"+entry.name):
		shutil.rmtree(dataUpdateLogBkpLoc+"\\"+entry.name)
for entry in scandir(dataUpdateLogLoc):
	shutil.move(dataUpdateLogLoc+"\\"+entry.name, dataUpdateLogBkpLoc+"\\"+entry.name.replace(".log", "")+currDateTime+".log")

# Backing up Sql files
for entry in scandir(dataCompareSqlBkpLoc):
	if os.path.isfile(dataCompareSqlBkpLoc+"\\"+entry.name):
		os.remove(dataCompareSqlBkpLoc+"\\"+entry.name)
	elif os.path.isdir(dataCompareSqlBkpLoc+"\\"+entry.name):
		shutil.rmtree(dataCompareSqlBkpLoc+"\\"+entry.name)
for entry in scandir(dataCompareSqlLoc):
	shutil.move(dataCompareSqlLoc+"\\"+entry.name, dataCompareSqlBkpLoc+"\\"+entry.name.replace(".sql", "")+currDateTime+".sql")


DBcursorForAltTbl.close()
del DBcursorForAltTbl
DBcnxnForAltTbl.commit()
DBcnxnForAltTbl.close()

DBcursor.close()
del DBcursor
DBcnxn.commit()
DBcnxn.close()

tableNamesFile.close()

scriptLogFile.write("End of script. Script has run successfully! Have a good day! \n\n")
scriptLogFile.write("End time: " + currDateTime + "\n\n")
scriptLogFile.close()
