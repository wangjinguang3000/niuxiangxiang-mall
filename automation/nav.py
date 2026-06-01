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
    
    # Go to bottom nav
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=bottomNav&m=first_duoduokes&op=bottomNav&version_id=0", wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(2)
    
    body = await page.evaluate("() => document.body.innerText")
    print(body[:800])
    
    # Find edit links
    edit_links = page.locator("text=编辑")
    count = await edit_links.count()
    print(f"\nEdit links: {count}")
    
    # Click first edit to see form
    if count > 0:
        await edit_links.first.click()
        await asyncio.sleep(2)
        
        fields = await page.evaluate("""() => {
            var els = document.querySelectorAll("input, textarea, select");
            return Array.from(els).map(function(el) {
                return {tag:el.tagName, type:el.type, name:el.name, placeholder:(el.placeholder||"").substring(0,30)};
            });
        }""")
        print(f"\nForm fields:")
        for f in fields:
            if f["name"]:
                print(f"  {f['tag']} name={f['name']} type={f['type']} placeholder={f['placeholder']}")
    
    await browser.close()
    await pw.stop()

asyncio.run(main())