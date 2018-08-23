@ECHO OFF
SET sourceConnString=Data Source=<source_server_name>;Initial Catalog=<source_db_name>;Integrated Security=True;Pooling=False
SET targetConnString=Data Source=<target_server_name>;Initial Catalog=<target_db_name>;Integrated Security=True;Pooling=False
SET MSBuildPath=C:\Windows\Microsoft.NET\Framework64\v4.0.30319
SET ProjectPath=<path to .sqlproj>
SET ReportPath=%1
SET LogPath=%2

echo start /b /wait "" "%MSBuildPath%\MSBuild.exe" "%ProjectPath%" /t:SqlSchemaCompare /p:source="%sourceConnString%" /p:target="%targetConnString%" /p:BlockOnPossibleDataLoss=FALSE /p:XmlOutput="%ReportPath%" /p:Deploy="true"

start /b /wait "" "%MSBuildPath%\MSBuild.exe" "%ProjectPath%" /t:SqlSchemaCompare /p:source="%sourceConnString%" /p:target="%targetConnString%" /p:BlockOnPossibleDataLoss=FALSE /p:XmlOutput="%ReportPath%" /p:Deploy="true" > "%LogPath%" /p:VisualStudioVersion=14.0

Exit /b [1]
