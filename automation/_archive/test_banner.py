import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
import time

ADD_URL = "https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=indexSwiperInfo&m=first_duoduokes&op=indexSwiperInfo&version_id=0&pos=0"

async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page(viewport={"width":1440,"height":900})
    
    # Login
    print("Login...")
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=user&a=login&", wait_until="load", timeout=15000)
    await asyncio.sleep(1)
    await page.fill("input[name=username]", "w15024998286")
    await page.fill("input[name=password]", "w12345678")
    await page.click("input[type=submit]")
    await asyncio.sleep(3)
    print("OK")
    
    # Test accessing the add form with domcontentloaded
    print("Navigate to add form...")
    try:
        await page.goto(ADD_URL, wait_until="domcontentloaded", timeout=10000)
        print(f"  URL: {page.url[:120]}")
        print(f"  Title: {await page.title()}")
        
        # Check if form is loaded
        has_title = await page.locator("input[name=title]").count()
        print(f"  Title input: {has_title}")
        
        if has_title > 0:
            print("  Form loaded! Filling...")
            await page.locator("input[name=title]").fill("Test Banner Title")
            await page.locator("input[name=sort]").fill("1")
            print("  Form filled!")
        else:
            body = await page.evaluate("() => document.body.innerText")
            print(f"  Body: {body[:300]}")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    await browser.close()
    await pw.stop()

asyncio.run(main())