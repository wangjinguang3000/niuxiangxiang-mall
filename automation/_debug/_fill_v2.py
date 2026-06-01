#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用正确URL填充商城内容 v2"""
import asyncio, sys, time, re
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

AUTH = {'uname': creds['JHF_USERNAME'], 'pwd': creds['JHF_PASSWORD']}

# 正确的模块URLS（从侧边栏菜单发现）
MODULES = {
    '公告管理': {
        'list_url': f'{BASE}/web/index.php?c=site&a=entry&do=offNoticeManage&m=first_duoduokes&op=offNoticeManage',
        'post_url': f'{BASE}/web/index.php?c=site&a=entry&do=offNoticeManage&m=first_duoduokes&op=offNoticeManage&ac=post',
        'items': [
            {"title": "草原人宠互动季正式启动！", "sort": "1",
             "content": "牛香香草原人宠互动季第一季开放报名！\n\n时间：2026年7月\n地点：内蒙古锡林郭勒多伦县\n规模：60-100组（1人+1狗）\n费用：1980元/组（早鸟价1780元，限20名）\n\n四大比赛项目：意志力挑战赛、叼物接力赛、趣味障碍赛、才艺大比拼\n\n费用包含：蒙古包3天2晚、全部餐饮（含烤全羊）、8000元奖金池、专业摄影师跟拍、牛肝干伴手礼。\n\n咨询电话：13145294218 王经理"},
            {"title": "牛香香牛肝干正式上线！配料表只有新鲜牛肝", "sort": "2",
             "content": "牛香香牛肝干正式上线！\n\n我们用人食标准做宠物零食。\n\n为什么选牛肝？高蛋白29g/100g、富含铁锌维生素A、天然肉香无需诱食剂。\n\n零添加承诺：0防腐剂、0诱食剂、0谷物、0色素。配料表只有一样：新鲜牛肝。\n\n三种规格：80g袋装¥16、240g盒装¥48、480g礼盒装¥88\n\n自有工厂 | SC10415255102074 | 内蒙古锡林郭勒"},
            {"title": "招商加盟 寻找城市合伙人", "sort": "3",
             "content": "牛香香正在寻找热爱宠物的城市合伙人！\n\n我们提供：自有工厂直供、完整品牌故事、一人可操作轻资产模式、赛事IP赋能\n\n适合人群：宠物店主、宠物博主达人、社群群主团长\n\n合作模式：一件代发（零库存）、区域代理（独家区域）、品牌联名（定制包装）\n\n咨询电话：13145294218 王经理\n邮箱：niuxiangxiang@163.com"},
        ]
    },
    '新手攻略': {
        'list_url': f'{BASE}/web/index.php?c=site&a=entry&do=noviceStrategy&m=first_duoduokes&op=noviceStrategy',
        'post_url': f'{BASE}/web/index.php?c=site&a=entry&do=noviceStrategy&m=first_duoduokes&op=noviceStrategy&ac=post',
        'items': [
            {"title": "参赛指南 · 草原人宠互动季全攻略", "sort": "1",
             "content": "【赛前准备】1.确认报名信息 2.赛前7天建群 3.带狗狗疫苗本 4.备好狗狗日用品\n\n【交通】自驾北京出发4-5小时G95高速；大巴到多伦县城接站；火车到张家口站接驳\n\n【住宿】蒙古包2人一包或家庭包，独立卫浴优先，带外套草原晚上凉\n\n【规则】意志力赛坐住不动最久胜、叼物接力最快胜、障碍赛最快完赛胜、才艺赛观众投票\n\n【FAQ】Q:狗狗需要参赛经验吗？A:不用！这是趣味赛。Q:大小犬都能参加？A:所有犬种欢迎！"},
            {"title": "喂养指南 · 牛肝干的正确喂法", "sort": "2",
             "content": "【推荐喂食量】小型犬<10kg每天10-20g、中型犬10-25kg每天20-40g、大型犬>25kg每天40-60g\n\n【喂食技巧】作为高价值训练奖励、掰碎拌粮提升食欲、温水泡软给老年犬、遛狗随身携带\n\n【注意事项】控制在每日食量10%以内、6个月以下幼犬少量、开封后密封避免受潮\n\n【省钱Tips】480g礼盒装单价最低0.18元/g、赛事期间有限时优惠、推荐好友互得奖励"},
            {"title": "加盟指南 · 如何成为城市合伙人", "sort": "3",
             "content": "【模式一：一件代发】零库存我们发货、利润零售价20-30%、适合宠物博主/团长/个人创业者\n\n【模式二：区域代理】独家区域每城1-3代理、利润35-45%、首批3000元起、适合宠物店线下渠道\n\n【模式三：品牌联名】定制包装你的品牌、起订量1000盒、适合宠物品牌MCN机构\n\n【我们提供】自有工厂品质保障、全套营销素材、赛事IP赋能、售后保障质量问题包退、定期培训\n\n【流程】提交申请→电话沟通→签署协议→正式开始！\n咨询：13145294218 王经理"},
            {"title": "创业日记 · 一个人搞一个品牌的故事", "sort": "4",
             "content": "Day 1 - 为什么选牛肝？我养了只狗，每次买零食都看配料表全是淀粉和添加剂。我想为什么不能用人食标准做宠物零食？于是决定从内蒙古新鲜牛肝开始。\n\nDay 30 - 找工厂：跑了锡林郭勒三个旗县，终于找到愿意小批量代工的工厂。老板说人食车间做宠物零食你认真的？我说正因为认真才选人食标准。\n\nDay 60 - 第一锅试产：低温烘焙48小时，打开烤箱整层楼都闻到肉香。第一批样品送给朋友，他们的狗吃完追着袋子跑。\n\n做品牌不是砸钱，是用心。一个人也能做出好品牌。"},
        ]
    }
}

