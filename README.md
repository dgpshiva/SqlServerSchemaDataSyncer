# SqlServerSchemaDataSyncer

This repository contains code that can be used to sync the schema and data between two sql server databases.

## Table of content
- [Requirements to run the code](#requirements-to-run-the-code)
- [Running the code](#running-the-code)
- [Known issues](#known-issues)
- [References](#references)

## Requirements to run the code
- Microsoft Visual Studio with Sql Server Data Tools installed
  This code has been tested with Visual Studio 2012 and 2017
  [SSDT VS 2017](https://docs.microsoft.com/en-us/sql/ssdt/download-sql-server-data-tools-ssdt?view=sql-server-2017)
  [SSDT VS 2012](https://msdn.microsoft.com/en-us/jj650015)
- tablediff.exe
  (This comes with SQL Server installation and usually found at "C:\\Program Files\\Microsoft SQL Server\\<version_number>\\COM")
- sqlcmd.exe
  (This comes with SQL Server installation and usually found at "C:\\Program Files\\Microsoft SQL Server\\<version_number>\\Tools\\Binn")

## Running the code
- Open your version of Microsoft Visual Studio
- Create a new SQL Server project
  (In VS 2017: File -> New -> Project -> Other Languages -> SQL Server)
- Make note of location where project is saved
- Pull the code from branch [master](https://github.com/dgpshiva/SqlServerSchemaDataSyncer) of this repository
- Open the file [SqlServerDataCompareUpdate.py](./SqlServerDataCompareUpdate.py)
- Update the "Initial Settings" section
  Line 29 (Update location to your tablediff.exe)
  Line 30 (Update location to your sqlcmd.exe)
  Lines 31 - 34 (Source and Target server and database names)
- Update Lines 80 and 82 with your SQL Server Driver name (if it is not "SQL Server")
- Open the file [SqlServerDataCompareUpdate.bat](./SqlServerDataCompareUpdate.bat)
- Update Line 2 (SQL Server connection string to Source database)
- Update Line 3 (SQL Server connection string to Target database)
  (Sample connection string format: "Data Source=<server_name>;Initial Catalog=<database_name>;User ID=<username>;Password=<password>;")
- Update Line 4 (Path to MSBuild)
  (Default path to .NET 4 is used in the script: "C:\Windows\Microsoft.NET\Framework64\v4.0.30319")
  (Change if your path is different)
- Update Line 5 with complete path to the SQL Server project created above
  ("Path to SQL Server Project\<Project_name.sqlproj>")
- Run the python code [SqlServerDataCompareUpdate.py](./SqlServerDataCompareUpdate.py) using the command `python SqlServerDataCompareUpdate.py`
- This should sync the schema and data between the Source and Target SQL Server databases

## Known issues
- If a table does not have a primary key, identity, rowguid or unique key column, the data update might not work properly
- If the logs under "ScriptLogs" folder show an error check the logs under "DataCompare\LogsBkp" folder for details

## References
- [SQL Server Data Tools Team Blog](http://blogs.msdn.com/b/ssdt/archive/2014/07/15/msbuild-support-for-schema-compare-is-available.aspx)


![Alt Text](./SQLServerSchemaDataSyncer.gif)
