#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过UI点击导航+添加内容"""
import asyncio, sys
from datetime import datetime
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

ANNOUNCEMENTS = [
    {"title": "草原人宠互动季正式启动！", "sort": "1",
     "content": "牛香香草原人宠互动季第一季开放报名！\n时间：2026年7月 地点：内蒙古锡林郭勒多伦县\n规模：60-100组（1人+1狗） 费用：1980元/组（早鸟价1780元）\n四大比赛项目：意志力挑战赛、叼物接力赛、趣味障碍赛、才艺大比拼\n费用包含：蒙古包3天2晚、全部餐饮（含烤全羊）、8000元奖金池、专业摄影师跟拍、牛肝干伴手礼\n咨询电话：13145294218 王经理"},
    {"title": "牛香香牛肝干正式上线！配料表只有新鲜牛肝", "sort": "2",
     "content": "牛香香牛肝干正式上线！人食标准做宠物零食。\n为什么选牛肝？高蛋白29g/100g、富含铁锌维生素A、天然肉香无需诱食剂\n零添加承诺：0防腐剂、0诱食剂、0谷物、0色素\n配料表只有一样：新鲜牛肝\n三种规格：80g袋装¥16、240g盒装¥48、480g礼盒装¥88\n自有工厂 SC10415255102074 内蒙古锡林郭勒"},
    {"title": "招商加盟 寻找城市合伙人", "sort": "3",
     "content": "牛香香正在寻找热爱宠物的城市合伙人！\n我们提供：自有工厂直供、完整品牌故事、一人可操作轻资产模式、赛事IP赋能\n适合人群：宠物店主、宠物博主达人、社群群主团长\n合作模式：一件代发（零库存）、区域代理（独家区域）、品牌联名（定制包装）\n咨询电话：13145294218 王经理 邮箱：niuxiangxiang@163.com"},
]

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
        log(f'登录OK')
        
        # 进入应用
        await page.goto(APP_URL, wait_until='networkidle', timeout=20000)
        await asyncio.sleep(4)
        
        # 点击"更多设置"展开子菜单
        log('展开"更多设置"...')
        try:
            await page.click('text=更多设置', timeout=5000)
            await asyncio.sleep(2)
        except:
            pass
        
        # 点击"公告管理"
        log('点击"公告管理"...')
        await page.click('text=公告管理', timeout=5000)
        await asyncio.sleep(4)
        log(f'URL: {page.url[:150]}')
        
        # 截图看状态
        await page.screenshot(path=str(OUT_DIR / 'announce_list.png'), full_page=True)
        
        # 查找"添加"按钮/链接
        add_info = await page.evaluate('''() => {
            var links = document.querySelectorAll("a");
            var btns = document.querySelectorAll("button");
            var r = {links: [], btns: []};
            links.forEach(function(l) {
                var t = (l.innerText || "").trim();
                if (t) r.links.push({text: t.substring(0, 30), href: (l.href||"").substring(0, 200)});
            });
            btns.forEach(function(b) {
                var t = (b.innerText || b.value || "").trim();
                if (t) r.btns.push({text: t.substring(0, 30)});
            });
            return r;
        }''')
        log(f'链接: {[(l["text"]) for l in add_info["links"][:15]]}')
        log(f'按钮: {add_info["btns"][:10]}')
        
        # 获取页面主要文字
        body_text = await page.evaluate('() => (document.body?.innerText || "").substring(0, 500)')
        log(f'页面文字: {body_text[:300]}')
        
        await browser.close()

asyncio.run(main())
