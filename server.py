from aiohttp import web, WSCloseCode, WSMsgType
import asyncio
import logging
import math
import weakref
import os

logger = logging.getLogger(__name__)


async def factorial_producer():
    """ Produces factorial of next number and sleeps """
    number = 1
    factorial = number
    while True:
        factorial *= number
        yield number, factorial
        number += 1
        await asyncio.sleep(0.1)


async def broadcast_factorial(app):
    """ Broadcasts factorials infinitly to all connected websockets """
    try:
        async for number, factorial in factorial_producer():
            for ws in app['websockets']:
                await ws.send_str('!{} = {}'.format(number, factorial))
            logger.info("!%s = %s", number, factorial)
            number += 1
    except asyncio.CancelledError:
        pass


async def start_background_tasks(app):
    app['broadcast_factorial'] = app.loop.create_task(broadcast_factorial(app))


async def cleanup_background_tasks(app):
    app['broadcast_factorial'].cancel()
    await app['broadcast_factorial']


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    request.app['websockets'].add(ws)
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    request.app['websockets'].remove(ws)
                    await ws.close()
                else:
                    await ws.send_str('%s pong' % msg.data)
            elif msg.type == WSMsgType.ERROR:
                logging.exception('ws connection closed with exception %s' %
                                  ws.exception())

    finally:
        request.app['websockets'].discard(ws)

    return ws


async def on_shutdown(app):
    for ws in set(app['websockets']):
        await ws.close(code=WSCloseCode.GOING_AWAY,
                       message='Server shutdown')


def get_app():
    app = web.Application()
    app['websockets'] = weakref.WeakSet()
    app.on_shutdown.append(on_shutdown)
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.add_routes([web.get('/ws', websocket_handler)])
    return app


if __name__ == '__main__':
    HOST = os.getenv('HOST', "localhost")
    PORT = os.getenv('PORT', 8080)
    app = get_app()
    web.run_app(app, host=HOST, port=PORT)
