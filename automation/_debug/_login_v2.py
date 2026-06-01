#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""牛香香商城 · 智能登录脚本 v2"""
import asyncio, sys, time
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

async def try_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await ctx.new_page()
        
        page.on('console', lambda msg: print(f'  [CONSOLE {msg.type}] {msg.text}') if msg.type in ('error',) else None)
        
        print('>>> 访问登录页面...')
        resp = await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
        print(f'  状态码: {resp.status}')
        print(f'  当前URL: {page.url[:100]}')
        await asyncio.sleep(2)
        
        # 获取token
        token = await page.evaluate('() => { var el = document.querySelector("input[name=token]"); return el ? el.value : ""; }')
        print(f'  CSRF Token: {token[:40] if token else "(无)"}...')
        
        # 探查submit按钮
        btn_info = await page.evaluate('''() => {
            var btns = document.querySelectorAll("button[type=submit], input[type=submit]");
            var r = [];
            btns.forEach(function(b) {
                r.push({
                    tag: b.tagName,
                    text: (b.innerText || b.value || "").substring(0,30),
                    id: b.id,
                    className: (b.className || "").substring(0,40)
                });
            });
            return r;
        }''')
        print(f'  Submit元素: {btn_info}')
        
        # 填入账号密码
        print(f'>>> 填入账号: {USERNAME}')
        await page.fill('input[name=username]', USERNAME)
        await page.fill('input[name=password]', PASSWORD)
        await asyncio.sleep(0.5)
        
        # 方式1: 点击 button[type=submit]
        print('>>> 方式1: 点击 button[type=submit]...')
        try:
            await page.click('button[type=submit]', timeout=5000)
            await asyncio.sleep(4)
            print(f'  当前URL: {page.url[:120]}')
            if 'login' not in page.url.lower():
                print('  [OK] 登录成功! (button submit)')
                await browser.close()
                return True
        except Exception as e:
            print(f'  button submit失败: {e}')
        
        # 检查页面内容
        body_text = await page.evaluate('() => document.body.innerText.substring(0, 500)')
        print(f'  页面提示: {body_text[:300]}')
        
        # 方式2: 重新加载，尝试 input[type=submit]
        await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        await page.fill('input[name=username]', USERNAME)
        await page.fill('input[name=password]', PASSWORD)
        print('>>> 方式2: 点击 input[type=submit]...')
        try:
            await page.click('input[type=submit]', timeout=5000)
            await asyncio.sleep(4)
            print(f'  当前URL: {page.url[:120]}')
            if 'login' not in page.url.lower():
                print('  [OK] 登录成功! (input submit)')
                await browser.close()
                return True
        except Exception as e:
            print(f'  input submit失败: {e}')
        
        body_text = await page.evaluate('() => document.body.innerText.substring(0, 500)')
        print(f'  页面提示: {body_text[:300]}')
        
        # 方式3: 按Enter
        await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        await page.fill('input[name=username]', USERNAME)
        await page.fill('input[name=password]', PASSWORD)
        print('>>> 方式3: 按Enter键...')
        await page.press('input[name=password]', 'Enter')
        await asyncio.sleep(4)
        print(f'  当前URL: {page.url[:120]}')
        if 'login' not in page.url.lower():
            print('  [OK] 登录成功! (Enter)')
            await browser.close()
            return True
        
        body_text = await page.evaluate('() => document.body.innerText.substring(0, 500)')
        print(f'  页面提示: {body_text[:300]}')
        
        # 最终截图
        out_dir = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\automation\output")
        out_dir.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(out_dir / 'login_final.png'))
        print(f'  截图: {out_dir / "login_final.png"}')
        
        await browser.close()
        return False

result = asyncio.run(try_login())
print(f'\n=== 最终结果: {"成功!" if result else "失败 - 需确认密码或尝试其他方式"} ===')
