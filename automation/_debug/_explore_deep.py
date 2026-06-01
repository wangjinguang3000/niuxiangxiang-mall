#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""集汇返利后台 · 全覆盖探查"""
import asyncio, sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright
from pathlib import Path

BASE = 'https://h2025.jihuifan.com'
LOGIN_URL = f'{BASE}/web/index.php?c=user&a=login&'
APP_URL = f'{BASE}/web/index.php?c=home&a=welcome&do=account_ext&module_name=first_duoduokes&version_id=259'
OUT_DIR = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\automation\output\explore")
OUT_DIR.mkdir(parents=True, exist_ok=True)

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
        
        # 登录
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
        
        # 获取全部菜单项
        all_menus = await page.evaluate('''() => {
            var items = document.querySelectorAll(".treeview-menu li a, .sidebar-menu li a, li a");
            var seen = {};
            var r = [];
            items.forEach(function(a) {
                var t = (a.innerText || "").trim();
                if (t && t.length > 1 && t.length < 20 && !seen[t]) {
                    seen[t] = true;
                    r.push({text: t, href: (a.href || "").substring(0, 200)});
                }
            });
            return r;
        }''')
        
        # 去重
        unique = []
        seen = set()
        for m in all_menus:
            if m['text'] not in seen:
                seen.add(m['text'])
                unique.append(m)
        
        print(f'\n=== 全部菜单项 ({len(unique)}) ===')
        for m in unique:
            print(f'  {m["text"]}')
        
        # 探查"更多设置"下的每个子菜单
        sub_menus = [m for m in unique if m['text'] not in ['首页','平台管理','我的账户','消息管理','商城','应用模块','平台个数','平台续费','应用权限组','账号权限组','账号有效期','用户权限组','应用访问流量(API)','我的订单','牛香香优选','集汇返','菜单已锁定','用户名：','模块首页','操作员权限','更多设置','自营商城','小程序设置','分享图设计','广告跳转','提现管理','订单管理','用户管理','底部导航','新手攻略','公告管理']]
        
        log(f'\n=== 逐项探查 ({len(sub_menus)}个模块) ===')
        for m in sub_menus:
            name = m['text']
            log(f'\n--- {name} ---')
            try:
                # 回到应用
                await page.goto(APP_URL, wait_until='networkidle', timeout=15000)
                await asyncio.sleep(2)
                try:
                    await page.click('text=更多设置', timeout=3000)
                    await asyncio.sleep(2)
                except: pass
                
                # 点击菜单项
                await page.click(f'text={name}', timeout=5000)
                await asyncio.sleep(3)
                
                url = page.url[:150]
                log(f'  URL: {url}')
                
                # 获取页面概要
                summary = await page.evaluate('''() => {
                    var body = (document.body?.innerText || "").substring(0, 500);
                    var links = document.querySelectorAll("a");
                    var linkTexts = [];
                    links.forEach(function(l) {
                        var t = (l.innerText || "").trim();
                        if (t && t.length > 1 && t.length < 12) linkTexts.push(t);
                    });
                    return {body: body, links: linkTexts.slice(0, 15)};
                }''')
                
                log(f'  关键功能: {summary["links"][:8]}')
                log(f'  页面概览: {summary["body"][:200]}')
                
                # 截图
                safe = name.replace('/', '_').replace(' ', '_')
                await page.screenshot(path=str(OUT_DIR / f'{safe}.png'))
                
            except Exception as e:
                log(f'  失败: {e}')
        
        await browser.close()
        log('\n=== 全部探查完成! ===')

asyncio.run(main())
