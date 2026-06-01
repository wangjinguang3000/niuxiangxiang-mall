#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""牛香香商城 · 一键填充全部内容 v1"""
import asyncio, sys, time, re
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright
from pathlib import Path

# 凭证
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
BASE = 'https://h2025.jihuifan.com'
LOGIN_URL = f'{BASE}/web/index.php?c=user&a=login&'
OUT_DIR = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\automation\output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ===== 内容数据 =====
ANNOUNCEMENTS = [
    {"title": "草原人宠互动季正式启动！", "sort": "1",
     "content": "牛香香草原人宠互动季第一季开放报名！\n\n时间：2026年7月\n地点：内蒙古锡林郭勒多伦县\n规模：60-100组（1人+1狗）\n费用：1980元/组（早鸟价1780元，限20名）\n\n四大比赛项目：\n1. 意志力挑战赛——面对牛排坐住不动\n2. 叼物接力赛——草原上奔跑接力\n3. 趣味障碍赛——隧道+跳杆+绕桩\n4. 才艺大比拼——各种才艺都欢迎\n\n费用包含：蒙古包3天2晚、全部餐饮（含烤全羊）、8000元奖金池、专业摄影师跟拍、牛肝干伴手礼。\n\n报名方式：首页点击赛事入口\n咨询电话：13145294218 王经理"},
    {"title": "牛香香牛肝干正式上线！配料表只有新鲜牛肝", "sort": "2",
     "content": "牛香香牛肝干正式上线！\n\n我们用人食标准做宠物零食。\n\n为什么选牛肝？\n- 高蛋白：29g/100g\n- 富含铁、锌、维生素A\n- 天然肉香，无需诱食剂\n\n零添加承诺：\n- 0防腐剂\n- 0诱食剂\n- 0谷物\n- 0色素\n配料表只有一样：新鲜牛肝。\n\n三种规格：\n- 80g袋装：16元\n- 240g盒装（3袋）：48元\n- 480g礼盒装（6袋）：88元\n\n自有工厂 | SC10415255102074\n内蒙古锡林郭勒"},
    {"title": "招商加盟 寻找城市合伙人", "sort": "3",
     "content": "牛香香正在寻找热爱宠物的城市合伙人！\n\n我们提供：\n- 自有工厂直供\n- 完整品牌故事\n- 一人可操作，轻资产模式\n- 赛事IP赋能\n\n适合人群：\n- 宠物店主\n- 宠物博主/达人\n- 社群群主/团长\n\n合作模式：\n1. 一件代发（零库存）\n2. 区域代理（独家区域）\n3. 品牌联名（定制包装）\n\n咨询电话：13145294218 王经理\n邮箱：niuxiangxiang@163.com"},
]

