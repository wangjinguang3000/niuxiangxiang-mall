import asyncio
from playwright.async_api import async_playwright
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

async def explore():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page(viewport={"width": 1440, "height": 900})
    
    # Login
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=user&a=login&", wait_until="load", timeout=15000)
    await asyncio.sleep(1)
    await page.fill("input[name=username]", "w15024998286")
    await page.fill("input[name=password]", "w12345678")
    await page.click("input[type=submit]")
    await asyncio.sleep(3)

    # 进入商品管理
    product_url = "https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=selfMall&m=first_duoduokes&op=selfMall&version_id=0&tab_id=0"
    await page.goto(product_url, wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    body = await page.evaluate("() => document.body.innerText")
    print(f"商品管理页面:\n{body[:1000]}")
    
    # 获取商品列表
    rows = await page.evaluate("""() => {
        const rows = document.querySelectorAll('table tr');
        return Array.from(rows).slice(0, 15).map(tr => {
            const cells = tr.querySelectorAll('td, th');
            return Array.from(cells).map(c => c.innerText?.trim().substring(0, 30));
        });
    }""")
    print(f"\n商品列表 (前15行):")
    for i, row in enumerate(rows):
        print(f"  Row {i}: {row}")
    
    await browser.close()
    await pw.stop()

asyncio.run(explore())
