# AIO mem-cached JSON storage REST-like webserver

## What is this?
It's a Web server for storing data in key+value pairs

This is not a database, if you're looking for a database, look somewhere else, not here

## Features
- Create, update, read and/or delete data
- Password protected data and privacy modes
- Minimal web interface to interact with the API
- Manipulate the data using jobs inside the webserver

## Web interface

- Provides a minimal access to the API
- The web interface is only available when the privacy mode is active

## Jobs

- By using jobs, you can customize the behaviour of the data stored as time passes
- You can see an example of a job [here](myjobs.py) that runs as an asyncio task. Use that file as a template to make custom jobs

NOTICE: By extending the functionality with your own jobs, you will have to modify the requirements.txt file

## Environment Variables

- PASSWORD (text) Password for modifying data. Default is "12345678"
- PRIVATE (bool) Private mode. Default is "True"
- PORT (number) Port number for the web server. Default is 80

## API reference

### Read data (Private mode enabled)
Read a single key
```
POST /
JSON {"password":"YourPasswordHere","key":"NameOfTheKey"}
Sample Response {"NameOfTheKey":"ValueOfTheKey"}
```

Get multiple values from multiple keys

```
POST /
JSON {"password":"password":"keys":["key1","key2","keyN"]}
Sample Response {"key1":"value1","key2":"value2","keyN":"valueN"}
```

### Read data (Private mode disabled)
Retrieves all keys
```
GET /
Sample Response {"key1":"value1","key2":"value2","keyN":"valueN"}
```
Retrieve a specific key using the URL parameter "keyname"
```
GET /
URLParam keyname=some_key
Sample Response {"some_key":"value"}
```

### Write data
All responses are an empty JSON {}
Values can be strings, ints, etc... nested JSONs, arrays, arrays with JSONs...

Create or update a key+value pair
```
POST /
JSON {"password":"YourPasswordHere","key":"NameOfTheKey","value":"the_value"}
```

Create or update multiple key+value pairs:
```
POST /
JSON {"password":"YourPasswordHere","kvpairs":{"key1":"val1","key2":"val2","key3":"val3","keyN":"valN"}}
```

### Delete data
All responses are an empty JSON {}

Delete a single key along with it's value
```
DELETE /
JSON {"password":"YourPasswordHere","key":"NameOfTheKey"}
```

Delete multiple keys along with their corresponding values
```
DELETE /
JSON {"password":"YourPasswordHere","keys":["key1","key2","key3","keyN"]}
```
