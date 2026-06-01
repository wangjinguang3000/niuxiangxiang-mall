#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""牛香香 · 核心功能配置"""
import asyncio, sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright
from pathlib import Path

BASE = 'https://h2025.jihuifan.com'
LOGIN_URL = f'{BASE}/web/index.php?c=user&a=login&'
APP_URL = f'{BASE}/web/index.php?c=home&a=welcome&do=account_ext&module_name=first_duoduokes&version_id=259'
OUT_DIR = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\automation\output")

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

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await ctx.new_page()
        
        log('登录...')
        await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        await page.fill('input[name=username]', creds['JHF_USERNAME'])
        await page.fill('input[name=password]', creds['JHF_PASSWORD'])
        await page.click('input[type=submit]')
        await asyncio.sleep(4)
        log('登录OK')
        
        # === 1. 底部导航编辑 ===
        log('\n=== 1. 底部导航 ===')
        await go_app(page)
        await page.click('text=底部导航', timeout=5000)
        await asyncio.sleep(4)
        
        # 获取编辑链接
        edit_links = await page.evaluate('''() => {
            var links = document.querySelectorAll("a");
            var r = [];
            links.forEach(function(l) {
                if ((l.innerText || "").includes("编辑")) r.push(l.href);
            });
            return r;
        }''')
        log(f'  编辑链接: {len(edit_links)} 个')
        
        # 编辑第一个导航 (应该是首页)
        nav_config = [
            {"name": "首页", "icon": "home", "link": "/pages/index/index", "sort": "1"},
            {"name": "商品", "icon": "shop", "link": "/pages/shop/index", "sort": "2"},
        ]
        
        for idx, edit_url in enumerate(edit_links[:2]):
            if idx >= len(nav_config):
                break
            log(f'  编辑导航 #{idx+1}: {nav_config[idx]["name"]}')
            await page.goto(edit_url, wait_until='networkidle', timeout=15000)
            await asyncio.sleep(2)
            
            # 看表单
            fields = await page.evaluate('''() => {
                var els = document.querySelectorAll("input:not([type=hidden]):not([type=submit]), textarea, select");
                return Array.from(els).map(function(el) {
                    return {name: el.name || el.id || "", tag: el.tagName, type: el.type || ""};
                }).filter(function(f) { return f.name && f.name !== "token"; });
            }''')
            log(f'    字段: {[(f["name"] + "(" + f["tag"] + ")") for f in fields[:10]]}')
            
            # 填充
            data = nav_config[idx]
            for f in fields:
                name_low = f['name'].lower()
                val = None
                if 'name' in name_low or 'title' in name_low:
                    val = data['name']
                elif 'icon' in name_low:
                    val = data['icon']
                elif 'link' in name_low or 'url' in name_low or 'path' in name_low or 'page' in name_low:
                    val = data['link']
                elif 'sort' in name_low or 'order' in name_low:
                    val = data['sort']
                if val:
                    try:
                        sel = f'[name="{f["name"]}"]'
                        if f['tag'] == 'SELECT':
                            try: await page.select_option(f'select{sel}', val)
                            except: pass
                        else:
                            await page.fill(f'input{sel}', val[:100])
                    except: pass
            
            # 提交
            await asyncio.sleep(0.5)
            for sel in ['input[type=submit]', 'button[type=submit]', 'button:has-text("提交")', 'button:has-text("保存")']:
                try:
                    btn = page.locator(sel)
                    if await btn.count() > 0:
                        await btn.first.click()
                        await asyncio.sleep(3)
                        log(f'    已保存!')
                        break
                except: pass
        
        # === 2. 转盘抽奖配置 ===
        log('\n=== 2. 转盘抽奖 ===')
        await go_app(page)
        await page.click('text=转盘抽奖', timeout=5000)
        await asyncio.sleep(4)
        
        # 截图看转盘设置页面
        await page.screenshot(path=str(OUT_DIR / 'wheel_settings.png'))
        
        # 获取概率设置表单
        settings_url = await page.evaluate('''() => {
            var links = document.querySelectorAll("a");
            for (var i = 0; i < links.length; i++) {
                if ((links[i].innerText || "").includes("设置")) return links[i].href;
            }
            return "";
        }''')
        if settings_url:
            log(f'  设置URL: {settings_url[:120]}')
            await page.goto(settings_url, wait_until='networkidle', timeout=15000)
            await asyncio.sleep(3)
            
            # 看设置表单
            await page.screenshot(path=str(OUT_DIR / 'wheel_config.png'))
            wheel_fields = await page.evaluate('''() => {
                var body = (document.body?.innerText || "").substring(0, 1000);
                var inputs = document.querySelectorAll("input:not([type=hidden])");
                var r = [];
                inputs.forEach(function(el) {
                    r.push({name: el.name || el.id || "", type: el.type, value: el.value});
                });
                return {body: body, inputs: r};
            }''')
            log(f'  转盘设置: {wheel_fields["body"][:400]}')
            log(f'  Inputs: {wheel_fields["inputs"][:15]}')
        
        # === 3. 邀请海报 ===
        log('\n=== 3. 邀请海报 ===')
        await go_app(page)
        await page.click('text=邀请海报', timeout=5000)
        await asyncio.sleep(4)
        await page.screenshot(path=str(OUT_DIR / 'invite_poster.png'))
        
        poster_info = await page.evaluate('''() => {
            return (document.body?.innerText || "").substring(0, 500);
        }''')
        log(f'  海报页面: {poster_info[:300]}')
        
        # === 4. 分享图设计 ===
        log('\n=== 4. 分享图设计 ===')
        await go_app(page)
        await page.click('text=分享图设计', timeout=5000)
        await asyncio.sleep(4)
        await page.screenshot(path=str(OUT_DIR / 'share_design.png'))
        
        share_info = await page.evaluate('''() => {
            return (document.body?.innerText || "").substring(0, 500);
        }''')
        log(f'  分享图页面: {share_info[:300]}')
        
        await browser.close()
        log('\n=== 配置探查完成 ===')

asyncio.run(main())
