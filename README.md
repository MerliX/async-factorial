# async-factorial

## Description
Supports you with fresh factorial via websocket at `ws://localhost:8080/ws`
Can play ping-pong on any text sent via websocket

## Docker build and run
```bash
docker build . --tag=async_factorial
docker run -e="HOST=0.0.0.0" -e="PORT=8080" -p="8080:8080" async_factorial
```

## Test
```bash
pytest test.py
```
