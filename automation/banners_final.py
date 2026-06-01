import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright

ADD_URL = "https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=indexSwiperInfo&m=first_duoduokes&op=indexSwiperInfo&version_id=0&pos=0"
PRODUCT_IMG = "images/250/2026/01/s7Zzhf8v8tko7qjXoK4GO"

BANNERS = [
    {"title":"Grassland Pet Festival S1","type":"3","url":"https://h2025.jihuifan.com/app/","sort":"10"},
    {"title":"Beef Liver Jerky 0 Add","type":"12","url":"","sort":"9"},
    {"title":"Sign Up Early Bird 1780","type":"3","url":"https://h2025.jihuifan.com/app/","sort":"8"},
    {"title":"City Partner Wanted","type":"3","url":"https://h2025.jihuifan.com/app/","sort":"7"},
]

async def add_banner(page, banner, num):
    print(f"  Adding {num}: {banner['title']}")
    await page.goto(ADD_URL, wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(1)
    try:
        await page.locator("input[name=title]").fill(banner["title"])
        await page.locator("input[name=pic]").fill(PRODUCT_IMG)
        await page.locator(f"input[name=type][value='{banner['type']}']").check()
        if banner["url"]:
            await page.locator("input[name=value]").fill(banner["url"])
        await page.locator("input[name=sort]").fill(banner["sort"])
        cb = page.locator("input[name=status]")
        if not await cb.is_checked():
            await cb.check()
        await page.locator("input[name=submit]").click()
        await asyncio.sleep(2)
        print(f"    Done! URL={page.url[:100]}")
        return True
    except Exception as e:
        print(f"    Fail: {e}")
        return False

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
    
    ok = 0
    for i, b in enumerate(BANNERS):
        if await add_banner(page, b, i+1):
            ok += 1
    
    print(f"\nDone! Added {ok}/{len(BANNERS)} banners")
    await browser.close()
    await pw.stop()

asyncio.run(main())