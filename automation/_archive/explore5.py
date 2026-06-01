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

    # 进入集汇返模块
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=module&a=welcome&module_name=first_duoduokes", wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    # 点击广告跳转
    await page.click("text=广告跳转", timeout=5000)
    await asyncio.sleep(2)
    print(f"广告跳转URL: {page.url[:120]}")
    
    body = await page.evaluate("() => document.body.innerText")
    print(f"\n页面内容前600字:\n{body[:600]}")
    
    # 点击首页轮播标签
    try:
        await page.click("text=首页轮播", timeout=3000)
        await asyncio.sleep(1)
        print("\n进入首页轮播标签!")
    except:
        print("\n首页轮播不在可见链接中，尝试点击tab")
        # Try clicking tab elements
        tabs = await page.evaluate("""() => {
            const els = document.querySelectorAll('[class*=tab], [class*=nav], .layui-tab-title li, .nav-tabs li');
            return Array.from(els).map(el => ({text: el.innerText?.trim(), cls: el.className}));
        }""")
        for t in tabs:
            print(f"  Tab: [{t['text']}] cls={t['cls']}")
    
    await browser.close()
    await pw.stop()

asyncio.run(explore())
