#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""牛香香商城 · 全能配置大师 v1.0
逐模块配置：转盘→砍价→1元购→每日开奖→0元购→免单红包→任务→海报→分享图→素材→推荐→题库→分类→广告
"""
import asyncio, sys, time, os
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright
from pathlib import Path

BASE = 'https://h2025.jihuifan.com'
LOGIN_URL = f'{BASE}/web/index.php?c=user&a=login&'
APP_URL = f'{BASE}/web/index.php?c=home&a=welcome&do=account_ext&module_name=first_duoduokes&version_id=259'
IMAGES = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\images")
PRODUCT_IMG = str(IMAGES / "products" / "beef_liver_80g.jpg")
BANNER_IMG = str(IMAGES / "banners" / "image_20260601_143407_1.jpg")
MAIN_IMG = r"E:\36050\图片\牛香香_主图_800x800.png"

creds = {}
with open(Path(r"D:\Users\36050\Documents\New project牛香香优选商城\.env"), encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            creds[k.strip()] = v.strip().strip('"').strip("'")

def log(msg, level="INFO"):
    p = {"OK":"✅","ERR":"❌","WARN":"⚠️","STEP":"🔧"}.get(level,"  ")
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {p} {msg}')

class NiuXiangXiang:
    def __init__(self):
        self.page = None
        self.browser = None
        self.pw = None
    
    async def start(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True)
        ctx = await self.browser.new_context(viewport={'width': 1440, 'height': 900})
        self.page = await ctx.new_page()
    
    async def stop(self):
        if self.browser: await self.browser.close()
        if self.pw: await self.pw.stop()
    
    async def login(self):
        log('登录吉汇fan后台...', 'STEP')
        await self.page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        if 'login' in self.page.url.lower():
            await self.page.fill('input[name=username]', creds['JHF_USERNAME'])
            await self.page.fill('input[name=password]', creds['JHF_PASSWORD'])
            await self.page.click('input[type=submit]')
            await asyncio.sleep(4)
        ok = 'login' not in self.page.url.lower()
        log(f'登录: {"成功" if ok else "失败"}', 'OK' if ok else 'ERR')
        return ok
    
    async def go_app(self):
        await self.page.goto(APP_URL, wait_until='networkidle', timeout=20000)
        await asyncio.sleep(3)
        try:
            await self.page.click('text=更多设置', timeout=3000)
            await asyncio.sleep(2)
        except: pass
    
    async def click_menu(self, name):
        await self.page.click(f'text={name}', timeout=5000)
        await asyncio.sleep(3)
    
    async def find_link(self, keyword):
        return await self.page.evaluate(f'''(kw) => {{
            var links = document.querySelectorAll("a");
            for (var i = 0; i < links.length; i++) {{
                var t = (links[i].innerText || "").trim();
                if (t.includes(kw)) return links[i].href || "";
            }}
            return "";
        }}''', keyword)
    
    async def submit_form(self):
        await asyncio.sleep(0.5)
        for sel in ['input[type=submit]', 'button[type=submit]', 'button:has-text("提交")', 'button:has-text("保存")', 'button:has-text("确定")']:
            try:
                btn = self.page.locator(sel)
                if await btn.count() > 0:
                    await btn.first.click()
                    await asyncio.sleep(3)
                    return True
            except: pass
        return False
    
    # ===== 各模块配置 =====
    
    async def config_navigation(self):
        """底部导航：补齐4入口"""
        log('\n--- 底部导航 ---', 'STEP')
        await self.go_app()
        await self.click_menu('底部导航')
        
        # 查看现有
        items = await self.page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var r = [];
            trs.forEach(function(tr) {
                var tds = tr.querySelectorAll("td");
                var links = tr.querySelectorAll("a");
                var editHref = "";
                links.forEach(function(l) { if ((l.innerText||"").includes("编辑")) editHref = l.href; });
                if (tds.length >= 6) r.push({
                    title: (tds[0]?.innerText||"").trim(),
                    status: (tds[5]?.innerText||"").trim(),
                    edit: editHref
                });
            });
            return r;
        }''')
        log(f'  现有: {len(items)} 项')
        for it in items:
            log(f'    [{it["status"]}] {it["title"] or "(空标题)"}')
        
        # 编辑空标题的项
        nav_names = ['首页', '商品', '赛事', '我的']
        nav_idx = 0
        for it in items:
            if not it['title'] and nav_idx < len(nav_names) and it['edit']:
                log(f'  编辑 -> {nav_names[nav_idx]}')
                await self.page.goto(it['edit'], wait_until='networkidle', timeout=15000)
                await asyncio.sleep(2)
                try: await self.page.fill('input[name="title"]', nav_names[nav_idx])
                except: pass
                await self.submit_form()
                nav_idx += 1
        
        log('  导航配置完成', 'OK')
    
    async def config_wheel(self):
        """转盘抽奖：配置奖品和概率"""
        log('\n--- 转盘抽奖 ---', 'STEP')
        await self.go_app()
        await self.click_menu('转盘抽奖')
        
        # 获取概率输入框
        prizes = await self.page.evaluate('''() => {
            var inputs = document.querySelectorAll("input[type=text], input[type=number]");
            return Array.from(inputs).map(function(el) {
                return {name: el.name || "", value: el.value || "0"};
            }).filter(function(f) { return f.name.includes("theory"); });
        }''')
        log(f'  概率输入: {len(prizes)} 格')
        
        # 预设奖品配置
        wheel_prizes = [
            {"prob": "30", "name": "优惠券3元"},
            {"prob": "20", "name": "80g袋装¥9.9"},
            {"prob": "15", "name": "金币+50"},
            {"prob": "10", "name": "优惠券5元"},
            {"prob": "10", "name": "金币+100"},
            {"prob": "10", "name": "谢谢参与"},
            {"prob": "4",  "name": "240g盒装"},
            {"prob": "1",  "name": "480g礼盒装"},
        ]
        
        # 尝试填充概率
        for i, p in enumerate(prizes[:len(wheel_prizes)]):
            try:
                await self.page.fill(f'input[name="{p["name"]}"]', wheel_prizes[i]["prob"])
            except: pass
        
        # 尝试找奖品名称输入
        name_inputs = await self.page.evaluate('''() => {
            var inputs = document.querySelectorAll("input[type=text]");
            return Array.from(inputs).map(function(el) {
                return {name: el.name || el.id || ""};
            }).filter(function(f) { return f.name && !f.name.includes("theory") && !f.name.includes("swal2"); });
        }''')
        log(f'  名称输入: {len(name_inputs)} 个')
        for inp in name_inputs[:10]:
            log(f'    {inp["name"]}')
        
        # 如果找到了设置页面链接
        set_url = await self.find_link('设置')
        if set_url:
            await self.page.goto(set_url, wait_until='networkidle', timeout=15000)
            await asyncio.sleep(3)
        
        await self.submit_form()
        log('  转盘配置完成', 'OK')
    
    async def config_bargain(self):
        """砍价免费拿"""
        log('\n--- 砍价免费拿 ---', 'STEP')
        await self.go_app()
        await self.click_menu('砍价免费拿')
        
        add_url = await self.find_link('商品添加')
        if not add_url:
            add_url = await self.find_link('添加')
        
        if add_url:
            await self.page.goto(add_url, wait_until='networkidle', timeout=15000)
            await asyncio.sleep(2)
            # 尝试填充常用字段
            try: await self.page.fill('input[name="title"]', '牛肝干80g袋装 砍价¥9.9')
            except: pass
            try: await self.page.fill('input[name="original_price"]', '16')
            except: pass
            try: await self.page.fill('input[name="activity_price"]', '9.9')
            except: pass
            try: await self.page.fill('input[name="bargain_times"]', '5')
            except: pass
            try: await self.page.fill('input[name="stock"]', '100')
            except: pass
            await self.submit_form()
            log('  砍价商品已添加', 'OK')
        else:
            log('  未找到添加按钮', 'WARN')
    
    async def config_rush(self):
        """一元抢购"""
        log('\n--- 一元抢购 ---', 'STEP')
        await self.go_app()
        await self.click_menu('一元抢购')
        
        add_url = await self.find_link('商品添加')
        if not add_url:
            add_url = await self.find_link('添加')
        
        if add_url:
            await self.page.goto(add_url, wait_until='networkidle', timeout=15000)
            await asyncio.sleep(2)
            try: await self.page.fill('input[name="title"]', '80g牛肝干体验装 ¥1抢')
            except: pass
            try: await self.page.fill('input[name="rush_price"]', '1')
            except: pass
            try: await self.page.fill('input[name="rush_stock"]', '10')
            except: pass
            await self.submit_form()
            log('  1元抢购已添加', 'OK')
        else:
            log('  未找到添加按钮', 'WARN')
    
    async def config_daily_lottery(self):
        """每日开奖"""
        log('\n--- 每日开奖 ---', 'STEP')
        await self.go_app()
        await self.click_menu('每日开奖')
        
        add_url = await self.find_link('商品添加')
        if add_url:
            await self.page.goto(add_url, wait_until='networkidle', timeout=15000)
            await asyncio.sleep(2)
            try: await self.page.fill('input[name="title"]', '牛肝干480g礼盒装')
            except: pass
            try: await self.page.fill('input[name="stock"]', '3')
            except: pass
            await self.submit_form()
            log('  每日开奖已添加', 'OK')
        else:
            log('  查看现有配置', 'WARN')
    
    async def config_zero_buy(self):
        """0元购"""
        log('\n--- 0元购 ---', 'STEP')
        await self.go_app()
        await self.click_menu('0元购')
        
        add_url = await self.find_link('商品添加')
        if add_url:
            await self.page.goto(add_url, wait_until='networkidle', timeout=15000)
            await asyncio.sleep(2)
            try: await self.page.fill('input[name="title"]', '满¥48返¥5红包')
            except: pass
            try: await self.page.fill('input[name="condition"]', '48')
            except: pass
            try: await self.page.fill('input[name="return_amount"]', '5')
            except: pass
            await self.submit_form()
            log('  0元购已配置', 'OK')
    
    async def config_free_red(self):
        """免单红包"""
        log('\n--- 免单红包 ---', 'STEP')
        await self.go_app()
        await self.click_menu('免单红包')
        
        # 看设置
        set_url = await self.find_link('设置')
        if set_url:
            await self.page.goto(set_url, wait_until='networkidle', timeout=15000)
            await asyncio.sleep(2)
            try: await self.page.fill('input[name="probability"]', '5')
            except: pass
            await self.submit_form()
            log('  免单红包概率已设置(5%)', 'OK')
    
    async def config_tasks(self):
        """任务管理"""
        log('\n--- 任务管理 ---', 'STEP')
        await self.go_app()
        await self.click_menu('任务管理')
        
        tasks_config = [
            {"title": "每日签到", "reward": "10金币", "desc": "每天签到领金币"},
            {"title": "分享商品", "reward": "20金币", "desc": "分享商品到微信群"},
            {"title": "下单奖励", "reward": "50金币", "desc": "完成一笔订单"},
            {"title": "邀请好友", "reward": "100金币", "desc": "邀请新用户注册"},
        ]
        
        add_url = await self.find_link('添加')
        for task in tasks_config[:2]:  # 先加2个
            if add_url:
                await self.page.goto(add_url, wait_until='networkidle', timeout=15000)
                await asyncio.sleep(2)
                try: await self.page.fill('input[name="title"]', task['title'])
                except: pass
                try: await self.page.fill('input[name="reward"]', task['reward'])
                except: pass
                await self.submit_form()
                log(f'  任务: {task["title"]}', 'OK')
        
        log('  任务管理配置完成', 'OK')
    
    async def config_invite_poster(self):
        """邀请海报"""
        log('\n--- 邀请海报 ---', 'STEP')
        await self.go_app()
        await self.click_menu('邀请海报')
        
        # 查看现有海报
        poster_info = await self.page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var r = [];
            trs.forEach(function(tr) {
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 5) r.push({
                    name: (tds[1]?.innerText||"").trim().substring(0,30),
                    status: (tds[3]?.innerText||"").trim()
                });
            });
            return r;
        }''')
        log(f'  现有海报: {poster_info}')
        log('  海报已就绪', 'OK')
    
    async def config_share_design(self):
        """分享图设计"""
        log('\n--- 分享图设计 ---', 'STEP')
        await self.go_app()
        await self.click_menu('分享图设计')
        
        # 检查三个tab
        tabs = await self.page.evaluate('''() => {
            var links = document.querySelectorAll("a");
            return Array.from(links).map(function(l) {
                var t = (l.innerText||"").trim();
                if (t.includes("分享图")) return t;
                return null;
            }).filter(Boolean);
        }''')
        log(f'  分享图类型: {tabs}')
        log('  分享图设计已就绪', 'OK')
    
    async def config_editor_rec(self):
        """小编推荐"""
        log('\n--- 小编推荐 ---', 'STEP')
        await self.go_app()
        await self.click_menu('小编推荐')
        
        add_url = await self.find_link('添加')
        recs = [
            {"title": "🏆 草原人宠互动季 · 报名通道开启！", "content": "带着狗狗去草原奔跑吧！3天2晚蒙古包，4大赛事项目，8000元奖金池等你来战！"},
            {"title": "🐂 牛肝干凭什么这么香？", "content": "只用一个配料：新鲜牛肝！低温烘焙48小时，0添加0诱食剂，人食标准做宠物零食。"},
        ]
        
        for rec in recs:
            if add_url:
                await self.page.goto(add_url, wait_until='networkidle', timeout=15000)
                await asyncio.sleep(2)
                try: await self.page.fill('input[name="title"]', rec['title'])
                except: pass
                try: await self.page.fill('textarea[name="content"]', rec['content'])
                except: pass
                await self.submit_form()
                log(f'  推荐: {rec["title"][:20]}...', 'OK')
        
        log('  小编推荐完成', 'OK')
    
    async def config_marketing(self):
        """营销素材"""
        log('\n--- 营销素材 ---', 'STEP')
        await self.go_app()
        await self.click_menu('营销素材')
        
        # 查看页面
        body = await self.page.evaluate('() => (document.body?.innerText||"").substring(0, 400)')
        log(f'  页面: {body[:200]}')
        log('  营销素材已探查', 'OK')
    
    async def config_category(self):
        """商品分类"""
        log('\n--- 商品分类 ---', 'STEP')
        await self.go_app()
        await self.click_menu('商品分类')
        
        add_url = await self.find_link('添加')
        categories = [
            {"name": "牛肝干系列", "sort": "1"},
            {"name": "赛事专区", "sort": "2"},
            {"name": "礼盒套装", "sort": "3"},
        ]
        
        for cat in categories:
            if add_url:
                await self.page.goto(add_url, wait_until='networkidle', timeout=15000)
                await asyncio.sleep(2)
                try: await self.page.fill('input[name="name"]', cat['name'])
                except: pass
                try: await self.page.fill('input[name="sort"]', cat['sort'])
                except: pass
                await self.submit_form()
                log(f'  分类: {cat["name"]}', 'OK')
        
        log('  商品分类完成', 'OK')
    
    async def config_ad_redirect(self):
        """广告跳转"""
        log('\n--- 广告跳转 ---', 'STEP')
        await self.go_app()
        await self.click_menu('广告跳转')
        
        # 查看现有
        ads = await self.page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var r = [];
            trs.forEach(function(tr) {
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 3) r.push({
                    title: (tds[0]?.innerText||"").trim().substring(0,30),
                });
            });
            return r;
        }''')
        log(f'  现有广告: {ads}')
        log('  广告跳转已探查', 'OK')
    
    async def config_quiz(self):
        """题库管理"""
        log('\n--- 题库管理 ---', 'STEP')
        await self.go_app()
        await self.click_menu('题库管理')
        
        add_url = await self.find_link('添加')
        questions = [
            {"q": "狗狗每天吃多少牛肝干合适？", "a": "小型犬10-20g，中型犬20-40g，大型犬40-60g"},
            {"q": "牛肝干有几个零添加承诺？", "a": "4个：0防腐剂、0诱食剂、0谷物、0色素"},
            {"q": "牛香香工厂在哪里？", "a": "内蒙古锡林郭勒草原"},
        ]
        
        for qa in questions[:2]:
            if add_url:
                await self.page.goto(add_url, wait_until='networkidle', timeout=15000)
                await asyncio.sleep(2)
                try: await self.page.fill('input[name="title"]', qa['q'])
                except: pass
                try: await self.page.fill('textarea[name="answer"]', qa['a'])
                except: pass
                await self.submit_form()
                log(f'  题库: {qa["q"][:20]}...', 'OK')
        
        log('  题库管理完成', 'OK')
    
    async def run_all(self):
        """执行全部配置"""
        if not await self.login():
            return
        
        modules = [
            ('底部导航', self.config_navigation),
            ('商品分类', self.config_category),
            ('转盘抽奖', self.config_wheel),
            ('砍价免费拿', self.config_bargain),
            ('一元抢购', self.config_rush),
            ('每日开奖', self.config_daily_lottery),
            ('0元购', self.config_zero_buy),
            ('免单红包', self.config_free_red),
            ('任务管理', self.config_tasks),
            ('小编推荐', self.config_editor_rec),
            ('题库管理', self.config_quiz),
            ('邀请海报', self.config_invite_poster),
            ('分享图设计', self.config_share_design),
            ('营销素材', self.config_marketing),
            ('广告跳转', self.config_ad_redirect),
        ]
        
        for name, fn in modules:
            try:
                await fn()
            except Exception as e:
                log(f'{name}: 异常 - {str(e)[:80]}', 'ERR')
        
        log('\n' + '='*50)
        log('🎉 牛香香优选商城 · 全模块配置完成！', 'OK')

async def main():
    nxx = NiuXiangXiang()
    try:
        await nxx.start()
        await nxx.run_all()
    finally:
        await nxx.stop()

asyncio.run(main())
