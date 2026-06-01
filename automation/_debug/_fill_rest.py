#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""填充所有剩余模块"""
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

GUIDES = [
    {"title": "参赛指南 · 草原人宠互动季全攻略",
     "content": "【赛前准备】1.确认报名信息（1人+1狗）2.赛前7天建微信群 3.携带狗狗健康证疫苗本 4.备好狗狗日用品粮水碗牵引绳\n\n【交通方式】自驾北京出发4-5小时G95高速 / 大巴到多伦县城接站 / 火车到张家口站接驳车\n\n【住宿安排】蒙古包2人一包或家庭包、独立卫浴优先、带外套草原晚上凉\n\n【比赛规则】意志力赛面对牛排坐住不动最久胜 / 叼物接力最快叼回胜 / 障碍赛最快完赛胜 / 才艺赛观众投票\n\n【常见问题】Q:狗狗需要参赛经验吗？A:不用！这是趣味赛不是专业赛。Q:大小犬都能参加？A:所有犬种欢迎！Q:能带2只狗吗？A:可以！加300元含围巾+保险+拍照"},
    {"title": "喂养指南 · 牛肝干的正确喂法",
     "content": "【推荐喂食量】小型犬<10kg每天10-20g / 中型犬10-25kg每天20-40g / 大型犬>25kg每天40-60g\n\n【喂食技巧】作为高价值训练奖励 / 掰碎拌粮提升食欲 / 温水泡软给老年犬 / 遛狗随身携带\n\n【注意事项】肝脏零食虽好不要过量 / 控制在每日食量10%以内 / 6个月以下幼犬少量喂 / 开封后密封避免受潮\n\n【为什么狗狗爱吃？】牛肝含天然肉香物质，低温烘焙锁住天然风味，不用加诱食剂就超香\n\n【省钱Tips】480g礼盒装单价最低0.18元/g / 赛事期间有限时优惠 / 推荐好友互得奖励"},
    {"title": "加盟指南 · 如何成为牛香香城市合伙人",
     "content": "【模式一：一件代发】零库存我们发货 / 利润零售价20-30% / 适合宠物博主团长个人创业者\n\n【模式二：区域代理】独家区域每城1-3代理 / 利润35-45% / 首批3000元起 / 适合宠物店线下渠道\n\n【模式三：品牌联名】定制包装你的品牌 / 起订量1000盒 / 适合宠物品牌MCN机构\n\n【我们提供】自有工厂品质保障 / 全套营销素材图+视频 / 赛事IP赋能 / 售后保障质量问题包退 / 定期培训\n\n【流程】提交申请→电话沟通→签署协议→正式开始！咨询13145294218王经理"},
    {"title": "创业日记 · 一个人搞一个品牌的故事",
     "content": "Day 1 - 为什么选牛肝？我养了只狗每次买零食都看配料表全是淀粉和添加剂。为什么不能用人食标准做宠物零食？于是决定从内蒙古草原新鲜牛肝开始\n\nDay 30 - 找工厂：跑了锡林郭勒三个旗县终于找到愿意小批量代工的工厂。老板说人食车间做宠物零食你认真的？我说正因为认真才选人食标准\n\nDay 60 - 第一锅试产：低温烘焙48小时打开烤箱整层楼都闻到肉香。第一批样品送给朋友试他们的狗吃完追着袋子跑\n\nDay 90 - 上线准备：产品出来了怎么让人知道？我决定办草原人宠互动季——把爱狗的人聚到大草原上让产品自己说话\n\n做品牌不是砸钱是用心。一个人也能做出好品牌"},
]

def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}')

async def go_app(page):
    await page.goto(APP_URL, wait_until='networkidle', timeout=20000)
    await asyncio.sleep(3)
    try:
        await page.click('text=更多设置', timeout=5000)
        await asyncio.sleep(2)
    except:
        pass

async def click_menu(page, name):
    log(f'  点击"{name}"...')
    await page.click(f'text={name}', timeout=5000)
    await asyncio.sleep(4)

async def get_add_url(page):
    return await page.evaluate('''() => {
        var links = document.querySelectorAll("a");
        for (var i = 0; i < links.length; i++) {
            var t = (links[i].innerText || "").trim();
            if (t.includes("发布") || t.includes("添加") || t.includes("新增")) {
                return links[i].href || "";
            }
        }
        return "";
    }''')

