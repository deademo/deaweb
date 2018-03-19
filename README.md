# deaweb
lightweight asynchronous easy-to-use web-framework for micropython

# How to use
It's really simple, just a fast example:
```
import deaweb
app = deaweb.Server()

@app.handler('/hi')
def hello_world_handler(request):
    return 'Hello World!'
```
For more details look at [API reference](#api-reference)

# Installation 
### Using upip
You can use upip to install deaweb. Example: 
```
import upip
upip.install('deaweb')
import deaweb
```
### Using frozen micropython code (.mpy file) or python source code (.py file)
Just download `deaweb.mpy` or `deaweb.py` file and put it near your app to use .py/.mpy file as python module.
After just import deaweb in your app:
```
import deaweb
```

Also you can complile deaweb.mpy file using deaweb.py using [MicroPython cross compiler](https://github.com/micropython/micropython/tree/master/mpy-cross)

# Known issues
### When you trying to install deaweb using upip on esp8266 you may got:
```
MemoryError: memory allocation failed, allocating 72 bytes
```
In this case just [use deaweb.mpy file](#using-frozen-micropython-code-mpy-file-or-python-source-code-py-file)

# API reference
### Request
##### **`Request.headers`** _(dict or None)_
Contains dict of a request headers. None if headers not read.
Example:
```
@app.handler('/')
def test(request):
    # print's Content-Type of request or None if not provided
    print(request.headers.get('Content-Type'))
```       
##### **`Request.method`** _(str or None)_
Contains string with a request method (like a GET/POST/PUT... etc). None if headers not read.

##### **`Request.path`** _(str or None)_
Contains string with a request path (like a /get, /hi or /). None if headers not read.

##### **`Request.protocol`** _(str or None)_
Contains string of a request protocol. None if headers not read.

##### **`Request.get(name)`** _(str, list or None)_
Returns value of params provided in query string. Needs to be headers read.
Returns None if parameter not found/provided.
Return list if several parameter with same name provided.
Example:
```
@app.handler('/get_data')
def data_handler(request):
    # if user sent request http://ip:port/get_data?key=userdata&a=1&a=2 will print
    print(request.get('param1')) # None
    print(request.get('key')) # userdata
    print(request.get('a')) # ['1', '2']
```

##### **`Request.content_length`** _(int)_
Return request Content-Length header value. If header not provided returns 0.

##### **`Request.readinto(file_path)`** _(None)_
Reads payload and storing it into file_path
Example:
```
@app.handler('/put_data')
def put_data_handler(request):
    await request.readinto('some_file.ext')
    return 'ok'
```

##### **`Request.readinto_safe(file_path)`** _(bool)_
Same with [Request.readinto](#requestreadintofile_path-none), but
If you got MemoryError then just False will returned. If not True.
And file first will be written into buffer file and if download successful
renamed to yours file name

##### **`Request.reader`** _(uasyncio.StreamReader)_
Returns request reader

```
@app.handler('/upload_file')
def upload_file_handler(request):
with open('file.tmp', 'w') as f:
    content = await request.reader.read()
    f.write(content)
```

##### **`Request.writer`** _(uasyncio.StreamWriter)_
Returns request writer
Example:
```
@app.handler('/')
def main_handler(request):
    response = Response('My response', request=request) # creating response object
    await response.awrite() # writing response
```

### Response
You can do not use this class to return a response

Just return string what you want from handler to make a response
##### **`Response(body=None, status_code=200, content_type='text/html')`**
 *`body`* _(str)_ - Response string. By default None.
 
 *`status_code`* _(int)_ - Response status code. By default 200.
 
 *`content_type`* _(str)_ - Response Content-Type. By default 'text/html'.

##### **`Response.awrite()`** _(None)_
Use this method to write `Response.body` to the client.
Example:

```
await response.awrite()
```
or
```
yield from response.awrite()
```

##### **`Response.aclose()`** _(None)_
Use this method to close response/communication with client.

##### **`Response.body`** _(str or None)_
Respose body. None if not set.

##### **`Response.status_code`** _(int)_
Respose status code. By default 200.

##### **`Response.content_type`** _(str or None)_
Respose Content-Type header value. 'text/html' if not set.

### FileResponse
Used to return file as response

TODO:
 - file name in header
 - file content type in depend on file extension
 - read N bytes instead readline
Example:
```
@app.handler('/get_some_file')
def get_some_file_handler(request):
    return FileResponse('some_file.ext')
```
