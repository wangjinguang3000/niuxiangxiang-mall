import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright

async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page(viewport={"width":1440,"height":900})
    
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=user&a=login&", wait_until="load", timeout=15000)
    await asyncio.sleep(1)
    await page.fill("input[name=username]", "w15024998286")
    await page.fill("input[name=password]", "w12345678")
    await page.click("input[type=submit]")
    await asyncio.sleep(3)
    
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=site&a=entry&eid=36&version_id=0", wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(2)
    
    body = await page.evaluate("() => document.body.innerText")
    print(body[:800])
    
    await browser.close()
    await pw.stop()

asyncio.run(main())