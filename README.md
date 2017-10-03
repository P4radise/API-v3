# API-v3
Version 3 API for OneVizion

This is a wrapper for simplifying API connection to a OneVizion system.


The Parameters.json file is not necessary, but we added in, since we use it for our scripts, and it keeps hardcoded logins and things our of a script.

All of our scripts use a Parameters.json file, which includes usernames and passwords along with URLs and other configuration.  This lets us test locally, then copy a script up unedited, to the production server or UAT server, and it will work correctly using parameters for that system.

That file looks like this:

{
"MyInfo": {
"email": "mgreene@onevizion.com",
"name": "Mike Greene"
},
"dev-mtrac.mobilitie.com": {
"url":"dev-mtrac.mobilitie.com",
"UserName": "mgreene",
"Password": “xxxxxxxxxx"
},
"mtrac.mobilitie.com": {
"url":"mtrac.mobilitie.com",
"UserName": "mgreene",
"Password": “xxxxxxxx"
},
"trackor.onevizion.com": {
"url":"trackor.onevizion.com",
"UserName": "mgreene",
"Password": “xxxxxxxxxxxx"
},
"Veracode": {
"UserName": "mgreene@onevizion.com",
"Password": “xxxxxxxxx"
},
"ReleaseSFTP": {
"Host": "ftp.onevizion.com",
"UserName": "releases",
"Password": “xxxxxxxx"
},
"Folders": {
"Archiva": "/opt/tomcat/data/repositories/releases",
"Git": "/Users/mike/GitHub/IKAM/ov"
},
"SMTP_ESRI": {
"UserName": "mgreene@onevizion.com",
"Password": “xxxxxxxxxxxxx",
"Server": "smtp.office365.com",
"Port": "587",
"Security": "STARTTLS",
"To": "mgreene@onevizion.com"
},
"SMTP": {
"UserName": "mgreene@onevizion.com",
"Password": “xxxxxxxxxxxx",
"Server": "smtp.office365.com",
"Port": "587",
"Security": "STARTTLS",
"To": "mgreene@onevizion.com"
},
"AWSCredentials": {
"AccessKey": “AOJBFJQEBFJQEFJEEJBFEJF",
"SecretAccessKey”:”jlknf3kj4nr34rjnwj4nrwj4werwe"
}
}

The idea is that you have a token, like “STMP” , or “trackor.onevizion.com”, and it has all the relavent  parameter info.


We tried to add some automatic Logging and Messaging for all API connections.  It is optional, but can cut down on lines of code if you want to use it.
To implement this, we created a Config stucture so you can pass parameters to ALL instances of the classes you create.  This is not elegant, but it cut down on necessary lines of code and made readability much better.

This Config structure is used for Messaging by setting the "Verbosity" item to a number. Vebosity = 0 gives only error messaging, Verbosity = 1 gives a little more information.  The higher the number, the more information, although, at teh time of this writing, 2 is the highest used.
for example:
onevizion.Config["Verbosity"] = 1

The Logging part is handled in onevizion.Config["Trace"].  Trace is an OrderedDict.  This can be used however you need to get a list of Messaging that hapened during the script's run.
