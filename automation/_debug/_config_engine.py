#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""牛香香 · 裂变引擎一键配置"""
import asyncio, sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright
from pathlib import Path

BASE = 'https://h2025.jihuifan.com'
LOGIN_URL = f'{BASE}/web/index.php?c=user&a=login&'
APP_URL = f'{BASE}/web/index.php?c=home&a=welcome&do=account_ext&module_name=first_duoduokes&version_id=259'

creds = {}
with open(Path(r"D:\Users\36050\Documents\New project牛香香优选商城\.env"), encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            creds[k.strip()] = v.strip().strip('"').strip("'")

def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}')

async def go_app(page):
    await page.goto(APP_URL, wait_until='networkidle', timeout=20000)
    await asyncio.sleep(3)
    try:
        await page.click('text=更多设置', timeout=5000)
        await asyncio.sleep(2)
    except: pass

async def click_menu(page, name):
    log(f'  点击 "{name}"...')
    await page.click(f'text={name}', timeout=5000)
    await asyncio.sleep(4)
    log(f'  URL: {page.url[:120]}')

async def find_action_link(page, keyword):
    """找发布/添加/编辑等操作链接"""
    return await page.evaluate(f'''(keyword) => {{
        var links = document.querySelectorAll("a");
        for (var i = 0; i < links.length; i++) {{
            var t = (links[i].innerText || "").trim();
            if (t.includes(keyword)) return links[i].href || "";
        }}
        return "";
    }}''', keyword)

