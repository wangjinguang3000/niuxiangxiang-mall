#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过UI点击导航+添加内容 v3"""
import asyncio, sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright
from pathlib import Path

BASE = 'https://h2025.jihuifan.com'
LOGIN_URL = f'{BASE}/web/index.php?c=user&a=login&'
APP_URL = f'{BASE}/web/index.php?c=home&a=welcome&do=account_ext&module_name=first_duoduokes&version_id=259'
OUT_DIR = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\automation\output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

creds = {}
with open(Path(r"D:\Users\36050\Documents\New project牛香香优选商城\.env"), encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            creds[k.strip()] = v.strip().strip('"').strip("'")

ANNOUNCEMENTS = [
    {"title": "草原人宠互动季正式启动！", "content": "牛香香草原人宠互动季第一季开放报名！\n\n时间：2026年7月\n地点：内蒙古锡林郭勒多伦县\n规模：60-100组（1人+1狗）\n\n四大比赛项目：\n1. 意志力挑战赛——面对牛排坐住不动\n2. 叼物接力赛——草原上奔跑接力\n3. 趣味障碍赛——隧道+跳杆+绕桩\n4. 才艺大比拼——各种才艺都欢迎\n\n咨询电话：13145294218 王经理"},
    {"title": "牛香香牛肝干正式上线！配料表只有新鲜牛肝", "content": "牛香香牛肝干正式上线！\n\n人食标准做宠物零食\n\n零添加承诺：0防腐剂、0诱食剂、0谷物、0色素\n配料表只有一样：新鲜牛肝\n\n三种规格：80g袋装¥16、240g盒装¥48、480g礼盒装¥88\n\n自有工厂 SC10415255102074 内蒙古锡林郭勒"},
    {"title": "招商加盟 寻找城市合伙人", "content": "牛香香正在寻找热爱宠物的城市合伙人！\n\n我们提供：自有工厂直供、完整品牌故事、一人可操作轻资产模式、赛事IP赋能\n\n适合人群：宠物店主、宠物博主达人、社群群主团长\n\n合作模式：一件代发（零库存）、区域代理（独家区域）、品牌联名（定制包装）\n\n咨询电话：13145294218 王经理"},
]

def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}')

async def navigate_to_module(page, menu_name):
    """通过侧边栏导航到指定模块"""
    # 进入应用
    await page.goto(APP_URL, wait_until='networkidle', timeout=20000)
    await asyncio.sleep(3)
    # 展开"更多设置"
    try:
        await page.click('text=更多设置', timeout=5000)
        await asyncio.sleep(2)
    except:
        pass
    # 点击目标菜单
    log(f'  点击"{menu_name}"...')
    await page.click(f'text={menu_name}', timeout=5000)
    await asyncio.sleep(4)
    log(f'  URL: {page.url[:120]}')

async def click_add_button(page):
    """查找并点击发布/添加按钮"""
    # 查找链接文字包含"发布"或"添加"的
    add_url = await page.evaluate('''() => {
        var links = document.querySelectorAll("a");
        for (var i = 0; i < links.length; i++) {
            var t = (links[i].innerText || "").trim();
            if (t.includes("发布") || t.includes("添加") || t.includes("新增")) {
                return links[i].href || "";
            }
        }
        return "";
    }''')
    log(f'  添加URL: {add_url[:150]}')
    return add_url

async def fill_form(page, item):
    """填充表单并提交"""
    await asyncio.sleep(2)
    
    # 截图
    await page.screenshot(path=str(OUT_DIR / 'form_before.png'))
    
    # 获取表单字段
    fields = await page.evaluate('''() => {
        var els = document.querySelectorAll("input:not([type=hidden]):not([type=submit]):not([type=checkbox]), textarea, select");
        return Array.from(els).map(function(el) {
            return {name: el.name || el.id || "", tag: el.tagName, type: el.type || "", placeholder: (el.placeholder||"").substring(0,30)};
        }).filter(function(f) { return f.name && f.name !== "token" && f.name !== "submit"; });
    }''')
    
    log(f'  表单字段 ({len(fields)}):')
    for f in fields[:15]:
        log(f'    {f["tag"]}[name="{f["name"]}"] type={f["type"]}')
    
    if not fields:
        log('  无表单字段，截图保存')
        await page.screenshot(path=str(OUT_DIR / 'form_empty.png'))
        return False
    
    # 填充
    for f in fields:
        name_low = f['name'].lower()
        val = None
        if any(k in name_low for k in ['title', 'name', 'cname', 'subject']):
            val = item.get('title', '')
        elif any(k in name_low for k in ['content', 'desc', 'detail', 'info', 'intro', 'body', 'text', 'article', 'message']):
            val = item.get('content', '')
        elif any(k in name_low for k in ['sort', 'order', 'displayorder', 'rank', 'weight']):
            val = item.get('sort', '1')
        elif any(k in name_low for k in ['link', 'url', 'href']):
            val = item.get('link', item.get('url', ''))
        
        if val is not None:
            try:
                sel = f'[name="{f["name"]}"]'
                if f['tag'] == 'TEXTAREA':
                    await page.fill(f'textarea{sel}', str(val)[:5000])
                elif f['tag'] == 'SELECT':
                    try:
                        await page.select_option(f'select{sel}', str(val))
                    except:
                        pass
                else:
                    await page.fill(f'input{sel}', str(val)[:300])
            except Exception as e:
                pass
    
    # 提交
    await asyncio.sleep(0.5)
    for sel in ['input[type=submit]', 'button[type=submit]', 'button:has-text("提交")', 'button:has-text("保存")', 'input.btn-primary', 'button:has-text("发布")']:
        try:
            btn = page.locator(sel)
            if await btn.count() > 0:
                await btn.first.click()
                await asyncio.sleep(3)
                log(f'  已提交!')
                return True
        except:
            pass
    
    log(f'  未找到提交按钮')
    return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await ctx.new_page()
        
        # 登录
        log('登录...')
        await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        await page.fill('input[name=username]', creds['JHF_USERNAME'])
        await page.fill('input[name=password]', creds['JHF_PASSWORD'])
        await page.click('input[type=submit]')
        await asyncio.sleep(4)
        log('登录OK')
        
        # === 公告管理 ===
        log('\n=== 公告管理 ===')
        await navigate_to_module(page, '公告管理')
        
        # 先看看有多少条
        count = await page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var c = 0;
            trs.forEach(function(tr) { 
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 3) c++; 
            });
            return c;
        }''')
        log(f'  现有 {count} 条公告')
        
        for idx, item in enumerate(ANNOUNCEMENTS):
            log(f'  [{idx+1}/3] {item["title"][:30]}...')
            
            # 重新导航到列表页
            await navigate_to_module(page, '公告管理')
            
            # 点击"公告发布"
            add_url = await click_add_button(page)
            if not add_url:
                log('  找不到添加按钮!')
                continue
            
            await page.goto(add_url, wait_until='networkidle', timeout=15000)
            if not await fill_form(page, item):
                log('  填充/提交失败')
                continue
        
        await browser.close()
        log('\n完成!')

asyncio.run(main())
