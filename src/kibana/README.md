# Introduction
The following is guide to using the following python scripts located under ``/Ransomware-Detection-Mechanism/src/kibana/bulk_json_generator.py``
* bulk_json_generator.py
* bulk_json_refresher.py
* bulk_json_combiner.py

# Prerequisites
1. Install dependencies using `- pip install -r ./requirements.txt`

# Bulk JSON Generator
This is the main script for converting generating a JSON file that is readable through ElasticSearch's BULK API. This script will take a `.txt` consisting of a specific type of IoC and either create a new file or append to an existing BulkAPI JSON File.

## Usage
```
usage: bulk_json_generator.py [-h] (--new  | --update ) --text  --malware  --ioc_type  -src  [--date] [--rsa] [--epoch] [--silent]

Appending or creating new json files with new information

optional arguments:
  -h, --help        show this help message and exit
  --new             writes to the full path of desired json file (e.g. C:/GitHub-Projects/Ransomware-Detection-Mechanism/ioc_list.json
  --update          appends the existing BULK api json file with new data (e.g. C:/GitHub-Projects/Ransomware-Detection-Mechanism/ioc_list.json
  --text            text file containing values of the iocs
  --malware         type of malware (e.g. Trickbot)
  --ioc_type        type of ioc (MD5|SHA256|IP|URL|DOMAIN|other)
  -src , --source   Source of malware dataset(e.g. www.virusshare.com)
  --date            Optional - date of when IOC was collected (MM/DD/YYYY)
  --rsa             Optional - the RSA key of the IOC
  --epoch           Optional - the epoch number of the IOC (e.g. 1)
  --silent          Optional - Silent mode for reduced system logs
```

## Example
```
python .\bulk_json_generator.py  --update F:\GitHub-Projects\Ransomware-Detection-Mechanism\src\data\inputs\existing_file.json --text C:\Users\peter\Desktop\temp.txt --malware emotet -src https://paste.cryptolaemus.com/emotet/2020/02/07/09-emotet-malware-IoCs_02-07-09-20.html --date 02/05/2020 --epoch 3 --ioc_type SHA256                                                
```

**Note: Each IoC must be seperated by a new line within the text file for the script to run**

Example: temp.txt
```
04a447159355a9910c53ca5d9ac22cd37183611b1f70979342b4980362936ce9
082a3c205aad68e7f8c96cdd2d2efb1b6bf4c4ab2ef27e281adb8564d40447d6
0dcc63432d1c79cd46bbae2af17c856ccf14d669abfd200c5d21ec050dbac004
0fffa97cfc98d6ddd11b19d1d04930015a9170427e5fd47ae409ef59fbe7270e
1065371a2d78cd0aab5f8bf32772f611df9ef917c441a35bb0a84d051c8647f2

```
# Bulk JSON Refresher
This script is used to update an existing BulkAPI JSON with the latest information from VirusTotal, IPInfo, and Cymruwhois.

## Usage
```
usage: bulk_json_refresher.py [-h] -path

Updating/Refreshing existing JSON latest API information

optional arguments:
  -h, --help       show this help message and exit
  -path , --path   Path to bulk api JSON to be updated (e.g. C:/GitHub-Projects/Ransomware-Detection-Mechanism/ioc_list.json
```
## Example
```
python .\bulk_json_refresher.py --path F:\GitHub-Projects\Ransomware-Detection-Mechanism\src\data\inputs\ioc_list_final.json
```
# Bulk JSON Combiner
This script is used to combine two existing BulkAPI JSONs.  If a destination is not selected by the user, the combined result will be saved to the first JSON.

## Usage
```
usage: bulk_json_combiner.py [-h] -a  -b  [-dest]
optional arguments:
  -h, --help       show this help message and exit
  -a , --file_1    Path to first bulk api JSON to be combined (e.g. ../Ransomware-Detection-Mechanism/ioc_list.json
  -b , --file_2    Path to second bulk api JSON to be combined (e.g. ../Ransomware-Detection-Mechanism/ioc_list.json
  -dest , --dest   Destination of combined file, if this argument is not used, the second file will be combined on the first file -- (e.g. ../Ransomware-Detection-Mechanism/ioc_list.json  
```

## Example
```
python .\bulk_json_combiner.py -a F:\GitHub-Projects\Ransomware-Detection-Mechanism\src\data\inputs\ioc_list_final.json -b 
F:\GitHub-Projects\Ransomware-Detection-Mechanism\src\data\inputs\ioc_emotet_copy.json -dest F:\GitHub-Projects\Ransomware-Detection-Mechanism\src\data\inputs\complete_ioc_list.json    
```