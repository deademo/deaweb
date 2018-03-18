import gc
import uos

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


def handler_404(*_, **__):
    return Response(body='Not found', status_code=404)


class Server:
    handler_404 = handler_404

    def __init__(self, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._handlers = {}

    def handler(self, path):
        def make_handler(handler):
            self._handlers[path] = handler
            return handler
        return make_handler

    async def server_handler(self, reader, writer):
        request = Request(reader, writer)
        await request.read_headers()
        handler = self._handlers.get(request.path, self.handler_404)

        is_coroutine = (
            hasattr(asyncio, 'iscoroutinefunction') and
            asyncio.iscoroutinefunction(handler)
        )
        if is_coroutine or handler.__class__.__name__ == 'generator':
            response = await handler(request)
        else:
            response = handler(request)

        if response is None:
            return None

        if not isinstance(response, Response):
            response = Response(response)
        response.request = request
        await response.awrite()
        await response.aclose()

    def add_handler(self, path, handler):
        self._handlers[path] = handler

    def make_server(self, ip="0.0.0.0", port=8080):
        return asyncio.start_server(self.server_handler, ip, port)

    def start_server(self, *args, **kwargs):
        asyncio.ensure_future(
            self.make_server(*args, **kwargs),
            loop=self.loop
        )


class Request:
    def __init__(self, reader, writer, *, loop=None):
        self.loop = loop
        self.reader = reader
        self.writer = writer
        self.headers = None
        self.method = None
        self.path = None
        self.protocol = None
        self.params = {}

    @property
    def content_length(self):
        return int(self.headers.get('Content-Length', 0))

    async def read_headers(self):
        self.headers = {}

        # First request line
        line = await self.reader.readline()
        self.method, path, self.protocol = line.split()

        # Splitting path and query string
        path = path.split(b'?', 1)
        self.path = '/'+path[0].strip(b'/').decode()
        if len(path) > 1:
            query_string = path[1]
            self.params = parse_qs(query_string.decode())

        # Do ... while headers provided
        line = await self.reader.readline()
        while line != b"\r\n":
            k, v = line.split(b":", 1)
            self.headers[k.decode().strip()] = v.decode().strip()
            line = await self.reader.readline()

        return self.headers

    def get(self, name):
        data = self.params.get(name)
        if data and len(data) == 1:
            return data[0]
        return data

    async def _write(self, data):
        if hasattr(self.writer, 'awrite'):
            await self.writer.awrite(data.encode())
        else:
            self.writer.write(data.encode())

    async def readinto(self, file_path):
        """
        TODO: find better way to save file with small memory usange
        """

        total_read = 0
        size = self.content_length
        block_size = 128

        file_size_reopen = 1024
        reopen_every_n_block = int(file_size_reopen/128)
        if reopen_every_n_block <= 0:
            reopen_every_n_block = 1

        f = open(file_path, 'wb')
        while total_read < size:
            if total_read+block_size >= size:
                block_size = size-total_read

            read_buffer = await self.reader.read(block_size)
            f.write(read_buffer)

            block_read = int(total_read/block_size)
            if block_read % reopen_every_n_block == 0:
                f.close()
                f = open(file_path, 'ab')
                gc.collect()

            total_read += len(read_buffer)
            if total_read % 1024 == 0:
                print('\r{:>6.2f}% {:0.2f}/{:0.2f} KB - {} ... '.format(total_read/size*100, total_read/1024, size/1024, file_path))
        f.close()

    async def readinto_safe(self, file_path):
        try:
            await self.readinto(str(file_path)+'_tmp')
            uos.rename(file_path+'_tmp', file_path)
            return True
        except:
            return False


class Response:
    __response_template = (
        "HTTP/1.1 {status_code} NA\r\n"
        "Server: micropython\r\n"
        "Content-Type: {content_type}\r\n"
        "Content-Length: {content_length}\r\n"
        "Connection: closed\r\n")

    def __init__(self, body=None, status_code=200, content_type='text/html',
                 headers={}, *, request=None):
        self.body = body
        self.status_code = status_code
        self.request = request
        self.content_type = content_type
        self.headers = headers

    async def awrite_headers(self):
        headers_values = {
            'content_length': self.content_length,
            'status_code': self.status_code,
            'content_type': self.content_type,
        }
        for key, value in self.headers.items():
            key = key.lower().replace('-', '_')
            if key in headers_values:
                headers_values[key] = value

        response = self.__response_template.format(**headers_values)
        for header, value in self.headers.items():
            response += '{}: {}\r\n'.format(header, value)
        response += "\r\n"

        await self.request._write(response)

    async def awrite(self, body=None):
        if not body:
            await self.request._write(body)
        elif not self.body:
            await self.request._write(self.body)

    async def aclose(self):
        await self.request._write("\r\n")
        if hasattr(self.request.writer, 'aclose'):
            await self.request.writer.aclose()

    @property
    def content_length(self):
        return len(self.body) if self.body else '0'


class FileResponse(Response):
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        self._content_length = None
        super().__init__(file_path, *args, **kwargs)

    async def awrite(self):
        await self.awrite_headers()
        with open(self.file_path) as f:
            for line in f.readline():
                await self.request._write(line)

    @property
    def content_length(self):
        if not self._content_length:
            self._content_length = uos.stat(self.file_path)[6]
        return self._content_length

def unquote_plus(s):
    s = s.replace("+", " ")
    arr = s.split("%")
    arr2 = [chr(int(x[:2], 16)) + x[2:] for x in arr[1:]]
    return arr[0] + "".join(arr2)


def parse_qs(s):
    res = {}
    if s:
        pairs = s.split("&")
        for p in pairs:
            vals = [unquote_plus(x) for x in p.split("=", 1)]
            if len(vals) == 1:
                vals.append(True)
            if vals[0] in res:
                res[vals[0]].append(vals[1])
            else:
                res[vals[0]] = [vals[1]]
    return res


def main():
    app = Server()

    @app.handler('/')
    async def hello(request):
        await Response('ok', request=request).awrite()
        return None

    app.start_server()

    app.loop.run_forever()
    app.loop.close()


if __name__ == '__main__':
    main()
