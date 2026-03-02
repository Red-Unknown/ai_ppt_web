
import asyncio
import time
import socket
import logging
import ssl
import aiohttp
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TARGET_HOSTS = [
    "api.tavily.com",
    "api.deepseek.com",
    "duckduckgo.com"
]

async def check_dns(host: str):
    start = time.time()
    try:
        addr_info = await asyncio.get_event_loop().getaddrinfo(host, 443)
        duration = (time.time() - start) * 1000
        logger.info(f"DNS Resolution ({host}): {duration:.2f}ms - OK")
        return True
    except Exception as e:
        logger.error(f"DNS Resolution ({host}): FAILED - {e}")
        return False

async def check_tcp_connect(host: str, port: int = 443):
    start = time.time()
    try:
        reader, writer = await asyncio.open_connection(host, port)
        duration = (time.time() - start) * 1000
        writer.close()
        await writer.wait_closed()
        logger.info(f"TCP Connection ({host}:{port}): {duration:.2f}ms - OK")
        return True
    except Exception as e:
        logger.error(f"TCP Connection ({host}:{port}): FAILED - {e}")
        return False

async def check_ssl_handshake(host: str, port: int = 443):
    start = time.time()
    try:
        # Create SSL context
        ssl_context = ssl.create_default_context()
        reader, writer = await asyncio.open_connection(host, port, ssl=ssl_context)
        duration = (time.time() - start) * 1000
        writer.close()
        await writer.wait_closed()
        logger.info(f"SSL Handshake ({host}:{port}): {duration:.2f}ms - OK")
        return True
    except Exception as e:
        logger.error(f"SSL Handshake ({host}:{port}): FAILED - {e}")
        return False

async def check_aiohttp_pool(concurrency: int = 50):
    """
    Check if aiohttp pool can handle concurrency without blocking.
    """
    start = time.time()
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for _ in range(concurrency):
            # Just hit google or something stable
            tasks.append(session.get("https://www.google.com", timeout=5))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = (time.time() - start) * 1000
            
            success = sum(1 for r in results if not isinstance(r, Exception) and r.status == 200)
            failed = concurrency - success
            
            logger.info(f"Aiohttp Pool Test (Concurrency {concurrency}): {duration:.2f}ms")
            logger.info(f"  Success: {success}/{concurrency}")
            logger.info(f"  Failed: {failed}/{concurrency}")
            
            if failed > 0:
                logger.warning(f"  Failures: {failed} requests failed or timed out.")
        except Exception as e:
            logger.error(f"Aiohttp Pool Test FAILED: {e}")

async def main():
    logger.info("Starting Network Diagnostics...")
    
    # Check DNS
    for host in TARGET_HOSTS:
        await check_dns(host)
        
    # Check TCP
    for host in TARGET_HOSTS:
        await check_tcp_connect(host)

    # Check SSL
    for host in TARGET_HOSTS:
        await check_ssl_handshake(host)
        
    # Check Aiohttp Pool
    logger.info("Checking Connection Pool limits...")
    await check_aiohttp_pool(concurrency=20)
    
    logger.info("Diagnostics Complete.")

if __name__ == "__main__":
    asyncio.run(main())
