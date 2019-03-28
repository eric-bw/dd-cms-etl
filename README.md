# dd-cms-etl

## Purpose
This package is built to package and deploy content across environments
. This is a two step process
1. first export the data from an environment using export.py into a xlsx package
2. transfer the xlsx package to a new environment

## Install Instructions
#### General
* install python 3.7+ (later versions are likely fine but this is only tested with python 3)
* download this package or clone it using git.
* unzip the zip file
* open your terminal and go to the folder where the scripts are contained
* install dependencies by calling 
   ```$ pip3 install -r requirements.txt```
* this script is written in python 3 and is not compatible with python 2
   
#### Windows Instructions
there are a few differences between Windows and OSX that it makes sense to address them separately.
* Windows does not have python installed by default
* if you go through the default install process the python PATH is not setup and you wont be able to access python from the command line

install steps for windows
1. download the 32 bit package from the python website. https://www.python.org/downloads/windows/ (latest python 3)
2. after downloading the exe, execute it 
3. select custom install 
![](https://docs.python.org/3/_images/win_installer.png "Custom Install")
4. select the following options and change the install path to c:\python37 for ease of reference sake. 
![](http://www.pitt.edu/~naraehan/python3/img/win-install3.png)
5. in a windows terminal go to the unzipped folder (ex $ cd ~/Downloads/dd-cms-etl)
6. execute scripts


#### Mac OSX instructions
Typically OSX already has python installed BUT python is mapped to python 2 you have to use python3 to execute a python 3 script.
1. where instructions say to use python, call python3 instead
2. where instructions say use pip, use pip3 instead.
   
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

```$ python transfer.py -i <input 'contentpak_<username>.<date>.zip'> -u <username> -p <password> -t <token> -s <is_sandbox? t/f>```
#### Params
-i **input: Required** the path to the content pack you want to import  
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
