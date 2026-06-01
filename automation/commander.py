#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""牛香香优选商城 · 后端自动化总指挥 v2.1"""

import asyncio, json, os, sys, time
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.async_api import async_playwright

# ===== 配置 =====

from env_loader import JHF_USERNAME as USERNAME, JHF_PASSWORD as PASSWORD, JHF_BASE_URL as BASE_URL, JHF_LOGIN_URL as LOGIN_URL


OUTPUT_DIR = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\automation\output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PRODUCTS = [
    {"title": "牛肝干 80g 袋装", "price": "16.00", "stock": "999", "ori_price": "19.90",
     "desc": "锡林郭勒草原新鲜牛肝,低温烘焙,0添加\n配料表只有一样:新鲜牛肝\n规格:80g/袋\nSC10415255102074", "commission": "10", "sort": "1"},
    {"title": "牛肝干 240g 盒装(3袋)", "price": "48.00", "stock": "999", "ori_price": "58.00",
     "desc": "锡林郭勒草原新鲜牛肝,低温烘焙,0添加\n配料表只有一样:新鲜牛肝\n规格:240g/盒(80gx3袋)\nSC10415255102074", "commission": "10", "sort": "2"},
    {"title": "牛肝干 480g 礼盒装", "price": "88.00", "stock": "500", "ori_price": "108.00",
     "desc": "锡林郭勒草原新鲜牛肝,低温烘焙,0添加\n配料表只有一样:新鲜牛肝\n规格:480g/礼盒(80gx6袋)\n附赠品牌围巾\nSC10415255102074", "commission": "12", "sort": "3"},
]

BANNERS = [
    {"title": "草原人宠互动季 第一季", "sort": "10"},
    {"title": "牛香香牛肝干 0添加宠物零食", "sort": "9"},
    {"title": "报名参赛 早鸟价1780", "sort": "8"},
    {"title": "招商加盟 一起搞宠物事业", "sort": "7"},
]

ANNOUNCEMENTS = [
    {"title": "草原人宠互动季正式启动!", "sort": "1"},
    {"title": "牛香香牛肝干正式上线!配料表只有新鲜牛肝", "sort": "2"},
    {"title": "招商加盟 寻找城市合伙人", "sort": "3"},
]

GUIDES = [
    {"title": "参赛指南 草原人宠互动季全攻略", "sort": "1"},
    {"title": "喂养指南 牛肝干的正确喂法", "sort": "2"},
    {"title": "加盟指南 如何成为牛香香城市合伙人", "sort": "3"},
    {"title": "创业日记 一个人搞一个品牌的故事", "sort": "4"},
]


