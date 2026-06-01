#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过侧边栏点击导航+添加内容"""
import asyncio, sys, time
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
        
        # 第一步：点击"更多设置"展开子菜单
        print('\n>>> 点击"更多设置"...')
        try:
            await page.click('text=更多设置', timeout=5000)
            await asyncio.sleep(2)
            print('  已点击')
        except Exception as e:
            print(f'  失败: {e}')
        
        # 截图看看展开后的菜单
        await page.screenshot(path=str(OUT_DIR / 'menu_expanded.png'), full_page=True)
        
        # 获取展开后的所有菜单文字
        menu_text = await page.evaluate('''() => {
            var items = document.querySelectorAll(".menu-item, .nav-item, li a, .treeview-menu li a, .sidebar-menu li a");
            return Array.from(items).map(function(el) {
                return (el.innerText || "").trim().substring(0, 40);
            }).filter(function(t) { return t && t.length > 1 && t.length < 30; });
        }''')
        print(f'\n菜单项 ({len(menu_text)}):')
        for t in menu_text[:40]:
            print(f'  - {t}')
        
        # 尝试点击"公告管理"
        print('\n>>> 尝试点击子菜单项...')
        targets = ['公告管理', '新手攻略', '置顶跳转', '底部导航', '首页轮播', '分销管理']
        for target in targets:
            try:
                # 先回应用首页
                await page.goto(APP_URL, wait_until='networkidle', timeout=20000)
                await asyncio.sleep(3)
                # 展开更多设置
                try:
                    await page.click('text=更多设置', timeout=3000)
                    await asyncio.sleep(2)
                except:
                    pass
                
                # 点击目标
                el = page.locator(f'text={target}')
                count = await el.count()
                print(f'  {target}: 找到{count}个匹配')
                if count > 0:
                    await el.first.click()
                    await asyncio.sleep(3)
                    print(f'    点击后URL: {page.url[:120]}')
                    await page.screenshot(path=str(OUT_DIR / f'nav_{target}.png'), full_page=True)
            except Exception as e:
                print(f'  {target}: 失败 - {e}')
        
        await browser.close()

asyncio.run(main())
