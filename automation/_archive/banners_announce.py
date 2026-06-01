import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright

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
    
    # Go to ad/banner page
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=site&a=entry&eid=36&version_id=0", wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    # Find "add" button for banner
    add_href = await page.evaluate("""() => {
        var links = document.querySelectorAll("a");
        for (var i=0; i<links.length; i++) {
            if (links[i].innerText && links[i].innerText.trim() === "增加") {
                return links[i].href;
            }
        }
        return null;
    }""")
    print(f"Add banner URL: {add_href}")
    
    if add_href:
        await page.goto(add_href, wait_until="load", timeout=15000)
        await asyncio.sleep(2)
        
        # Get form fields
        fields = await page.evaluate("""() => {
            var els = document.querySelectorAll("input, textarea, select");
            return Array.from(els).map(function(el) {
                return {
                    tag: el.tagName,
                    type: el.type,
                    name: el.name,
                    placeholder: (el.placeholder||"").substring(0,40),
                    id: el.id
                };
            });
        }""")
        print(f"\nForm fields ({len(fields)}):")
        for f in fields:
            if f["name"] or f["placeholder"]:
                print(f"  {f['tag']} name={f['name']} type={f['type']} placeholder={f['placeholder']} id={f['id']}")
        
        # Get page text
        body = await page.evaluate("() => document.body.innerText")
        print(f"\nPage text (first 500):\n{body[:500]}")
    
    await browser.close()
    await pw.stop()

asyncio.run(main())