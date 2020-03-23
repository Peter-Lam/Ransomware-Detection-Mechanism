To import this Kibana file
1.  Start you elastic search instance
2. Start Kibana instance
3. Open Kibana (localhost:5601)
4. Go to Management/Save Objects
5. Click Import
6. Load your data using powershell and elastic bulk api import command ```Invoke-RestMethod "http://localhost:9200/ioc/_bulk?pretty" -Method Post -ContentType 'application/x-ndjson' -InFile "..\Ransomware-Detection-Mechanism\src\data\inputs\ioc_list_final.json"```