def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}')

async def fill_module(page, name, config):
    """填充一个模块"""
    log(f'\n{"="*50}')
    log(f'填充: {name} ({len(config["items"])}条)')
    
    for idx, item in enumerate(config['items']):
        log(f'  [{idx+1}/{len(config["items"])}] {item["title"][:30]}...')
        
        # 导航到添加页面
        await page.goto(config['post_url'], wait_until='load', timeout=20000)
        await asyncio.sleep(3)
        try:
            await page.wait_for_load_state('networkidle', timeout=8000)
        except:
            pass
        await asyncio.sleep(1)
        
        # 获取表单字段
        fields = await page.evaluate('''() => {
            var els = document.querySelectorAll("input:not([type=hidden]):not([type=submit]):not([type=checkbox]):not([type=radio]), textarea, select");
            return Array.from(els).map(function(el) {
                return {name: el.name || el.id || "", tag: el.tagName, type: el.type || "", placeholder: (el.placeholder||"").substring(0,30)};
            }).filter(function(f) { return f.name && f.name !== "token"; });
        }''')
        log(f'    字段: {[(f["name"][:15] + "(" + f["tag"] + ")") for f in fields[:12]]}')
        
        if not fields:
            # 截图看状态
            await page.screenshot(path=str(OUT_DIR / f'add_{name}_{idx}.png'))
            log(f'    无表单字段! 截图已保存')
            continue
        
        # 智能填充
        for f in fields:
            name_low = f['name'].lower()
            val = None
            if any(k in name_low for k in ['title', 'name', 'cname', 'subject']):
                val = item.get('title', '')
            elif any(k in name_low for k in ['content', 'desc', 'detail', 'info', 'intro', 'body', 'text', 'article']):
                val = item.get('content', '')
            elif any(k in name_low for k in ['sort', 'order', 'displayorder', 'rank', 'weight']):
                val = item.get('sort', '1')
            elif any(k in name_low for k in ['link', 'url', 'href', 'jump']):
                val = item.get('link', item.get('url', ''))
            
            if val is not None:
                try:
                    sel = f'[name="{f["name"]}"]'
                    if f['tag'] == 'TEXTAREA':
                        await page.fill(f'textarea{sel}', str(val)[:5000])
                    elif f['tag'] == 'SELECT':
                        try:
                            await page.select_option(f'select{sel}', str(val))
                        except:
                            pass
                    else:
                        await page.fill(f'input{sel}', str(val)[:300])
                except Exception as e:
                    pass
        
        # 提交
        submitted = False
        for btn_sel in ['input[type=submit]', 'button[type=submit]', 'button:has-text("提交")', 'button:has-text("保存")', 'input.btn-primary']:
            try:
                btn = page.locator(btn_sel)
                if await btn.count() > 0:
                    await btn.first.click()
                    await asyncio.sleep(3)
                    log(f'    已提交!')
                    submitted = True
                    break
            except:
                pass
        
        if not submitted:
            log(f'    未找到提交按钮')
            await page.screenshot(path=str(OUT_DIR / f'nosubmit_{name}_{idx}.png'))
            continue
        
        # 回到列表页确认
        await page.goto(config['list_url'], wait_until='load', timeout=15000)
        await asyncio.sleep(2)
        try:
            await page.wait_for_load_state('networkidle', timeout=8000)
        except:
            pass
    
    log(f'  {name}: 完成!')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await ctx.new_page()
        
        # 登录
        log('登录后台...')
        await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        await page.fill('input[name=username]', AUTH['uname'])
        await page.fill('input[name=password]', AUTH['pwd'])
        await page.click('input[type=submit]')
        await asyncio.sleep(4)
        log(f'登录: {"OK" if "login" not in page.url.lower() else "FAIL"}')
        
        # 先进入应用
        await page.goto(APP_URL, wait_until='networkidle', timeout=20000)
        await asyncio.sleep(3)
        
        # 填充各模块
        for name, config in MODULES.items():
            await fill_module(page, name, config)
        
        await browser.close()
        log('\n全部完成!')

asyncio.run(main())
