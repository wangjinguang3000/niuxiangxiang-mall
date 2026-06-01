import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright

LOGIN = "https://h2025.jihuifan.com/web/index.php?c=user&a=login&"
BASE = "https://h2025.jihuifan.com"
EDIT = BASE + "/web/index.php?c=site&a=entry&do=selfGoodsInfo&m=first_duoduokes&op=selfGoodsInfo&version_id=0&id="

PRODUCTS = [
    {"id":"1780","title":"NiuXiangXiang Beef Liver 80g","price":"1600","mprice":"1990","stock":"999","comm":"10","sort":"10",
     "desc":"Ingredients: fresh beef liver only. Low-temp baked, zero additives. 80g/pack. SC10415255102074"},
    {"id":"1778","title":"NiuXiangXiang Beef Liver 240g Box(3 packs)","price":"4800","mprice":"5800","stock":"999","comm":"10","sort":"9",
     "desc":"Ingredients: fresh beef liver only. Low-temp baked, zero additives. 240g/box(80gx3). SC10415255102074"},
    {"id":"1776","title":"NiuXiangXiang Beef Liver 480g Gift Box","price":"8800","mprice":"10800","stock":"500","comm":"12","sort":"8",
     "desc":"Ingredients: fresh beef liver only. Low-temp baked, zero additives. 480g gift box(80gx6). Free bandana. SC10415255102074"},
]

async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page(viewport={"width":1440,"height":900})
    
    print("Login...")
    await page.goto(LOGIN, wait_until="load", timeout=15000)
    await asyncio.sleep(1)
    await page.fill("input[name=username]", "w15024998286")
    await page.fill("input[name=password]", "w12345678")
    await page.click("input[type=submit]")
    await asyncio.sleep(3)
    print("OK")
    
    plist = BASE + "/web/index.php?c=site&a=entry&do=selfMall&m=first_duoduokes&op=selfMall&version_id=0&tab_id=0"
    await page.goto(plist, wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    ids_js = """() => {
        var links = document.querySelectorAll("a");
        var ids = [];
        for (var i=0; i<links.length; i++) {
            var h = links[i].href;
            if (h && h.indexOf("selfGoodsInfo")>=0 && h.indexOf("id=")>=0) {
                var m = h.match(/id=([0-9]+)/);
                if (m) ids.push(m[1]);
            }
        }
        var u = [];
        for (var j=0; j<ids.length; j++) { if (u.indexOf(ids[j])<0) u.push(ids[j]); }
        return u;
    }"""
    ids = await page.evaluate(ids_js)
    print(f"Found products: {ids}")
    
    our = set(p["id"] for p in PRODUCTS)
    for p in PRODUCTS:
        if p["id"] not in ids:
            print(f"  Skip {p['id']}")
            continue
        print(f"  Update {p['id']}")
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
            print("    Done!")
        except Exception as e:
            print(f"    Failed: {e}")
    
    other = [i for i in ids if i not in our]
    print(f"Hide {len(other)}: {other}")
    for pid in other:
        try:
            await page.goto(EDIT + pid, wait_until="load", timeout=15000)
            await asyncio.sleep(1)
            cb = page.locator("input[name=status]")
            if await cb.is_checked():
                await cb.uncheck()
                await page.locator("input[name=submit]").click()
                await asyncio.sleep(1)
                print(f"    Hidden {pid}")
            else:
                print(f"    {pid} already off")
        except Exception as e:
            print(f"    Fail {pid}: {e}")
    
    print("DONE!")
    await browser.close()
    await pw.stop()

asyncio.run(main())