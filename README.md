# deaweb
lightweight asynchroumous easy-to-use web-framework for micropython

# Instalation 
### Using upip
You can use upip to install deaweb. Example: 
```
import upip
upip.install('deaweb')
import deaweb
```
### Using frozen micropython code (.mpy file) or python source code (.py file)
Just download `deaweb.mpy` or `deaweb.py` file and put it near your app to use .mpy file as python module.
After just import deaweb in your app:
```
import deaweb
```
# How to use
It's really simple, just fast example:
```
import deaweb
app = deaweb.Server()

@app.handler('/hi')
def hello_world_handler(request):
    return 'Hello World!'
```
For more details look at API reference or examples

# API reference
### Request
##### **`Request.headers`** _(dict or None)_
Contains dict of request headers. None if headers not read.
Example:
```
@app.handler('/')
def test(request):
    # print's Content-Type of request or None if not provided
    print(request.headers.get('Content-Type'))
```       
##### **`Request.method`** _(str or None)_
Contains string with request method (like a GET/POST/PUT... etc). None if headers not read.

##### **`Request.path`** _(str or None)_
Contains string with request path (like a /get, /hi or /). None if headers not read.

##### **`Request.protocol`** _(str or None)_
Contains string of request protocol. None if headers not read.

##### **`Request.params`** _(dict)_
Contains query string params as dict. Empty if headers not read.
Example:
```
@app.handler('/get_data')
def data_handler(request):
    # if user sent request http://ip:port/get_data?key=userdata will print
    print(request.params.get('param1')) # None
    print(request.params.get('key')) # userdata
```
##### **`Request.reader`** _(uasyncio.StreamReader)_
If request body provided you can use reader method `read` to read data of request
Example:
```
@app.handler('/upload_file')
def upload_file_handler(request):
with open('file.tmp', 'w') as f:
    content = await request.reader.read()
    f.write(content)
```
##### **`Request.writer`** _(uasyncio.StreamWriter)_
If you need to send response before handler finished you can use writer method `write` and `aclose` to write and close response
Example:
```
@app.handler('/')
def main_handler(request):
    response = Response('My response', request=request) # creating response object
    await response.awrite() # writing response
```
