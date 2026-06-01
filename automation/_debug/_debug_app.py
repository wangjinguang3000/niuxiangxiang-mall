#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过点击侧边栏导航到各模块"""
import asyncio, sys
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
        print('Login OK')
        
        # 进入应用
        await page.goto(APP_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(4)
        print(f'App: {page.url[:120]}')
        await page.screenshot(path=str(OUT_DIR / 'app_home.png'), full_page=True)
        
        # 获取页面所有可见文字，找到侧边栏菜单
        all_text = await page.evaluate('() => document.body.innerText')
        print(f'\n页面文字(前800):\n{all_text[:800]}')
        
        # 找所有链接
        links = await page.evaluate('''() => {
            var all = document.querySelectorAll("a, li, .nav-item, .menu-item, [class*=nav], [class*=menu], [class*=sidebar]");
            return Array.from(all).map(function(el) {
                var text = (el.innerText || "").trim().substring(0, 40);
                var href = (el.href || el.getAttribute("data-url") || el.getAttribute("data-href") || "").substring(0, 120);
                var cls = (el.className || "").substring(0, 60);
                return {text, href, cls, tag: el.tagName};
            }).filter(function(l) { return l.text && l.text.length > 1; });
        }''')
        print(f'\n菜单/链接 ({len(links)}):')
        for l in links[:30]:
            print(f'  [{l["tag"]}] {l["text"]} | {l["href"][:60]} | {l["cls"][:40]}')
        
        await browser.close()

asyncio.run(main())
