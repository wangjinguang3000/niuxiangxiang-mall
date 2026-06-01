import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright

ADD_URL = "https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=pageJumpInfo&m=first_duoduokes&op=pageJumpInfo&version_id=0&pos=2"

TOPLINKS = [
    {"title":"Sign Up","sort":"10"},
    {"title":"Shop","sort":"9"},
    {"title":"Join Us","sort":"8"},
    {"title":"Events","sort":"7"},
    {"title":"Videos","sort":"6"},
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
    
    ok = 0
    for i, tl in enumerate(TOPLINKS):
        print(f"Adding {i+1}: {tl['title']}")
        await page.goto(ADD_URL, wait_until="domcontentloaded", timeout=10000)
        await asyncio.sleep(1)
        try:
            await page.locator("input[name=title]").fill(tl["title"])
            await page.locator("input[name=sort]").fill(tl["sort"])
            cb = page.locator("input[name=status]")
            if not await cb.is_checked():
                await cb.check()
            await page.locator("input[name=submit]").click()
            await asyncio.sleep(2)
            print(f"  Done!")
            ok += 1
        except Exception as e:
            print(f"  Fail: {e}")
    
    print(f"\nAdded {ok}/{len(TOPLINKS)} toplinks")
    await browser.close()
    await pw.stop()

asyncio.run(main())