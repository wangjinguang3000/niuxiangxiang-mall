import asyncio
from playwright.async_api import async_playwright, TimeoutError
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

    # 进入商品管理
    product_url = "https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=selfMall&m=first_duoduokes&op=selfMall&version_id=0&tab_id=0"
    await page.goto(product_url, wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    # Click the first "编辑" link
    try:
        edit_links = page.locator("text=编辑")
        count = await edit_links.count()
        print(f"找到 {count} 个编辑链接")
        if count > 0:
            await edit_links.first.click()
            await asyncio.sleep(2)
            print(f"编辑页面URL: {page.url[:150]}")
            
            # Get all form fields
            fields = await page.evaluate("""() => {
                const els = document.querySelectorAll('input, textarea, select');
                return Array.from(els).map(el => ({
                    tag: el.tagName,
                    type: el.type,
                    name: el.name,
                    id: el.id,
                    placeholder: (el.placeholder||'').substring(0,40),
                    value: (el.value||'').substring(0,40)
                }));
            }""")
            
            print(f"\n表单字段 ({len(fields)} 个):")
            for f in fields:
                if f['name'] or f['placeholder']:
                    print(f"  {f['tag']}[name={f['name']}][id={f['id']}] type={f['type']} placeholder={f['placeholder']} value={f['value']}")
    except Exception as e:
        print(f"编辑失败: {e}")
    
    await browser.close()
    await pw.stop()

asyncio.run(explore())
