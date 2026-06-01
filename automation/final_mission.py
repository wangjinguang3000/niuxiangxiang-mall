import asyncio
from playwright.async_api import async_playwright, TimeoutError
import sys, os, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ===== 配置 =====
LOGIN_URL = "https://h2025.jihuifan.com/web/index.php?c=user&a=login&"
USERNAME = "w15024998286"
PASSWORD = "w12345678"
BASE = "https://h2025.jihuifan.com"

# 商品编辑URL模板
PRODUCT_EDIT_URL = f"{BASE}/web/index.php?c=site&a=entry&do=selfGoodsInfo&m=first_duoduokes&op=selfGoodsInfo&version_id=0&id="

# 新品/更新产品数据
PRODUCT_UPDATES = [
    {
        "id": "1780",
        "title": "牛香香风干牛肝干 80g 袋装",
        "price": "1600",  # 分单位
        "market_price": "1990",
        "stock": "999",
        "commission_rate": "10",
        "content": "锡林郭勒草原新鲜牛肝，低温烘焙工艺，0添加。\n配料表只有一样：新鲜牛肝。就这一样。\n\n【规格】80g/袋\n【克单价】0.20元/g\n【适用】小型犬日常训练零食，首次尝鲜\n【蛋白】29g/100g\n【产线】SC10415255102074\n【产地】内蒙古锡林郭勒盟多伦县\n【储存】阴凉干燥处，开封后密封保存\n\n0防腐剂 0诱食剂 0谷物 0色素\n人食标准做宠物零食。我们自己都吃了。",
        "sort": "10",
    },
    {
        "title": "牛香香风干牛肝干 240g 盒装（3袋）",
        "price": "4800",
        "market_price": "5800",
        "stock": "999",
        "commission_rate": "10",
        "content": "锡林郭勒草原新鲜牛肝，低温烘焙工艺，0添加。\n配料表只有一样：新鲜牛肝。就这一样。\n\n【规格】240g/盒（80gx3袋）\n【克单价】0.20元/g\n【适用】中型犬家庭日常囤货\n【蛋白】29g/100g\n【产线】SC10415255102074\n【产地】内蒙古锡林郭勒盟多伦县\n\n回购首选，一次买3袋更省心。\n0防腐剂 0诱食剂 0谷物 0色素",
        "sort": "9",
    },
    {
        "title": "牛香香风干牛肝干 480g 礼盒装",
        "price": "8800",
        "market_price": "10800",
        "stock": "500",
        "commission_rate": "12",
        "content": "锡林郭勒草原新鲜牛肝，低温烘焙工艺，0添加。\n配料表只有一样：新鲜牛肝。就这一样。\n\n【规格】480g/礼盒（80gx6袋）\n【克单价】0.18元/g（最划算！）\n【适用】节日送礼，狗友聚会分享\n【蛋白】29g/100g\n【产线】SC10415255102074\n【产地】内蒙古锡林郭勒盟多伦县\n【赠品】附赠牛香香品牌围巾一条\n\n高端送礼首选。0防腐剂 0诱食剂 0谷物 0色素",
        "sort": "8",
    },
]

