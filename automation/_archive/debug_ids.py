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
    
    plist = "https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=selfMall&m=first_duoduokes&op=selfMall&version_id=0&tab_id=0"
    await page.goto(plist, wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    # Get ALL links with their href
    links = await page.evaluate("""() => {
        var all = document.querySelectorAll("a");
        var result = [];
        for (var i=0; i<all.length; i++) {
            var a = all[i];
            if (a.href && a.innerText && a.innerText.trim() === "编辑") {
                result.push({text: a.innerText.trim(), href: a.href.substring(0,200)});
            }
        }
        return result;
    }""")
    
    print(f"Edit links: {len(links)}")
    for l in links:
        print(f"  {l['href']}")
    
    await browser.close()
    await pw.stop()

asyncio.run(main())