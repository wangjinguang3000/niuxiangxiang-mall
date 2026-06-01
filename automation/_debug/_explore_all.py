#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""牛香香商城 · 后台全模块探查 v3"""
import asyncio, sys, time
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright
from pathlib import Path

env_file = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\.env")
creds = {}
with open(env_file, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            creds[k.strip()] = v.strip().strip('"').strip("'")

USERNAME = creds['JHF_USERNAME']
PASSWORD = creds['JHF_PASSWORD']
LOGIN_URL = 'https://h2025.jihuifan.com/web/index.php?c=user&a=login&'
BASE_URL = 'https://h2025.jihuifan.com'
OUT_DIR = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\automation\output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def now():
    return datetime.now().strftime('%H:%M:%S')

async def explore():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await ctx.new_page()
        
        # ===== 登录 =====
        print(f'[{now()}] >>> 登录后台...')
        await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        if 'login' in page.url.lower():
            await page.fill('input[name=username]', USERNAME)
            await page.fill('input[name=password]', PASSWORD)
            await page.click('input[type=submit]')
            await asyncio.sleep(4)
        ok = 'login' not in page.url.lower()
        print(f'[{now()}] 登录: {"OK" if ok else "FAIL"} | URL: {page.url[:80]}')
        if not ok:
            await browser.close()
            return
        
        # ===== 导航到应用 =====
        app_url = f"{BASE_URL}/web/index.php?c=home&a=welcome&do=account_ext&module_name=first_duoduokes&version_id=259"
        await page.goto(app_url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)
        print(f'[{now()}] >>> 进入应用: {page.url[:100]}')
        
        modules = [
            ("商品管理", f"{BASE_URL}/web/index.php?c=site&a=entry&do=selfMall&m=first_duoduokes&op=selfMall&tab_id=0"),
            ("首页轮播", f"{BASE_URL}/web/index.php?c=site&a=entry&do=indexSwiper&m=first_duoduokes&op=indexSwiper&tab_id=0"),
            ("公告管理", f"{BASE_URL}/web/index.php?c=site&a=entry&do=notice&m=first_duoduokes&op=notice&tab_id=0"),
            ("新手攻略", f"{BASE_URL}/web/index.php?c=site&a=entry&do=article&m=first_duoduokes&op=article&tab_id=0"),
            ("底部导航", f"{BASE_URL}/web/index.php?c=site&a=entry&do=bottomnav&m=first_duoduokes&op=bottomnav&tab_id=0"),
            ("置顶跳转", f"{BASE_URL}/web/index.php?c=site&a=entry&do=topnav&m=first_duoduokes&op=topnav&tab_id=0"),
            ("分销管理", f"{BASE_URL}/web/index.php?c=site&a=entry&do=commission&m=first_duoduokes&op=commission&tab_id=0"),
        ]
        
        results = {}
        for name, url in modules:
            print(f'\n[{now()}] === {name} ===')
            try:
                await page.goto(url, wait_until='networkidle', timeout=20000)
                await asyncio.sleep(2)
                # 提取表格数据
                data = await page.evaluate('''() => {
                    var rows = document.querySelectorAll("table tr, table tbody tr");
                    var r = [];
                    rows.forEach(function(row) {
                        var cells = row.querySelectorAll("td, th");
                        var rowData = [];
                        cells.forEach(function(c) {
                            var t = (c.innerText || "").trim().substring(0, 80);
                            if (t) rowData.push(t);
                        });
                        if (rowData.length >= 2) r.push(rowData);
                    });
                    return r.slice(0, 20);
                }''')
                results[name] = data
                print(f'  条目数: {len(data)}')
                for row in data[:8]:
                    print(f'  {" | ".join(row[:4])}')
                # 截图
                safe_name = name.replace('/', '_')
                await page.screenshot(path=str(OUT_DIR / f'{safe_name}.png'))
            except Exception as e:
                print(f'  FAIL: {e}')
                results[name] = []
        
        await browser.close()
        
        # ===== 汇总 =====
        print(f'\n{"="*50}')
        print(f'[{now()}] === 探查汇总 ===')
        for name, data in results.items():
            status = f'{len(data)} 条' if data else '空/失败'
            print(f'  {name}: {status}')
        
        return results

asyncio.run(explore())
print('\n探查完成! 截图保存在 automation/output/')
