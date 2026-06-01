import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright

BASE = "https://h2025.jihuifan.com"
ADD_URL = BASE + "/web/index.php?c=site&a=entry&do=indexSwiperInfo&m=first_duoduokes&op=indexSwiperInfo&version_id=0&pos=0"

BANNERS = [
    {"title":"Grassland Pet Interaction Season - Season 1","type_val":"3","value":"","sort":"10",
     "desc":"Register now! Early bird 1780. 4 competition events, 60-100 dog groups, 3 days 2 nights in Mongolian yurt."},
    {"title":"NiuXiangXiang Beef Liver Jerky - Zero Additives","type_val":"12","value":"","sort":"9",
     "desc":"Ingredients: fresh beef liver only. Human-grade pet treats. 80g/240g/480g available."},
    {"title":"Sign Up Now! Early Bird 1780","type_val":"3","value":"","sort":"8",
     "desc":"Limited 20 early bird slots. Mongolian grassland. Camping with your dog!"},
    {"title":"Join Us - Become City Partner","type_val":"3","value":"","sort":"7",
     "desc":"Looking for pet-loving partners. Zero inventory dropshipping available. Contact: 13145294218"},
]

async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page(viewport={"width":1440,"height":900})
    
    # Login
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=user&a=login&", wait_until="load", timeout=15000)
    await asyncio.sleep(1)
    await page.fill("input[name=username]", "w15024998286")
    await page.fill("input[name=password]", "w12345678")
    await page.click("input[type=submit]")
    await asyncio.sleep(3)
    print("Login OK")
    
    # Check the value options for radio buttons
    await page.goto(ADD_URL, wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    radio_vals = await page.evaluate("""() => {
        var radios = document.querySelectorAll("input[type=radio]");
        var result = [];
        for (var i=0; i<radios.length; i++) {
            var r = radios[i];
            var label = r.parentElement ? r.parentElement.innerText : "";
            result.push({value: r.value, label: label.trim().substring(0,40)});
        }
        return result;
    }""")
    
    print("Radio button values:")
    seen = set()
    for r in radio_vals:
        if r["value"] not in seen:
            seen.add(r["value"])
            print(f"  value={r['value']} -> {r['label']}")
    
    # Now add banners one by one
    for i, b in enumerate(BANNERS):
        print(f"\nAdding banner {i+1}: {b['title']}")
        await page.goto(ADD_URL, wait_until="load", timeout=15000)
        await asyncio.sleep(1)
        
        try:
            # Fill title
            await page.locator("input[name=title]").fill(b["title"])
            
            # Select radio button for type
            await page.locator(f"input[name=type][value='{b['type_val']}']").check()
            
            # Fill value/URL
            if b["value"]:
                await page.locator("input[name=value]").fill(b["value"])
            
            # Fill description
            await page.locator("textarea[name=info]").fill(b["desc"])
            
            # Set sort order
            await page.locator("input[name=sort]").fill(b["sort"])
            
            # Enable
            status_cb = page.locator("input[name=status]")
            if not await status_cb.is_checked():
                await status_cb.check()
            
            # Submit
            await page.locator("input[name=submit]").click()
            await asyncio.sleep(2)
            
            new_url = page.url
            print(f"  Submitted! URL: {new_url[:120]}")
            
        except Exception as e:
            print(f"  Failed: {e}")
    
    print("\n=== Banners Done! ===")
    await browser.close()
    await pw.stop()

asyncio.run(main())