class Commander:
    def __init__(self, headless=True):
        self.headless = headless
        self.page = None
        self.browser = None
        self.playwright = None

    def log(self, msg, level="INFO"):
        prefix = {"INFO": "  ", "OK": "[OK]", "ERR": "[ERR]", "STEP": ">>>", "WARN": "[WARN]"}
        print(f"{prefix.get(level, '')} [{datetime.now().strftime('%H:%M:%S')}] {msg}")

    async def start(self):
        self.log("启动浏览器...", "STEP")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        ctx = await self.browser.new_context(viewport={"width": 1440, "height": 900})
        self.page = await ctx.new_page()

    async def stop(self):
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()

    async def login(self):
        self.log("登录后台...", "STEP")
        await self.page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        if "login" not in self.page.url:
            self.log("已有登录状态", "OK"); return True
        await self.page.fill("input[name=username]", USERNAME)
        await self.page.fill("input[name=password]", PASSWORD)
        await self.page.click("input[type=submit]")
        await asyncio.sleep(3)
        ok = "login" not in self.page.url
        self.log("登录成功" if ok else "登录失败", "OK" if ok else "ERR")
        return ok

    async def screenshot(self, name):
        p = str(OUTPUT_DIR / f"{name}.png")
        await self.page.screenshot(path=p, full_page=True)

    async def explore_page(self, label=""):
        info = await self.page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a')).filter(a => a.href && a.innerText?.trim()).map(a => ({
                text: a.innerText.trim().substring(0,40),
                href: a.href.substring(0,200)
            }));
            const inputs = Array.from(document.querySelectorAll('input,select,textarea')).map(el => ({
                tag: el.tagName, type: el.type, name: el.name,
                placeholder: (el.placeholder||'').substring(0,40)
            }));
            const text = document.body.innerText.substring(0, 2000);
            return {links, inputs, text, url: window.location.href};
        }""")
        if label: self.log(f"=== 页面探查: {label} ===", "STEP")
        self.log(f"URL: {info['url']}")
        self.log(f"链接: {len(info['links'])} 个, 表单字段: {len(info['inputs'])} 个")
        for l in info['links'][:12]:
            self.log(f"  [{l['text']}]")
        return info

    async def navigate_store(self):
        app_url = f"{BASE_URL}/web/index.php?c=home&a=welcome&do=account_ext&module_name=first_duoduokes&version_id=259"
        await self.page.goto(app_url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

    async def click_text(self, text):
        try:
            await self.page.click(f"text={text}", timeout=5000)
            await asyncio.sleep(2)
            return True
        except:
            return False

    async def run_full_mission(self):
        missions = [
            ("自营商城首页", self.mission_store),
            ("商品管理", self.mission_products),
            ("首页轮播", self.mission_banners),
            ("公告管理", self.mission_announcements),
            ("新手攻略", self.mission_guides),
            ("置顶跳转", self.mission_toplinks),
            ("底部导航", self.mission_nav),
        ]
        for name, fn in missions:
            self.log(f"\n{'='*40}", "STEP")
            self.log(f"探查: {name}", "STEP")
            try:
                await fn()
                self.log(f"{name} - 完成", "OK")
            except Exception as e:
                self.log(f"{name} - 失败: {e}", "ERR")
                await self.screenshot(f"err_{name}")

    async def mission_store(self):
        await self.navigate_store()
        await self.explore_page("自营商城")

    async def mission_products(self):
        await self.navigate_store()
        if await self.click_text("自营商城"):
            await self.explore_page("商品管理")
            await self.screenshot("products")

    async def mission_banners(self):
        await self.navigate_store()
        url = f"{BASE_URL}/web/index.php?c=site&a=entry&do=slide&module_name=first_duoduokes&direct=1"
        await self.page.goto(url, wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        await self.explore_page("首页轮播")
        await self.screenshot("banners")

    async def mission_announcements(self):
        await self.navigate_store()
        url = f"{BASE_URL}/web/index.php?c=site&a=entry&do=notice&module_name=first_duoduokes&direct=1"
        await self.page.goto(url, wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        await self.explore_page("公告管理")
        await self.screenshot("announcements")

    async def mission_guides(self):
        await self.navigate_store()
        url = f"{BASE_URL}/web/index.php?c=site&a=entry&do=article&module_name=first_duoduokes&direct=1"
        await self.page.goto(url, wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        await self.explore_page("新手攻略")
        await self.screenshot("guides")

    async def mission_toplinks(self):
        await self.navigate_store()
        url = f"{BASE_URL}/web/index.php?c=site&a=entry&do=topnav&module_name=first_duoduokes&direct=1"
        await self.page.goto(url, wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        await self.explore_page("置顶跳转")
        await self.screenshot("toplinks")

    async def mission_nav(self):
        await self.navigate_store()
        url = f"{BASE_URL}/web/index.php?c=site&a=entry&do=bottomnav&module_name=first_duoduokes&direct=1"
        await self.page.goto(url, wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        await self.explore_page("底部导航")
        await self.screenshot("navigation")


async def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--visible", action="store_true", help="显示浏览器窗口")
    args = p.parse_args()

    c = Commander(headless=not args.visible)
    try:
        await c.start()
        if not await c.login():
            print("\n登录失败，请检查网络或账号密码")
            return
        await c.run_full_mission()
        print(f"\n全部探查完成! 截图: {OUTPUT_DIR}")
    finally:
        await c.stop()

if __name__ == "__main__":
    asyncio.run(main())
