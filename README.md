# dd-cms-etl

## Purpose
This package is built to package and deploy content across environments
. This is a two step process
1. first export the data from an environment using export.py into a xlsx package
2. transfer the xlsx package to a new environment

## Install Instructions
* install python 3.7
* download this package or clone it using git.
* open your terminal and go to the folder where the scripts are contained
* install dependencies by calling 
   ```$ pip3 install -r requirements.txt```
   
## export
call this script with the following parameters to generate a package. 
the output will be an excel file and a folder called files. The folder contains the image content. *<> means user provided values.

```$ python export.py -u <username> -p <password> -t <token> -s <is_sandbox? t/f>```

#### Params
-u **username: Required** Salesforce environment username  
-p **password: Required** Salesforce environment password  
-t **Token: Required**   A salesforce token is a second passowrd that is required to access the Salesforce API. If you dont have it go to Settings > Reset Security Token and a new token will be emailed to you  
-s **Sandbox: Required** put 't' or 'true' if connection to a sandbox, put false if connecting to production

## transfer
call this script with the following parameters to transfer a package to a new environment

```$ python transfer.py -i <input 'export.19-03-20.xlsx'> -u <username> -p <password> -t <token> -s <is_sandbox? t/f>```
#### Params
-i **input: Required** the name of the file you want to import  
-u **username: Required** Target Salesforce environment username   
-p **password: Required** Target Salesforce environment password  
-t **Token: Required**   A salesforce token is a second passowrd that is required to access the Salesforce API. If you dont have it go to Settings > Reset Security Token and a new token will be emailed to you  
-s **Sandbox: Required** put 't' or 'true' if connection to a sandbox, put false if connecting to production  
-l **Level: Optional** <Number> control what gets transferred  
```
Level 1: transfer files
Level 2: transfer pages
Level 3: transfer content
Level 4: transfer assets
```
