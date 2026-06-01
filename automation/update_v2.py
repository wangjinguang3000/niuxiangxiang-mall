import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright

BASE = "https://h2025.jihuifan.com"
EDIT = BASE + "/web/index.php?c=site&a=entry&do=selfGoodsInfo&m=first_duoduokes&op=selfGoodsInfo&version_id=0&id="

NEED_UPDATE = [
    {"id":"1780","title":"NiuXiangXiang Beef Liver Jerky 80g Pack","price":"1600","mprice":"1990","stock":"999","comm":"10","sort":"10",
     "desc":"Ingredients: fresh beef liver only. Low-temp baked, zero additives, zero preservatives.\n\nSpec: 80g/pack\nUnit price: 0.20/g\nBest for: small dogs daily treat\nProtein: 29g/100g\nSC10415255102074"},
    {"id":"1779","title":"NiuXiangXiang Beef Liver Jerky 240g Box(3 packs)","price":"4800","mprice":"5800","stock":"999","comm":"10","sort":"9",
     "desc":"Ingredients: fresh beef liver only. Low-temp baked, zero additives.\n\nSpec: 240g/box (80g x 3 packs)\nUnit price: 0.20/g\nBest for: medium dog family stock-up\nProtein: 29g/100g\nSC10415255102074"},
    {"id":"1777","title":"NiuXiangXiang Beef Liver Jerky 480g Gift Box","price":"8800","mprice":"10800","stock":"500","comm":"12","sort":"8",
     "desc":"Ingredients: fresh beef liver only. Low-temp baked, zero additives.\n\nSpec: 480g gift (80g x 6 packs)\nUnit price: 0.18/g (best value!)\nBonus: free brand bandana\nProtein: 29g/100g\nSC10415255102074"},
]

HIDE_IDS = ["1770","1771","1772","1773","1774","1775","1776"]

async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page(viewport={"width":1440,"height":900})
    
    print("Login...")
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=user&a=login&", wait_until="load", timeout=15000)
    await asyncio.sleep(1)
    await page.fill("input[name=username]", "w15024998286")
    await page.fill("input[name=password]", "w12345678")
    await page.click("input[type=submit]")
    await asyncio.sleep(3)
    print("OK")
    
    # Phase 1: Update 3 beef liver products
    print("\n=== Phase 1: Update Products ===")
    for p in NEED_UPDATE:
        print(f"  Updating ID={p['id']}: {p['title']}")
        await page.goto(EDIT + p["id"], wait_until="load", timeout=15000)
        await asyncio.sleep(1)
        try:
            await page.locator("input[name=title]").fill(p["title"])
            await page.locator("input[name=price]").fill(p["price"])
            await page.locator("input[name=market_price]").fill(p["mprice"])
            await page.locator("input[name=stock]").fill(p["stock"])
            await page.locator("input[name=commission_rate]").fill(p["comm"])
            await page.locator("input[name=sort]").fill(p["sort"])
            await page.locator("textarea[name=content]").fill(p["desc"])
            await page.locator("input[name=submit]").click()
            await asyncio.sleep(2)
            print(f"    Done!")
        except Exception as e:
            print(f"    Failed: {e}")
    
    # Phase 2: Hide 7 unrelated products
    print(f"\n=== Phase 2: Hide {len(HIDE_IDS)} Products ===")
    for pid in HIDE_IDS:
        try:
            await page.goto(EDIT + pid, wait_until="load", timeout=15000)
            await asyncio.sleep(1)
            cb = page.locator("input[name=status]")
            if await cb.is_checked():
                await cb.uncheck()
                await page.locator("input[name=submit]").click()
                await asyncio.sleep(1)
                print(f"    Hidden ID={pid}")
            else:
                print(f"    ID={pid} already off")
        except Exception as e:
            print(f"    Fail ID={pid}: {e}")
    
    print("\n=== ALL DONE! ===")
    await browser.close()
    await pw.stop()

asyncio.run(main())