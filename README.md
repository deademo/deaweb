# deaweb
lightweight asynchroumous easy-to-use web-framework for micropython

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

### Response
You can do not use this class to return response

Just return string what you want from handler to make response
##### **`Response(body=None, status_code=200, content_type='text/html')`**
 **`body`** _(str)_ - Response string. By default None.
 
 **`status_code`** _(int)_ - Response status code. By default 200.
 
 **`content_type`** _(str)_ - Response Content-Type. By default 'text/html'.

##### **`awrite()`** _(None)_
Use this method to write `Response.body` to client.
Example:

```
await response.awrite()
```
or
```
yield from response.awrite()
```

##### **`aclose()`** _(None)_
Use this method to close response/communication with client.

##### **`body`** _(str or None)_
Respose body. None if not set.

##### **`status_code`** _(int)_
Respose status code. By default 200.

##### **`content_type`** _(str or None)_
Respose Content-Type header value. 'text/html' if not set.
