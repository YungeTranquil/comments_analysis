import asyncio
import aiohttp

async def fetch_url_async(url, cookies=None):
    """
    Asynchronous fetch content from a URL using a GET request with custom User-Agent and cookies.
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": user_agent}
    if cookies is None:
        cookies = {}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, cookies=cookies) as response:
            return await response.text()  # Assuming you want the text content

async def main(urls):
    tasks = [fetch_url_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# Example usage
urls = ["https://example.com", "https://example.org", "https://example.com/data"]
asyncio.run(main(urls))