#doesn't work on Google collab
import asyncio
import aiohttp
import time

websites = []
with open('feed.txt', 'r') as malicious_dns_file:
    for site in malicious_dns_file:
        websites.append(site)

async def get(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                resp = await response.read()
                print("Successfully got url {} with response of length {}.".format(url, len(resp)))
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def main(urls, amount):
    ret = await asyncio.gather(*[get(url) for url in urls])
    print("Finalized all. ret is a list of len {} outputs.".format(len(ret)))


start = time.time()
asyncio.run(main(websites, len(websites)))
end = time.time()

print("Took {} seconds to pull {} websites.".format(end - start, len(websites)))
