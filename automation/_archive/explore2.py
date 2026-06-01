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
    print("已登录")

    # 进入集汇返模块首页
    app_url = "https://h2025.jihuifan.com/web/index.php?c=module&a=welcome&module_name=first_duoduokes"
    await page.goto(app_url, wait_until="load", timeout=15000)
    await asyncio.sleep(3)
    print(f"当前URL: {page.url[:120]}")
    
    # 获取页面所有链接
    links = await page.evaluate("""() => {
        return Array.from(document.querySelectorAll("a")).filter(a => a.href && a.innerText?.trim()).map(a => ({
            text: a.innerText.trim().substring(0,30),
            href: a.href.substring(0,250)
        }));
    }""")
    
    print(f"找到 {len(links)} 个链接:")
    for l in links[:30]:
        # filter to only store-related
        if "first_duoduokes" in l["href"] or "store" in l["text"] or len(l["text"]) > 0:
            print(f"  [{l['text']}]")

    # Click "自营商城" 
    try:
        await page.click("text=自营商城", timeout=5000)
        await asyncio.sleep(2)
        print(f"\n进入自营商城后URL: {page.url[:120]}")
        
        # Get links again
        links2 = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll("a")).filter(a => a.href && a.innerText?.trim()).map(a => ({
                text: a.innerText.trim().substring(0,40),
                href: a.href.substring(0,300)
            }));
        }""")
        print(f"自营商城下级链接 {len(links2)} 个:")
        for l in links2:
            print(f"  [{l['text']}] -> {l['href'][:120]}")
    except Exception as e:
        print(f"点击自营商城失败: {e}")
    
    await browser.close()
    await pw.stop()

asyncio.run(explore())
