#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探查模块页面真实结构"""
import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright
from pathlib import Path

BASE = 'https://h2025.jihuifan.com'
LOGIN_URL = f'{BASE}/web/index.php?c=user&a=login&'
OUT_DIR = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\automation\output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

env_file = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\.env")
creds = {}
with open(env_file, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            creds[k.strip()] = v.strip().strip('"').strip("'")

modules = [
    ("公告(notice)", f'{BASE}/web/index.php?c=site&a=entry&do=notice&m=first_duoduokes&op=notice&tab_id=0'),
    ("攻略(article)", f'{BASE}/web/index.php?c=site&a=entry&do=article&m=first_duoduokes&op=article&tab_id=0'),
    ("置顶(topnav)", f'{BASE}/web/index.php?c=site&a=entry&do=topnav&m=first_duoduokes&op=topnav&tab_id=0'),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await ctx.new_page()
        
        # 登录
        print('Login...')
        await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        await page.fill('input[name=username]', creds['JHF_USERNAME'])
        await page.fill('input[name=password]', creds['JHF_PASSWORD'])
        await page.click('input[type=submit]')
        await asyncio.sleep(4)
        print(f'Login OK: {page.url[:80]}')
        
        for name, url in modules:
            print(f'\n=== {name} ===')
            await page.goto(url, wait_until='networkidle', timeout=20000)
            await asyncio.sleep(2)
            
            # 截图
            safe = name.split('(')[0]
            await page.screenshot(path=str(OUT_DIR / f'debug_{safe}.png'), full_page=True)
            
            # 找所有链接
            links = await page.evaluate('''() => {
                var all = document.querySelectorAll("a");
                return Array.from(all).map(function(a) {
                    return {
                        text: (a.innerText || "").trim().substring(0, 40),
                        href: (a.href || "").substring(0, 200),
                        class: (a.className || "").substring(0, 60)
                    };
                }).filter(function(l) { return l.text || l.href; });
            }''')
            print(f'  链接数: {len(links)}')
            for l in links[:15]:
                print(f'    [{l["text"]}] -> {l["href"][:80]}')
            
            # 找所有按钮
            buttons = await page.evaluate('''() => {
                var all = document.querySelectorAll("button, input[type=submit], input[type=button]");
                return Array.from(all).map(function(b) {
                    return {
                        text: (b.innerText || b.value || "").trim().substring(0, 40),
                        type: b.type || "",
                        tag: b.tagName
                    };
                });
            }''')
            print(f'  按钮数: {len(buttons)}')
            for b in buttons[:10]:
                print(f'    [{b["tag"]}] {b["text"]}')
            
            # 检查iframe
            iframes = await page.evaluate('''() => {
                return document.querySelectorAll("iframe").length;
            }''')
            print(f'  iframe数: {iframes}')
            
            # 页面body前500字符
            body = await page.evaluate('() => document.body.innerText.substring(0, 500)')
            print(f'  Body(前200字): {body[:200]}')
        
        await browser.close()

asyncio.run(main())