async def fill_form_smart(page, data):
    """智能填充表单"""
    await asyncio.sleep(2)
    fields = await page.evaluate('''() => {
        var els = document.querySelectorAll("input:not([type=hidden]):not([type=submit]):not([type=radio]):not([type=checkbox]), textarea, select");
        return Array.from(els).map(function(el) {
            return {name: el.name || el.id || "", tag: el.tagName, type: el.type || ""};
        }).filter(function(f) { return f.name && f.name !== "token"; });
    }''')
    
    log(f'    字段: {[(f["name"] + "(" + f["tag"] + ")") for f in fields[:10]]}')
    
    for f in fields:
        name_low = f['name'].lower()
        val = None
        for key, value in data.items():
            if key.lower() in name_low or name_low in key.lower():
                val = str(value)
                break
        if val is not None:
            try:
                sel = f'[name="{f["name"]}"]'
                if f['tag'] == 'TEXTAREA':
                    await page.fill(f'textarea{sel}', val[:5000])
                elif f['tag'] == 'SELECT':
                    try: await page.select_option(f'select{sel}', val)
                    except: pass
                else:
                    await page.fill(f'input{sel}', val[:300])
            except: pass
    
    await asyncio.sleep(0.5)
    for sel in ['input[type=submit]', 'button[type=submit]', 'button:has-text("提交")', 'button:has-text("保存")']:
        try:
            btn = page.locator(sel)
            if await btn.count() > 0:
                await btn.first.click()
                await asyncio.sleep(3)
                return True
        except: pass
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
        
        # === 1. 广告跳转（首页置顶） ===
        log('\n=== 1. 广告跳转（首页置顶） ===')
        await go_app(page)
        await click_menu(page, '广告跳转')
        
        # Check existing
        existing = await page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var c = 0;
            trs.forEach(function(tr) { 
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 2) c++; 
            });
            return c;
        }''')
        log(f'  现有: {existing} 条')
        
        # Add toplinks
        toplinks = [
            {"title": "🔥 草原人宠互动季报名中", "url": "/pages/event/index", "sort": "1"},
            {"title": "🎁 新人首单立减3元", "url": "/pages/shop/index", "sort": "2"},
        ]
        for item in toplinks:
            add_url = await find_action_link(page, '添加')
            if not add_url:
                add_url = await find_action_link(page, '新增')
            if add_url:
                await page.goto(add_url, wait_until='networkidle', timeout=15000)
                ok = await fill_form_smart(page, item)
                log(f'  {item["title"][:20]}: {"OK" if ok else "FAIL"}')
            else:
                log(f'  找不到添加按钮')
            # 回列表页
            await go_app(page)
            await click_menu(page, '广告跳转')
        
        # === 2. 砍价免费拿 ===
        log('\n=== 2. 砍价免费拿 ===')
        await go_app(page)
        await click_menu(page, '砍价免费拿')
        
        existing = await page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var c = 0;
            trs.forEach(function(tr) { 
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 2 && tds[0].innerText.trim()) c++; 
            });
            return c;
        }''')
        log(f'  现有: {existing} 条')

        # Add bargain item
        add_url = await find_action_link(page, '添加')
        if not add_url:
            add_url = await find_action_link(page, '商品添加')
        if add_url:
            await page.goto(add_url, wait_until='networkidle', timeout=15000)
            log(f'  添加URL: {add_url[:120]}')
            # 探查表单
            fields = await page.evaluate('''() => {
                var els = document.querySelectorAll("input:not([type=hidden]):not([type=submit]), textarea, select");
                return Array.from(els).map(function(el) {
                    return {name: el.name || el.id || "", tag: el.tagName, type: el.type || ""};
                }).filter(function(f) { return f.name && f.name !== "token"; });
            }''')
            log(f'  表单字段: {[(f["name"] + "(" + f["tag"] + ")") for f in fields[:15]]}')
        else:
            log(f'  找不到添加按钮')
        
        # === 3. 一元抢购 ===
        log('\n=== 3. 一元抢购 ===')
        await go_app(page)
        await click_menu(page, '一元抢购')
        
        existing = await page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var c = 0;
            trs.forEach(function(tr) { 
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 2 && tds[0].innerText.trim()) c++; 
            });
            return c;
        }''')
        log(f'  现有: {existing} 条')
        
        add_url = await find_action_link(page, '添加')
        if not add_url:
            add_url = await find_action_link(page, '商品添加')
        if add_url:
            await page.goto(add_url, wait_until='networkidle', timeout=15000)
            fields = await page.evaluate('''() => {
                var els = document.querySelectorAll("input:not([type=hidden]):not([type=submit]), textarea, select");
                return Array.from(els).map(function(el) {
                    return {name: el.name || el.id || "", tag: el.tagName, type: el.type || ""};
                }).filter(function(f) { return f.name && f.name !== "token"; });
            }''')
            log(f'  表单字段: {[(f["name"] + "(" + f["tag"] + ")") for f in fields[:15]]}')
        
        # === 4. 任务管理 ===
        log('\n=== 4. 任务管理 ===')
        await go_app(page)
        await click_menu(page, '任务管理')
        
        tasks = await page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var r = [];
            trs.forEach(function(tr) { 
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 4) {
                    r.push({
                        task: (tds[0]?.innerText || "").trim().substring(0, 20),
                        title: (tds[1]?.innerText || "").trim().substring(0, 30)
                    });
                }
            });
            return r;
        }''')
        log(f'  现有任务: {tasks}')
        
        add_url = await find_action_link(page, '添加')
        if not add_url:
            add_url = await find_action_link(page, '新增')
        if add_url:
            await page.goto(add_url, wait_until='networkidle', timeout=15000)
            fields = await page.evaluate('''() => {
                var els = document.querySelectorAll("input:not([type=hidden]):not([type=submit]), textarea, select");
                return Array.from(els).map(function(el) {
                    return {name: el.name || el.id || "", tag: el.tagName, type: el.type || ""};
                }).filter(function(f) { return f.name && f.name !== "token"; });
            }''')
            log(f'  任务表单字段: {[(f["name"] + "(" + f["tag"] + ")") for f in fields[:15]]}')
        
        # === 5. 转盘抽奖 ===
        log('\n=== 5. 转盘抽奖 ===')
        await go_app(page)
        await click_menu(page, '转盘抽奖')
        
        await asyncio.sleep(2)
        wheel_info = await page.evaluate('''() => {
            return (document.body?.innerText || "").substring(0, 800);
        }''')
        log(f'  转盘页面: {wheel_info[:300]}')
        
        # Look for settings or add button
        for kw in ['添加', '设置', '新增', '概率设置', '奖品']:
            url = await find_action_link(page, kw)
            if url:
                log(f'  [{kw}] URL: {url[:120]}')
        
        # === 6. 底部导航 ===
        log('\n=== 6. 底部导航补齐 ===')
        await go_app(page)
        await click_menu(page, '底部导航')
        
        # Check existing items and their edit links
        nav_items = await page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var r = [];
            trs.forEach(function(tr) { 
                var tds = tr.querySelectorAll("td");
                var links = tr.querySelectorAll("a");
                var linkHrefs = [];
                links.forEach(function(l) {
                    if (l.innerText && (l.innerText.includes("编辑") || l.innerText.includes("修改")))
                        linkHrefs.push(l.href);
                });
                if (tds.length >= 3) {
                    r.push({
                        cells: Array.from(tds).slice(0, 4).map(function(td) { return (td.innerText||"").trim().substring(0, 40); }),
                        editLink: linkHrefs[0] || ""
                    });
                }
            });
            return r;
        }''')
        log(f'  现有导航:')
        for n in nav_items:
            log(f'    {n["cells"]} | edit: {n["editLink"][:80] if n["editLink"] else "none"}')
        
        # Add more nav items if needed
        nav_add = await find_action_link(page, '添加')
        if nav_add:
            await page.goto(nav_add, wait_until='networkidle', timeout=15000)
            fields = await page.evaluate('''() => {
                var els = document.querySelectorAll("input:not([type=hidden]):not([type=submit]), textarea, select");
                return Array.from(els).map(function(el) {
                    return {name: el.name || el.id || "", tag: el.tagName, type: el.type || ""};
                }).filter(function(f) { return f.name && f.name !== "token"; });
            }''')
            log(f'  导航表单字段: {[(f["name"] + "(" + f["tag"] + ")") for f in fields[:15]]}')
        
        await browser.close()
        log('\n=== 探查完成，准备配置 ===')

asyncio.run(main())
