import aiohttp


async def search(search_string: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://api.stackexchange.com/search/advanced?order=desc&sort=activity&title={search_string}&site=stackoverflow') as resp:
            return await resp.json()
