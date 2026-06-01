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
    
    # Go to announcements directly
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=offNoticeManage&m=first_duoduokes&op=offNoticeManage&version_id=0", wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(2)
    
    body = await page.evaluate("() => document.body.innerText")
    print(f"Page content:\n{body[:600]}")
    
    # Get ALL links
    links = await page.evaluate("""() => {
        var all = document.querySelectorAll("a, button, input[type=submit], input[type=button]");
        var result = [];
        for (var i=0; i<all.length; i++) {
            var el = all[i];
            var text = (el.innerText || el.value || el.textContent || "").trim();
            if (text.length > 0) {
                result.push({
                    tag: el.tagName,
                    text: text.substring(0,20),
                    href: el.href ? el.href.substring(0,150) : "no-href",
                    type: el.type || ""
                });
            }
        }
        return result;
    }""")
    
    print(f"\nAll clickable elements:")
    for l in links:
        print(f"  {l['tag']} [{l['text']}] href={l['href'][:80]} type={l['type']}")
    
    await browser.close()
    await pw.stop()

asyncio.run(main())