import asyncio

import deaweb

app = deaweb.Server()


@app.handler('/')
def handler_hello_world(request):
    return 'Hello, world!'


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.make_server('0.0.0.0', 8080))
    loop.close()
