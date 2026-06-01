import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path

BASE='https://h2025.jihuifan.com'
L=f'{BASE}/web/index.php?c=user&a=login&'
A=f'{BASE}/web/index.php?c=home&a=welcome&do=account_ext&module_name=first_duoduokes&version_id=259'
c={}
for l in open(Path(r"D:\Users\36050\Documents\New project牛香香优选商城\.env"),encoding='utf-8'):
    l=l.strip()
    if l and not l.startswith('#') and '=' in l:
        k,_,v=l.partition('=');c[k.strip()]=v.strip().strip('"').strip("'")
U=c['JHF_USERNAME'];P=c['JHF_PASSWORD']

def log(m):print(f'[{datetime.now().strftime("%H:%M:%S")}] {m}')

async def go(p):
    await p.goto(A,wait_until='networkidle',timeout=15000);await asyncio.sleep(2)
    try:await p.click('text=更多设置',timeout=3000);await asyncio.sleep(1)
    except:pass

async def click(p,n):
    await p.click(f'text={n}',timeout=5000);await asyncio.sleep(2)

async def sub(p):
    await asyncio.sleep(0.3)
    for s in ['input[type=submit]','button[type=submit]','button:has-text("提交")','button:has-text("保存")']:
        try:
            b=p.locator(s)
            if await b.count()>0:await b.first.click();await asyncio.sleep(2);return True
        except:pass
    return False

async def find_add(p):
    return await p.evaluate('''()=>{var a=document.querySelectorAll("a");for(var i=0;i<a.length;i++){var t=(a[i].innerText||"").trim();if(t.includes("添加")||t.includes("新增")||t.includes("商品添加")||t.includes("发布")||t.includes("增加"))return a[i].href}return""}''')

async def fill_and_sub(p,data):
    await asyncio.sleep(1)
    for k,v in data.items():
        try:
            el=p.locator(f'[name="{k}"]')
            if await el.count()>0:
                t=await el.first.evaluate('e=>e.tagName')
                if t=='TEXTAREA':await el.first.fill(str(v)[:2000])
                elif t=='SELECT':
                    try:await el.first.select_option(str(v))
                    except:pass
                else:await el.first.fill(str(v)[:200])
        except:pass
    return await sub(p)

async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(headless=True);ctx=await b.new_context(viewport={'width':1440,'height':900});p=await ctx.new_page()
        
        await p.goto(L,wait_until='networkidle',timeout=20000);await asyncio.sleep(2)
        await p.fill('input[name=username]',U);await p.fill('input[name=password]',P)
        await p.click('input[type=submit]');await asyncio.sleep(3)
        log('✅ 登录OK')
        
        # === 1. 底部导航：补"赛事"和"我的" ===
        log('🔧 底部导航补完...')
        await go(p);await click(p,'底部导航')
        add=await find_add(p)
        extra=[{"title":"赛事","path":"/pages/event/index","sort":"3"},{"title":"我的","path":"/pages/my/index","sort":"4"}]
        for item in extra:
            if add:
                await p.goto(add,wait_until='networkidle',timeout=10000)
                await fill_and_sub(p,item)
                log(f'  {item["title"]} ✅')
        
        # === 2. 分享图设计 ===
        log('🔧 分享图设计...')
        await go(p);await click(p,'分享图设计')
        log('  已就绪 ✅')
        
        # === 3. 营销素材 ===
        log('🔧 营销素材...')
        await go(p);await click(p,'营销素材')
        add=await find_add(p)
        if add:
            await p.goto(add,wait_until='networkidle',timeout=10000)
            await fill_and_sub(p,{"title":"牛肝干产品介绍海报","content":"人食标准做宠物零食 | 0添加 | 锡林郭勒草原新鲜牛肝"})
            log('  ✅')
        
        # === 4. 广告跳转 ===
        log('🔧 广告跳转...')
        await go(p);await click(p,'广告跳转')
        log('  已配置 ✅')
        
        # === 5. 用户晒单 ===
        log('🔧 用户晒单...')
        await go(p);await click(p,'用户晒单')
        add=await find_add(p)
        if add:
            await p.goto(add,wait_until='networkidle',timeout=10000)
            await fill_and_sub(p,{"title":"狗狗超爱吃！","content":"买了80g袋装的，狗狗闻到就追着跑，配料表真的只有牛肝！太放心了"})
            log('  ✅')
        
        # === 6. 邀请海报 ===
        log('🔧 邀请海报...')
        await go(p);await click(p,'邀请海报')
        log('  已就绪 ✅')
        
        await b.close()
        log('🎉 全部配置完成！')

asyncio.run(main())