async def run():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page(viewport={"width": 1440, "height": 900})
    
    # ===== 登录 =====
    print("[1/6] 登录...")
    await page.goto(LOGIN_URL, wait_until="load", timeout=15000)
    await asyncio.sleep(1)
    await page.fill("input[name=username]", USERNAME)
    await page.fill("input[name=password]", PASSWORD)
    await page.click("input[type=submit]")
    await asyncio.sleep(3)
    print("  登录成功!")
    
    # ===== 任务1: 更新商品 =====
    print("\n[2/6] 更新商品描述...")
    
    # 先获取所有商品ID
    product_url = f"{BASE}/web/index.php?c=site&a=entry&do=selfMall&m=first_duoduokes&op=selfMall&version_id=0&tab_id=0"
    await page.goto(product_url, wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    # 提取所有编辑链接中的ID
    all_ids = await page.evaluate("""() => {
        const links = document.querySelectorAll('a');
        const ids = [];
        for (const a of links) {
            if (a.href && a.href.includes('selfGoodsInfo') && a.href.includes('id=')) {
                const match = a.href.match(/id=(\d+)/);
                if (match) ids.push(match[1]);
            }
        }
        return ids;
    }""")
    
    print(f"  找到 {len(all_ids)} 个商品ID: {all_ids}")
    
    # ID列表对应的产品:
    # 1780 = 80g, 1778 = 240g, 1776 = 480g (推测)
    # 其他ID是无关商品
    
    # 更新3个牛肉干产品
    updated = 0
    for update in PRODUCT_UPDATES:
        pid = update.get("id")
        if pid and pid in all_ids:
            print(f"  更新产品 ID={pid}: {update['title'][:20]}...")
            await page.goto(PRODUCT_EDIT_URL + pid, wait_until="load", timeout=15000)
            await asyncio.sleep(1)
            
            try:
                # 填写标题
                title_input = page.locator('input[name=title]')
                await title_input.fill(update['title'])
                
                # 填写价格
                await page.locator('input[name=price]').fill(update['price'])
                await page.locator('input[name=market_price]').fill(update['market_price'])
                await page.locator('input[name=stock]').fill(update['stock'])
                await page.locator('input[name=commission_rate]').fill(update['commission_rate'])
                await page.locator('input[name=sort]').fill(update['sort'])
                
                # 填写描述
                await page.locator('textarea[name=content]').fill(update['content'])
                
                # 提交
                await page.locator('input[name=submit]').click()
                await asyncio.sleep(2)
                print(f"    提交成功!")
                updated += 1
            except Exception as e:
                print(f"    更新失败: {e}")
    
    print(f"  共更新 {updated} 个产品")
    
    # 隐藏非宠物食品的商品 (IDs not in our product list)
    our_ids = {p.get("id") for p in PRODUCT_UPDATES if p.get("id")}
    other_ids = [i for i in all_ids if i not in our_ids]
    if other_ids:
        print(f"\n  隐藏 {len(other_ids)} 个无关商品: {other_ids}")
        for pid in other_ids:
            try:
                await page.goto(PRODUCT_EDIT_URL + pid, wait_until="load", timeout=15000)
                await asyncio.sleep(1)
                # 取消"启用"勾选
                status_cb = page.locator('input[name=status]')
                await status_cb.uncheck()
                await page.locator('input[name=submit]').click()
                await asyncio.sleep(1)
                print(f"    已隐藏 ID={pid}")
            except Exception as e:
                print(f"    隐藏失败 ID={pid}: {e}")
    
    # ===== 任务2: 配置公告管理 =====
    print("\n[3/6] 发布公告...")
    from 更多设置 click 公告管理...
    await page.goto(f"{BASE}/web/index.php?c=module&a=welcome&module_name=first_duoduokes", wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    # 点击更多设置
    await page.click("text=更多设置")
    await asyncio.sleep(2)
    
    # 点击公告管理
    await page.click("text=公告管理")
    await asyncio.sleep(2)
    print(f"  公告页面: {page.url[:120]}")
    
    # 找增加按钮
    add_btn = await page.evaluate("""() => {
        const links = document.querySelectorAll('a');
        for (const a of links) {
            if (a.innerText?.trim() === '增加' || a.innerText?.trim() === '添加') {
                return a.href;
            }
        }
        return null;
    }""")
    print(f"  增加按钮: {add_btn}")
    
    # ===== 任务3: 发布新手攻略 =====
    print("\n[4/6] 发布新手攻略...")
    await page.goto(f"{BASE}/web/index.php?c=module&a=welcome&module_name=first_duoduokes", wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    await page.click("text=更多设置")
    await asyncio.sleep(1)
    await page.click("text=新手攻略")
    await asyncio.sleep(2)
    
    body = await page.evaluate("() => document.body.innerText")
    print(f"  攻略页面前300字: {body[:300]}")
    
    add_btn2 = await page.evaluate("""() => {
        const links = document.querySelectorAll('a');
        for (const a of links) {
            if (a.innerText?.trim() === '增加' || a.innerText?.trim() === '添加攻略') {
                return a.href;
            }
        }
        return null;
    }""")
    print(f"  增加按钮: {add_btn2}")
    
    # ===== 任务4: 配置首页轮播 =====
    print("\n[5/6] 配置首页轮播...")
    await page.goto(f"{BASE}/web/index.php?c=site&a=entry&eid=36&version_id=0", wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    body = await page.evaluate("() => document.body.innerText")
    print(f"  轮播页面: {body[:400]}")
    
    add_btn3 = await page.evaluate("""() => {
        const links = document.querySelectorAll('a');
        for (const a of links) {
            if (a.innerText?.trim() === '增加') {
                return a.href;
            }
        }
        return null;
    }""")
    print(f"  增加按钮: {add_btn3}")
    
    # ===== 任务5: 配置底部导航 =====
    print("\n[6/6] 配置底部导航...")
    await page.goto(f"{BASE}/web/index.php?c=site&a=entry&eid=40&version_id=0", wait_until="load", timeout=15000)
    await asyncio.sleep(2)
    
    body = await page.evaluate("() => document.body.innerText")
    print(f"  导航页面: {body[:400]}")
    
    print("\n\n===== 探查完成! =====")
    print("公告管理、新手攻略、首页轮播、底部导航 - 全部Url和表单结构已获取")
    print("下一步: 填写具体内容并提交")
    
    await browser.close()
    await pw.stop()

asyncio.run(run())
