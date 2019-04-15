# dd-cms-etl - V1.12

## Purpose
This package is built to package and deploy content across environments
. This is a two step process
1. first export the data from an environment using export.py into a xlsx package
2. transfer the xlsx package to a new environment

## Usage note:
In order to succesfully transfers a contentpak you need to have the System Administrator profile or profile that has visiblity/access to the Asset Library. Additionally, the Asset library should be shared with the site guest user that the community setup under so that assets can be viewed in a non logged in context. 
## Install Instructions
#### General
* install python 3.7+ (later versions are likely fine but this is only tested with python 3)
* download this package or clone it using git.
* unzip the zip file
* open your terminal and go to the folder where the scripts are contained
* install dependencies by calling 
   ```$ pip install -r requirements.txt``` (see mac instructions, if using osx)
* this script is written in python 3 and is not compatible with python 2
   
#### Windows Install Instructions
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


#### Mac OSX Install instructions
Typically OSX already has python installed BUT python is mapped to python 2 you have to use python3 to execute a python 3 script.
1. where instructions say to use python, call python3 instead
2. where instructions say use pip, use pip3 instead.
* install dependencies by calling 
   ```$ pip3 install -r requirements.txt```
   

## Windows execution instructions
Running from IDLE in windows tends to be a bit more responsive than running from the command line. These instructions address how to effectively provide parameters to the different scripts in order to run from IDLE

## Opening script in IDLE
1. open the folder that contains the script, then right click or double click on the file in windows to open in IDLE.
2. paste the lines provided into the script
3. press F5 or Run > Execute Script to execute the script and watch the results scroll across the screen. 
4. you can save multiple configurations by commenting out the lines you dont want to use by putting a # in front of the line. 
```
#sys.argv = ['','-u', '<username1>', '-p', '<password>', '-t', '<token>', '-s','t']
sys.argv = ['','-u', '<username2>', '-p', '<password>', '-t', '<token>', '-s','t']
```

#General Script Information

## export.py
call this script with the following parameters to generate a package. 
the output will be an excel file and a folder called files. The folder contains the image content. *<> means user provided values.  


```$ python export.py -u <username> -p <password> -t <token> -s <is_sandbox? t/f>```

* **note that these command line calls will work in Windows but review how to run in IDLE**

#### Params
-u **username: Required** Salesforce environment username  
-p **password: Required** Salesforce environment password  
-t **Token: Required**   A salesforce token is a second passowrd that is required to access the Salesforce API. If you dont have it go to Settings > Reset Security Token and a new token will be emailed to you  
-s **Sandbox: Required** put 't' or 'true' if connection to a sandbox, put false if connecting to production  
-pages **Filter By Page(s): Not Required** a comma delimited list of page slugs. When used it will limit the export to only the content that is related to the pages in the list.  
-mega **Filter By Mega Menu(s): Not Required:** a comma delimited list of mega menu slugs. When used it will imit the export to only the content that is related to the menus in the list. (can be used in addition to -pages)    

## transfer.py
call this script with the following parameters to transfer a package to a new environment

```$ python transfer.py -i <input 'contentpak_<username>.<date>.zip'> -u <username> -p <password> -t <token> -s <is_sandbox? t/f>```
* **note that these command line calls will work in Windows but review how to run in IDLE**

#### Params
-i **input: Required** the path to the content pack you want to import  
-u **username: Required** Target Salesforce environment username   
-p **password: Required** Target Salesforce environment password  
-t **Token: Required**   A salesforce token is a second passowrd that is required to access the Salesforce API. If you dont have it go to Settings > Reset Security Token and a new token will be emailed to you  
-s **Sandbox: Required** put 't' or 'true' if connection to a sandbox, put false if connecting to production  

