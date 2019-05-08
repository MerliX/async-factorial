from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from server import get_app
import math
import re


class FactorialSergerTestCase(AioHTTPTestCase):

    async def get_application(self):
        return get_app()

    @unittest_run_loop
    async def test_factorial_logic(self):
        ws = await self.client.ws_connect('/ws')

        # Let's receive factorial
        text = await ws.receive_str()
        
        # Checking format
        match_obj = re.match(r'\!(\d+) = (\d+)', text)
        assert match_obj

        # Checking result is correct
        n, f = map(int, match_obj.groups(0))
        assert f == math.factorial(n)

        # Let's receive next factorial
        text = await ws.receive_str()
        match_obj = re.match(r'\!(\d+) = (\d+)', text)

        # Checking that factorial of next number is correct
        assert match_obj
        n2, f2 = map(int, match_obj.groups(0))
        assert n + 1 == n2
        assert f2 == math.factorial(n2)


    @unittest_run_loop
    async def test_ping_pong(self):
        ws = await self.client.ws_connect('/ws')

        # Ping - pong
        await ws.send_str('ping')
        text = await ws.receive_str()
        assert text == 'ping pong'

    @unittest_run_loop
    async def test_open_close(self):

        # No websockets at start
        assert len(self.app['websockets']) == 0

        # Now connecting
        ws = await self.client.ws_connect('/ws')

        # Websocket stored
        assert len(self.app['websockets']) == 1

        # Now disconnecting
        await ws.send_str('close')
        await ws.receive()

        # Websocket is closed
        assert ws.closed

        # App does not store it anymore
        assert len(self.app['websockets']) == 0