GUIDES = [
    {"title": "参赛指南 · 草原人宠互动季全攻略", "sort": "1",
     "content": "【赛前准备】\n1. 确认报名信息（1人+1狗）\n2. 赛前7天建微信群\n3. 携带狗狗健康证（疫苗本）\n4. 备好狗狗日用品（粮、水碗、牵引绳）\n\n【交通方式】\n- 自驾：北京出发约4-5小时（G95高速）\n- 大巴：到多伦县城，我们接站到营地\n- 火车+接驳：到张家口站，我们安排接驳车\n\n【住宿安排】\n- 蒙古包（2人一包或家庭包）\n- 独立卫浴包间优先分配\n- 带件外套（草原晚上凉）\n\n【比赛规则】\n- 意志力：狗狗面对牛排坐住不动，坚持最久获胜\n- 叼物接力：最快叼回获胜\n- 障碍赛：最快完赛获胜\n- 才艺赛：观众投票\n\n【常见问题】\nQ: 狗狗需要参赛经验吗？\nA: 不用！这是趣味比赛，不是专业赛。\nQ: 大型犬/小型犬都能参加吗？\nA: 所有犬种都欢迎！\nQ: 能带2只狗吗？\nA: 可以！多一只加300元（含围巾+保险+拍照）\nQ: 天气不好怎么办？\nA: 赛前7天看天气预报，极端天气延期。"},
    {"title": "喂养指南 · 牛肝干的正确喂法", "sort": "2",
     "content": "【推荐喂食量】\n- 小型犬（<10kg）：每天10-20g\n- 中型犬（10-25kg）：每天20-40g\n- 大型犬（>25kg）：每天40-60g\n\n【喂食技巧】\n- 作为高价值训练奖励\n- 掰碎拌粮，提升食欲\n- 温水泡软给老年犬\n- 遛狗时随身携带\n\n【注意事项】\n- 肝脏零食虽好，不要过量\n- 控制在每日食量10%以内\n- 6个月以下幼犬少量喂\n- 开封后密封保存，避免受潮\n\n【为什么狗狗爱吃牛肝？】\n牛肝含有天然肉香物质，低温烘焙锁住天然风味，不用加诱食剂就超香。\n\n【省钱Tips】\n- 480g礼盒装单价最低（0.18元/g）\n- 赛事期间有限时优惠\n- 推荐好友互得奖励"},
    {"title": "加盟指南 · 如何成为牛香香城市合伙人", "sort": "3",
     "content": "【牛香香城市合伙人计划】\n\n模式一：一件代发（零门槛）\n- 零库存：我们代发\n- 利润：零售价20-30%\n- 适合：宠物博主、群主团长、个人创业者\n- 流程：提交申请→审核→开通\n\n模式二：区域代理\n- 独家区域：每城市1-3个代理\n- 利润：零售价35-45%\n- 首批进货：3000元起\n- 适合：宠物店、线下渠道\n\n模式三：品牌联名\n- 定制包装+你的品牌\n- 利润：面议\n- 起订量：1000盒\n- 适合：宠物品牌、MCN机构\n\n【我们提供】\n- 自有工厂，品质保障\n- 全套营销素材（图+视频）\n- 赛事IP赋能\n- 售后保障（质量问题包退）\n- 定期培训\n\n【加盟流程】\n1. 提交申请\n2. 电话沟通\n3. 签署协议\n4. 正式开始！\n\n咨询：13145294218 王经理"},
    {"title": "创业日记 · 一个人搞一个品牌的故事", "sort": "4",
     "content": "【牛香香创业日记】\n\nDay 1 - 为什么选牛肝？\n我养了一只狗，每次买零食都看配料表：全是淀粉和添加剂。我想为什么不能用人吃的标准做宠物零食？于是决定从内蒙古草原新鲜牛肝开始。\n\nDay 30 - 找工厂\n跑了锡林郭勒三个旗县，终于找到愿意小批量代工的工厂。老板说：\"人食车间做宠物零食？你认真的？\"我说：\"正因为我认真，才选人食标准。\"\n\nDay 60 - 第一锅试产\n低温烘焙48小时，打开烤箱那刻，整层楼都闻到了肉香。第一批样品送给朋友试，他们的狗吃完追着袋子跑。\n\nDay 90 - 上线准备\n产品出来了，下一个问题：怎么让人知道？我决定办草原人宠互动季——把爱狗的人聚到大草原上，让产品自己说话。\n\n做品牌不是砸钱，是用心。一个人也能做出好品牌。"},
]

NAV_ITEMS = [
    {"name": "首页", "icon": "home", "link": "pages/index/index", "sort": "1"},
    {"name": "商品", "icon": "shop", "link": "pages/shop/index", "sort": "2"},
    {"name": "赛事", "icon": "event", "link": "pages/event/index", "sort": "3"},
    {"name": "我的", "icon": "my", "link": "pages/my/index", "sort": "4"},
]

TOPLINKS = [
    {"title": "🔥 草原人宠互动季报名中", "link": "/pages/event/index", "sort": "1"},
    {"title": "🎁 新人首单立减3元", "link": "/pages/shop/index", "sort": "2"},
]

def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}')

async def do_login(page):
    log('登录后台...')
    await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
    await asyncio.sleep(2)
    if 'login' in page.url.lower():
        await page.fill('input[name=username]', USERNAME)
        await page.fill('input[name=password]', PASSWORD)
        await page.click('input[type=submit]')
        await asyncio.sleep(4)
    ok = 'login' not in page.url.lower()
    log(f'登录: {"OK" if ok else "FAIL"}')
    return ok

async def goto_module(page, name, list_url):
    """导航到模块列表页，返回是否有数据"""
    log(f'打开: {name}')
    await page.goto(list_url, wait_until='networkidle', timeout=20000)
    await asyncio.sleep(2)
    # 检测现有数据
    rows = await page.evaluate('''() => {
        var trs = document.querySelectorAll("table tr, table tbody tr");
        var count = 0;
        trs.forEach(function(tr) {
            var tds = tr.querySelectorAll("td");
            if (tds.length >= 3) count++;
        });
        return count;
    }''')
    log(f'  现有 {rows} 条数据')
    return rows

async def find_add_url(page):
    """找到'添加'按钮的链接"""
    return await page.evaluate('''() => {
        var links = document.querySelectorAll("a");
        for (var i = 0; i < links.length; i++) {
            var text = (links[i].innerText || "").trim();
            if (text === "添加" || text.includes("添加") || text === "新增" || text.includes("新增")) {
                return links[i].href || links[i].getAttribute("data-href") || "";
            }
        }
        return "";
    }''')

