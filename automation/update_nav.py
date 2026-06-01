import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright

NAV_URL = "https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=bottomNav&m=first_duoduokes&op=bottomNav&version_id=0"

NAV_UPDATES = [
    {"idx": 0, "title": "Home", "status": True},
    {"idx": 1, "title": "My", "status": True},
]

NEW_NAV = [
    {"title": "Events", "sort": "2"},
    {"title": "Products", "sort": "3"},
    {"title": "Join", "sort": "4"},
]

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
    
    # Update existing nav items
    print("=== Update existing nav ===")
    await page.goto(NAV_URL, wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(2)
    
    for update in NAV_UPDATES:
        await page.goto(NAV_URL, wait_until="domcontentloaded", timeout=10000)
        await asyncio.sleep(1)
        
        edit_links = page.locator("text=编辑")
        count = await edit_links.count()
        print(f"  Edit #{update['idx']+1}: title={update['title']}")
        
        await edit_links.nth(update["idx"]).click()
        await asyncio.sleep(2)
        
        try:
            await page.locator("input[name=title]").fill(update["title"])
            cb = page.locator("input[name=status]")
            if update["status"] and not await cb.is_checked():
                await cb.check()
            elif not update["status"] and await cb.is_checked():
                await cb.uncheck()
            await page.locator("input[name=submit]").click()
            await asyncio.sleep(2)
            print(f"    Done!")
        except Exception as e:
            print(f"    Fail: {e}")
    
    # Add new nav items
    print("\n=== Add new nav items ===")
    await page.goto(NAV_URL, wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(2)
    
    add_url = await page.evaluate("""() => {
        var links = document.querySelectorAll("a");
        for (var i=0; i<links.length; i++) {
            if (links[i].innerText && links[i].innerText.trim() === "增加") {
                return links[i].href;
            }
        }
        return null;
    }""")
    print(f"  Add URL: {add_url}")
    
    if add_url:
        for i, nav in enumerate(NEW_NAV):
            print(f"  Adding {i+1}: {nav['title']}")
            await page.goto(add_url, wait_until="domcontentloaded", timeout=10000)
            await asyncio.sleep(1)
            try:
                await page.locator("input[name=title]").fill(nav["title"])
                cb = page.locator("input[name=status]")
                if not await cb.is_checked():
                    await cb.check()
                await page.locator("input[name=submit]").click()
                await asyncio.sleep(2)
                print(f"    Done!")
            except Exception as e:
                print(f"    Fail: {e}")
    
    print("\n=== Navigation Done! ===")
    await browser.close()
    await pw.stop()

asyncio.run(main())