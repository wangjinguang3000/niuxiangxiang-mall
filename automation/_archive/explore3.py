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
    
    # 点击小程序设置
    await page.click("text=小程序设置", timeout=5000)
    await asyncio.sleep(2)
    print(f"小程序设置URL: {page.url[:120]}")
    
    # 获取子标签页
    links = await page.evaluate("""() => {
        return Array.from(document.querySelectorAll("a")).filter(a => a.href && a.innerText?.trim()).map(a => ({
            text: a.innerText.trim().substring(0,40),
            href: a.href.substring(0,300)
        }));
    }""")
    
    print(f"\n小程序设置下级链接:")
    for l in links:
        if "eid=38" in l["href"] or "first_duoduokes" in l["href"]:
            print(f"  [{l['text']}] -> {l['href'][:150]}")
    
    # 点击首页轮播
    try:
        await page.click("text=首页轮播", timeout=5000)
        await asyncio.sleep(2)
        print(f"\n首页轮播URL: {page.url[:150]}")
        
        # 获取轮播页面链接
        blinks = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll("a")).filter(a => a.href && a.innerText?.trim()).map(a => ({
                text: a.innerText.trim().substring(0,30),
                href: a.href.substring(0,250)
            }));
        }""")
        for l in blinks:
            if "slide" in l["href"] or "增加" in l["text"] or "编辑" in l["text"] or "banner" in l["href"]:
                print(f"  [{l['text']}] -> {l['href'][:150]}")
    except Exception as e:
        print(f"未找到首页轮播: {e}")
    
    await browser.close()
    await pw.stop()

asyncio.run(explore())