async def fill_and_submit(page, data, module_name):
    """通用表单填充和提交"""
    # 等待表单加载
    await asyncio.sleep(1)
    fields = await page.evaluate('''() => {
        var els = document.querySelectorAll("input[type=text], input[type=number], textarea, select, input[name]");
        var r = [];
        els.forEach(function(el) {
            var name = (el.name || el.id || "").toLowerCase();
            if (name && name !== "token" && el.type !== "hidden") {
                r.push({name: name, tag: el.tagName, type: el.type, placeholder: (el.placeholder||"").substring(0,30)});
            }
        });
        return r;
    }''')
    log(f'  表单字段: {[(f["name"][:20]) for f in fields[:10]]}')
    
    # 智能匹配填充
    filled = 0
    for f in fields:
        name = f['name'].lower()
        val = None
        if any(k in name for k in ['title', 'name', 'cname']):
            val = data.get('title') or data.get('name') or ''
        elif any(k in name for k in ['content', 'desc', 'detail', 'info', 'intro', 'body']):
            val = data.get('content') or ''
        elif any(k in name for k in ['sort', 'order', 'displayorder', 'rank']):
            val = data.get('sort') or '1'
        elif any(k in name for k in ['link', 'url', 'href']):
            val = data.get('link') or data.get('url') or ''
        elif any(k in name for k in ['price']):
            val = data.get('price') or ''
        
        if val is not None:
            try:
                if f['tag'] == 'TEXTAREA':
                    await page.fill(f'textarea[name="{f["name"]}"]', str(val)[:10000])
                elif f['tag'] == 'SELECT':
                    try:
                        await page.select_option(f'select[name="{f["name"]}"]', str(val))
                    except:
                        pass
                else:
                    await page.fill(f'input[name="{f["name"]}"]', str(val)[:500])
                filled += 1
            except Exception as e:
                pass
    
    log(f'  填充了 {filled} 个字段')
    
    # 提交
    try:
        # 尝试多种提交方式
        for sel in ['input[type=submit]', 'button[type=submit]', 'button:has-text("提交")', 'button:has-text("保存")', 'input[value="提交"]']:
            btn = page.locator(sel)
            if await btn.count() > 0:
                await btn.first.click()
                await asyncio.sleep(3)
                log(f'  已提交!')
                return True
        log(f'  未找到提交按钮')
        return False
    except Exception as e:
        log(f'  提交失败: {e}')
        return False

async def fill_module(page, name, list_url, items):
    """填充一个模块的全部内容"""
    log(f'\n{"="*40}')
    log(f'填充: {name} ({len(items)}条)')
    
    existing = await goto_module(page, name, list_url)
    
    success = 0
    for i, item in enumerate(items):
        # 每次重新导航到列表页获取新的add URL
        await goto_module(page, name, list_url)
        add_url = await find_add_url(page)
        if not add_url:
            log(f'  [{i+1}/{len(items)}] 找不到添加按钮，尝试直接构造URL...')
            # 尝试从当前URL构造
            current = page.url
            # 替换op参数
            if 'op=' in current:
                add_url = re.sub(r'op=\w+', 'op=post', current)
            else:
                log(f'  无法构造URL，跳过')
                continue
        
        log(f'  [{i+1}/{len(items)}] {item.get("title", item.get("name", ""))}')
        try:
            await page.goto(add_url, wait_until='networkidle', timeout=15000)
            if await fill_and_submit(page, item, name):
                success += 1
        except Exception as e:
            log(f'  失败: {e}')
    
    log(f'  {name}: 成功 {success}/{len(items)}')
    return success

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await ctx.new_page()
        
        if not await do_login(page):
            print('\n登录失败，终止')
            await browser.close()
            return
        
        results = {}
        
        # 1. 公告管理
        results['公告'] = await fill_module(
            page, '公告管理',
            f'{BASE}/web/index.php?c=site&a=entry&do=notice&m=first_duoduokes&op=notice&tab_id=0',
            ANNOUNCEMENTS
        )
        
        # 2. 新手攻略
        results['攻略'] = await fill_module(
            page, '新手攻略',
            f'{BASE}/web/index.php?c=site&a=entry&do=article&m=first_duoduokes&op=article&tab_id=0',
            GUIDES
        )
        
        # 3. 置顶跳转
        results['置顶跳转'] = await fill_module(
            page, '置顶跳转',
            f'{BASE}/web/index.php?c=site&a=entry&do=topnav&m=first_duoduokes&op=topnav&tab_id=0',
            TOPLINKS
        )
        
        # 4. 底部导航（先检查现有，可能需要编辑而非新增）
        log(f'\n{"="*40}')
        log('底部导航: 检查现有配置...')
        await goto_module(page, '底部导航',
            f'{BASE}/web/index.php?c=site&a=entry&do=bottomnav&m=first_duoduokes&op=bottomnav&tab_id=0')
        results['导航'] = '已检查'
        
        # 截图汇总
        await page.screenshot(path=str(OUT_DIR / 'final_summary.png'))
        
        await browser.close()
        
        # 汇总
        print(f'\n{"="*50}')
        print(f'执行完成!')
        for k, v in results.items():
            print(f'  {k}: {v}')
        print(f'\n截图: {OUT_DIR}/final_summary.png')

asyncio.run(main())
