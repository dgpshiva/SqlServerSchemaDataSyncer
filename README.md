# SqlServerSchemaDataSync
If you are looking to do inhouse comparison and update between two sql server databases and do not want to go for a third party software or license, you can use the above scripts for the same.

Requirements:
1. Two Sql Servers, a Source server and a Target server (the sql servers can even be present on different machines)
   (I have tried this between Sql Servers 2012 vs 2012 and also between 2012 vs 2014)
2. Visual Studio 2012 with SQL Server Data Tools installed on the machine having the Target Sql server

This can be used to sync the schema and data between two sql server databases

Reference site : http://blogs.msdn.com/b/ssdt/archive/2014/07/15/msbuild-support-for-schema-compare-is-available.aspx

SSDT download : https://msdn.microsoft.com/en-us/jj650015
