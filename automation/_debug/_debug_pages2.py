#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用正确的路径探查模块"""
import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright
from pathlib import Path

BASE = 'https://h2025.jihuifan.com'
LOGIN_URL = f'{BASE}/web/index.php?c=user&a=login&'
APP_URL = f'{BASE}/web/index.php?c=home&a=welcome&do=account_ext&module_name=first_duoduokes&version_id=259'
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

# 测试不同URL格式
modules = [
    ("公告-direct", f'{BASE}/web/index.php?c=site&a=entry&do=notice&module_name=first_duoduokes&direct=1'),
    ("公告-m", f'{BASE}/web/index.php?c=site&a=entry&do=notice&m=first_duoduokes&op=notice&tab_id=0'),
    ("攻略-direct", f'{BASE}/web/index.php?c=site&a=entry&do=article&module_name=first_duoduokes&direct=1'),
    ("攻略-m", f'{BASE}/web/index.php?c=site&a=entry&do=article&m=first_duoduokes&op=article&tab_id=0'),
    ("置顶-direct", f'{BASE}/web/index.php?c=site&a=entry&do=topnav&module_name=first_duoduokes&direct=1'),
    ("置顶-m", f'{BASE}/web/index.php?c=site&a=entry&do=topnav&m=first_duoduokes&op=topnav&tab_id=0'),
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
        print(f'Login OK')
        
        # 先进入应用
        print('\n进入应用...')
        await page.goto(APP_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)
        print(f'App URL: {page.url[:120]}')
        
        # 测试每个模块
        for name, url in modules:
            print(f'\n=== {name} ===')
            await page.goto(url, wait_until='load', timeout=20000)
            await asyncio.sleep(3)
            
            # 再等一会儿让JS加载
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            await asyncio.sleep(2)
            
            safe = name.replace('(', '_').replace(')', '')
            await page.screenshot(path=str(OUT_DIR / f'debug2_{safe}.png'), full_page=True)
            
            url_now = page.url[:120]
            body = await page.evaluate('() => (document.body?.innerText || "").substring(0, 300)')
            links = await page.evaluate('() => document.querySelectorAll("a").length')
            btns = await page.evaluate('() => document.querySelectorAll("button, input[type=submit]").length')
            frames = await page.evaluate('() => document.querySelectorAll("iframe").length')
            
            print(f'  URL: {url_now}')
            print(f'  a:{links} btn:{btns} iframe:{frames}')
            print(f'  Body: {body[:150]}')
        
        await browser.close()

asyncio.run(main())
