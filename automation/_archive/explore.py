import asyncio
from playwright.async_api import async_playwright
import json, sys
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
    print("已登录")

    # 进入自营商城应用
    app_url = "https://h2025.jihuifan.com/web/index.php?c=home&a=welcome&do=account_ext&module_name=first_duoduokes&version_id=259"
    await page.goto(app_url, wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    print("进入自营商城应用")
    
    # 获取侧边栏菜单
    links = await page.evaluate("""() => {
        return Array.from(document.querySelectorAll("a")).filter(a => a.href && a.innerText?.trim()).map(a => ({
            text: a.innerText.trim().substring(0,30),
            href: a.href.substring(0,200)
        }));
    }""")
    
    print(f"找到 {len(links)} 个链接:")
    for l in links[:25]:
        print(f"  [{l['text']}] -> {l['href'][:80]}")
    
    await browser.close()
    await pw.stop()

asyncio.run(explore())
