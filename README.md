# dd-cms-etl

## Purpose
This package is built to package and deploy content across environments
. This is a two step process
1. first export the data from an environment using export.py into a xlsx package
2. transfer the xlsx package to a new environment

## Install Instructions
* install python 3(.7)
* download this package or clone it using git.
* open your terminal and go to the folder where the scripts are contained
* install dependencies by calling 
   ```$ pip3 install -r requirements.txt```
   
## export
call this script with the following parameters to generate a package. 
the output will be an excel file and a folder called files. The folder contains the image content.
```$ python export -u <username> -p <password> -t <token> -s <is_sandbox? t/f>```
   
## transfer
call this script with the following parameters to transfer a package to a new environment
```$ python transfer -i <input 'export.19-03-20.xlsx'> -u <username> -p <password> -t <token> -s t```
