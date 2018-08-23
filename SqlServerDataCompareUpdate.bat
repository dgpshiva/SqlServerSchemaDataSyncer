@ECHO OFF
SET sourceConnString=Data Source=localhost;Initial Catalog=iFind_Demo_UnitTest;Integrated Security=True;Pooling=False
SET targetConnString=Data Source=localhost;Initial Catalog=UDWStaging;Integrated Security=True;Pooling=False
SET MSBuildPath=C:\Windows\Microsoft.NET\Framework64\v4.0.30319
SET ProjectDir=D:\code\SqlServerSchemaDataSync\SQLServerProject\SQLServerProject
SET ReportPath=%1
SET LogPath=%2

REM SET ReportPath=D:\code\SqlServerSchemaDataSync\SchemaUpdateReports
REM SET LogPath=D:\code\SqlServerSchemaDataSync\SchemaUpdateLogs

echo start /b /wait "" "%MSBuildPath%\MSBuild.exe" "%ProjectDir%\SQLServerProject.sqlproj" /t:SqlSchemaCompare /p:source="%sourceConnString%" /p:target="%targetConnString%" /p:BlockOnPossibleDataLoss=FALSE /p:XmlOutput="%ReportPath%" /p:Deploy="true"

start /b /wait "" "%MSBuildPath%\MSBuild.exe" "%ProjectDir%\SQLServerProject.sqlproj" /t:SqlSchemaCompare /p:source="%sourceConnString%" /p:target="%targetConnString%" /p:BlockOnPossibleDataLoss=FALSE /p:XmlOutput="%ReportPath%" /p:Deploy="true" > "%LogPath%" /p:VisualStudioVersion=14.0

Exit /b [1]