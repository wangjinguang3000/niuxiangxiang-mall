#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""牛香香 · 最终配置补齐"""
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
        
        # 进入应用+展开菜单
        await page.goto(APP_URL, wait_until='networkidle', timeout=20000)
        await asyncio.sleep(3)
        try:
            await page.click('text=更多设置', timeout=5000)
            await asyncio.sleep(2)
        except: pass
        
        # === 1. 添加更多导航项 ===
        log('\n=== 添加底部导航（赛事+我的） ===')
        await page.click('text=底部导航', timeout=5000)
        await asyncio.sleep(4)
        
        # 找"增加"按钮
        add_url = await page.evaluate('''() => {
            var links = document.querySelectorAll("a");
            for (var i = 0; i < links.length; i++) {
                var t = (links[i].innerText || "").trim();
                if (t === "增加" || t.includes("增加")) return links[i].href;
            }
            return "";
        }''')
        log(f'  增加URL: {add_url[:120] if add_url else "未找到"}')
        
        new_navs = [
            {"title": "赛事", "type_val": "原小程序", "path": "/pages/event/index", "sort": "3"},
            {"title": "我的", "type_val": "原小程序", "path": "/pages/my/index", "sort": "4"},
        ]
        
        for item in new_navs:
            if add_url:
                await page.goto(add_url, wait_until='networkidle', timeout=15000)
                await asyncio.sleep(2)
                
                # Fill form
                # title
                try: await page.fill('input[name="title"]', item['title'])
                except: pass
                # path (select)
                try: await page.select_option('select[name="path"]', item['path'])
                except: pass
                # sort
                try: await page.fill('input[name="sort"]', item['sort'])
                except: pass
                
                # 提交
                await asyncio.sleep(0.5)
                for sel in ['input[type=submit]', 'button[type=submit]', 'button:has-text("提交")', 'button:has-text("保存")']:
                    try:
                        btn = page.locator(sel)
                        if await btn.count() > 0:
                            await btn.first.click()
                            await asyncio.sleep(3)
                            log(f'  {item["title"]}: 已保存!')
                            break
                    except: pass
            else:
                log(f'  无增加链接，尝试直接URL')
                # Try constructing URL directly
                post_url = f'{BASE}/web/index.php?c=site&a=entry&do=bottomNavInfo&m=first_duoduokes&op=bottomNavInfo&version_id=259'
                await page.goto(post_url, wait_until='networkidle', timeout=15000)
                await asyncio.sleep(2)
                try: await page.fill('input[name="title"]', item['title'])
                except: pass
                try: await page.select_option('select[name="path"]', item['path'])
                except: pass
                try: await page.fill('input[name="sort"]', item['sort'])
                except: pass
                for sel in ['input[type=submit]', 'button[type=submit]']:
                    try:
                        btn = page.locator(sel)
                        if await btn.count() > 0:
                            await btn.first.click()
                            await asyncio.sleep(3)
                            log(f'  {item["title"]}: 已保存!')
                            break
                    except: pass
        
        # === 2. 转盘抽奖概率设置 ===
        log('\n=== 转盘抽奖概率 ===')
        await page.goto(APP_URL, wait_until='networkidle', timeout=20000)
        await asyncio.sleep(3)
        try:
            await page.click('text=更多设置', timeout=5000)
            await asyncio.sleep(2)
        except: pass
        await page.click('text=转盘抽奖', timeout=5000)
        await asyncio.sleep(4)
        
        # Look for 概率设置 form on the page itself
        wheel_form = await page.evaluate('''() => {
            var inputs = document.querySelectorAll("input[type=text], input[type=number]");
            return Array.from(inputs).map(function(el) {
                return {name: el.name || el.id || "", value: el.value || ""};
            }).filter(function(f) { return f.name; });
        }''')
        log(f'  转盘概率输入: {wheel_form[:10]}')
        
        # Try the direct turntable settings URL
        await page.goto(f'{BASE}/web/index.php?c=site&a=entry&do=turntableRotary&m=first_duoduokes&op=turntableRotary&version_id=259&tab_id=0', wait_until='networkidle', timeout=15000)
        await asyncio.sleep(3)
        
        wheel_body = await page.evaluate('''() => {
            return (document.body?.innerText || "").substring(0, 800);
        }''')
        log(f'  转盘页面内容: {wheel_body[:500]}')
        
        # === 3. 最终导航验证 ===
        log('\n=== 验证底部导航 ===')
        await page.goto(APP_URL, wait_until='networkidle', timeout=20000)
        await asyncio.sleep(3)
        try:
            await page.click('text=更多设置', timeout=5000)
            await asyncio.sleep(2)
        except: pass
        await page.click('text=底部导航', timeout=5000)
        await asyncio.sleep(4)
        
        nav_final = await page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var r = [];
            trs.forEach(function(tr) {
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 6) {
                    r.push({
                        title: (tds[0]?.innerText || "").trim(),
                        action: (tds[3]?.innerText || "").trim(),
                        status: (tds[5]?.innerText || "").trim(),
                    });
                }
            });
            return r;
        }''')
        log(f'  导航最终状态:')
        for n in nav_final:
            log(f'    {n["title"]} | {n["action"]} | {n["status"]}')
        
        await browser.close()
        log('\n=== 全部完成 ===')

asyncio.run(main())
