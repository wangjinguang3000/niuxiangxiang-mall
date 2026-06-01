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
    
    # Go to top links (置顶跳转)
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=site&a=entry&eid=36&version_id=0", wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(2)
    
    # Click the "置顶跳转" tab
    try:
        await page.click("text=首页置顶跳转", timeout=3000)
        await asyncio.sleep(2)
        print("Clicked toplinks tab")
    except:
        print("Toplinks tab not clickable, trying URL")
        await page.goto("https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=indexTopNav&m=first_duoduokes&op=indexTopNav&version_id=0", wait_until="domcontentloaded", timeout=10000)
        await asyncio.sleep(2)
    
    body = await page.evaluate("() => document.body.innerText")
    print(f"Page: {body[:500]}")
    
    # Find add button
    add_url = await page.evaluate("""() => {
        var links = document.querySelectorAll("a");
        for (var i=0; i<links.length; i++) {
            if (links[i].innerText && links[i].innerText.trim() === "增加") {
                return links[i].href;
            }
        }
        return null;
    }""")
    print(f"Add URL: {add_url}")
    
    # Explore the add form
    if add_url:
        await page.goto(add_url, wait_until="domcontentloaded", timeout=10000)
        await asyncio.sleep(1)
        
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
        
        # Add a toplink
        print("\nAdding toplink...")
        try:
            await page.locator("input[name=title]").fill("Sign Up")
            cb = page.locator("input[name=status]")
            if not await cb.is_checked():
                await cb.check()
            await page.locator("input[name=submit]").click()
            await asyncio.sleep(2)
            print("  Added!")
        except Exception as e:
            print(f"  Fail: {e}")
    
    print("\n=== Toplinks Done! ===")
    await browser.close()
    await pw.stop()

asyncio.run(main())