async def fill_and_submit(page, item, module_name):
    await asyncio.sleep(2)
    fields = await page.evaluate('''() => {
        var els = document.querySelectorAll("input:not([type=hidden]):not([type=submit]):not([type=checkbox]):not([type=radio]), textarea, select");
        return Array.from(els).map(function(el) {
            return {name: el.name || el.id || "", tag: el.tagName, type: el.type || ""};
        }).filter(function(f) { return f.name && f.name !== "token"; });
    }''')
    
    log(f'    字段数: {len(fields)}')
    for f in fields[:10]:
        log(f'    [{f["tag"]}] name={f["name"]} type={f["type"]}')
    
    for f in fields:
        name_low = f['name'].lower()
        val = None
        if any(k in name_low for k in ['title', 'name', 'cname', 'subject']):
            val = item.get('title', '')
        elif any(k in name_low for k in ['content', 'desc', 'detail', 'info', 'intro', 'body', 'text', 'article', 'message']):
            val = item.get('content', '')
        elif any(k in name_low for k in ['sort', 'order', 'displayorder', 'rank', 'weight']):
            val = item.get('sort', '1')
        elif any(k in name_low for k in ['link', 'url', 'href']):
            val = item.get('link', item.get('url', ''))
        if val is not None:
            try:
                sel = f'[name="{f["name"]}"]'
                if f['tag'] == 'TEXTAREA':
                    await page.fill(f'textarea{sel}', str(val)[:5000])
                elif f['tag'] == 'SELECT':
                    try: await page.select_option(f'select{sel}', str(val))
                    except: pass
                else:
                    await page.fill(f'input{sel}', str(val)[:300])
            except: pass
    
    await asyncio.sleep(0.5)
    for sel in ['input[type=submit]', 'button[type=submit]', 'button:has-text("提交")', 'button:has-text("保存")', 'button:has-text("发布")']:
        try:
            btn = page.locator(sel)
            if await btn.count() > 0:
                await btn.first.click()
                await asyncio.sleep(3)
                return True
        except: pass
    return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await ctx.new_page()
        
        log('登录...')
        await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        await page.fill('input[name=username]', creds['JHF_USERNAME'])
        await page.fill('input[name=password]', creds['JHF_PASSWORD'])
        await page.click('input[type=submit]')
        await asyncio.sleep(4)
        log('登录OK')
        
        # === 新手攻略 ===
        log('\n=== 新手攻略 ===')
        for idx, item in enumerate(GUIDES):
            log(f'  [{idx+1}/4] {item["title"][:30]}...')
            await go_app(page)
            await click_menu(page, '新手攻略')
            add_url = await get_add_url(page)
            if not add_url:
                log('  找不到添加按钮!')
                continue
            await page.goto(add_url, wait_until='networkidle', timeout=15000)
            ok = await fill_and_submit(page, item, '攻略')
            log(f'  结果: {"OK" if ok else "FAIL"}')
        
        # === 底部导航 ===
        log('\n=== 底部导航 ===')
        await go_app(page)
        await click_menu(page, '底部导航')
        await page.screenshot(path=str(OUT_DIR / 'nav_before.png'))
        
        # 检查现有导航
        nav_data = await page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var r = [];
            trs.forEach(function(tr) {
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 3) {
                    r.push({
                        title: (tds[0]?.innerText || "").trim().substring(0, 20),
                        status: (tds[tds.length-2]?.innerText || "").trim()
                    });
                }
            });
            return r;
        }''')
        log(f'  现有导航: {nav_data}')
        
        # === 首页轮播 check ===
        log('\n=== 首页轮播 ===')
        await go_app(page)
        # Find 首页轮播 in menu - might be under different menu
        # Check if we can find it
        banner_found = await page.evaluate('''() => {
            var items = document.querySelectorAll("li a, .sidebar-menu li a, .treeview-menu li a");
            for (var i = 0; i < items.length; i++) {
                if ((items[i].innerText || "").includes("轮播")) return items[i].innerText.trim();
            }
            return "";
        }''')
        log(f'  菜单中: {banner_found}')
        
        # Check indexSwiper directly
        await page.goto(f'{BASE}/web/index.php?c=site&a=entry&do=indexSwiper&m=first_duoduokes&op=indexSwiper&tab_id=0', wait_until='networkidle', timeout=15000)
        await asyncio.sleep(3)
        banners = await page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var r = [];
            trs.forEach(function(tr) {
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 3) {
                    r.push({
                        title: (tds[0]?.innerText || "").trim().substring(0, 30),
                        status: (tds[tds.length-2]?.innerText || "").trim()
                    });
                }
            });
            return r;
        }''')
        log(f'  现有轮播: {banners}')
        
        # === 置顶跳转 ===
        log('\n=== 置顶跳转 ===')
        topnav_found = await page.evaluate('''() => {
            var items = document.querySelectorAll("li a, .sidebar-menu li a, .treeview-menu li a");
            for (var i = 0; i < items.length; i++) {
                var t = (items[i].innerText || "").trim();
                if (t.includes("置顶") || t.includes("跳转") || t.includes("广告")) return t;
            }
            return "";
        }''')
        log(f'  菜单中: {topnav_found}')
        
        await page.goto(f'{BASE}/web/index.php?c=site&a=entry&do=topnav&m=first_duoduokes&op=topnav&tab_id=0', wait_until='networkidle', timeout=15000)
        await asyncio.sleep(3)
        tops = await page.evaluate('''() => {
            var trs = document.querySelectorAll("table tr");
            var r = [];
            trs.forEach(function(tr) {
                var tds = tr.querySelectorAll("td");
                if (tds.length >= 2) r.push((tds[0]?.innerText || "").trim().substring(0, 30));
            });
            return r;
        }''')
        log(f'  现有置顶: {tops}')
        
        # === 分销管理 ===
        log('\n=== 分销管理 ===')
        await page.goto(f'{BASE}/web/index.php?c=site&a=entry&do=commission&m=first_duoduokes&op=commission&tab_id=0', wait_until='networkidle', timeout=15000)
        await asyncio.sleep(3)
        comm = await page.evaluate('''() => {
            return (document.body?.innerText || "").substring(0, 300);
        }''')
        log(f'  分销页面: {comm[:200]}')
        
        await browser.close()
        log('\n全部完成!')

asyncio.run(main())
