@ECHO OFF
SET sourceConnString=Data Source=<Connection string to source db>
SET targetConnString=Data Source=<Connection string to target db>
SET MSBuildPath=C:\Windows\Microsoft.NET\Framework64\v4.0.30319
SET ProjectDir=<Path to .sqlproj file>
SET ReportPath=%1
SET LogPath=%2

echo start /b /wait "" "%MSBuildPath%\MSBuild.exe" "%ProjectDir%\SqlProjFileName.sqlproj" /t:SqlSchemaCompare /p:source="%sourceConnString%" /p:target="%targetConnString%" /p:BlockOnPossibleDataLoss=FALSE /p:XmlOutput="%ReportPath%" /p:Deploy="true"

start /b /wait "" "%MSBuildPath%\MSBuild.exe" "%ProjectDir%\SqlProjFileName.sqlproj" /t:SqlSchemaCompare /p:source="%sourceConnString%" /p:target="%targetConnString%" /p:BlockOnPossibleDataLoss=FALSE /p:XmlOutput="%ReportPath%" /p:Deploy="true" > "%LogPath%"

Exit /b [1]