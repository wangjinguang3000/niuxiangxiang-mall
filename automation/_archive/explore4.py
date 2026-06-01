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
    
    # 点击更多设置
    await page.click("text=更多设置", timeout=5000)
    await asyncio.sleep(2)
    print(f"更多设置URL: {page.url[:120]}")
    
    # 获取页面文本
    body = await page.evaluate("() => document.body.innerText")
    print(f"\n页面内容前500字:\n{body[:500]}")
    
    # 获取子标签
    links = await page.evaluate("""() => {
        return Array.from(document.querySelectorAll("a, .nav-tabs li, .tab-item, .layui-tab-title li, [class*=tab]")).map(el => ({
            text: (el.innerText||el.textContent||'').trim().substring(0,40),
            tag: el.tagName,
            cls: el.className?.substring(0,50)
        }));
    }""")
    
    print("\n标签页:")
    seen = set()
    for l in links:
        if l["text"] and l["text"] not in seen and len(l["text"]) < 20:
            seen.add(l["text"])
            print(f"  [{l['text']}] ({l['tag']})")

    await browser.close()
    await pw.stop()

asyncio.run(explore())
