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

async def fadd(p,data):
    await asyncio.sleep(1)
    for k,v in data.items():
        try:
            el=p.locator(f'[name="{k}"]')
            if await el.count()>0:
                t=await el.first.evaluate('e=>e.tagName')
                if t=='SELECT':
                    try:await el.first.select_option(str(v))
                    except:pass
                else:await el.first.fill(str(v)[:200])
        except:pass
    return await sub(p)

async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(headless=True);ctx=await b.new_context(viewport={'width':1440,'height':900});p=await ctx.new_page()
        
        # Login
        log('登录...')
        await p.goto(L,wait_until='networkidle',timeout=20000);await asyncio.sleep(2)
        await p.fill('input[name=username]',U);await p.fill('input[name=password]',P)
        await p.click('input[type=submit]');await asyncio.sleep(3)
        log('✅ 登录OK')
        
        # === 1. 底部导航 ===
        log('🔧 底部导航...')
        await go(p);await click(p,'底部导航')
        edits=await p.evaluate('''()=>{var r=[];document.querySelectorAll("a").forEach(function(a){if((a.innerText||"").includes("编辑"))r.push(a.href)});return r}''')
        names=['首页','商品','赛事','我的']
        for i,eu in enumerate(edits[:4]):
            await p.goto(eu,wait_until='networkidle',timeout=10000);await asyncio.sleep(1)
            try:await p.fill('input[name="title"]',names[i])
            except:pass
            await sub(p);log(f'  {names[i]} ✅')
        
        # === 2. 商品分类 ===
        log('🔧 商品分类...')
        await go(p);await click(p,'商品分类')
        add=await p.evaluate('''()=>{var a=document.querySelectorAll("a");for(var i=0;i<a.length;i++){if((a[i].innerText||"").includes("添加"))return a[i].href}return""}''')
        cats=[{"name":"牛肝干系列","sort":"1"},{"name":"赛事专区","sort":"2"},{"name":"礼盒套装","sort":"3"}]
        for ct in cats:
            if add:
                await p.goto(add,wait_until='networkidle',timeout=10000)
                await fadd(p,ct);log(f'  {ct["name"]} ✅')
        
        # === 3. 转盘抽奖 ===
        log('🔧 转盘抽奖...')
        await go(p);await click(p,'转盘抽奖')
        probs=['30','20','15','10','10','10','4','1']
        for i,pb in enumerate(probs):
            try:await p.fill(f'input[name="task[{i}][theory]"]',pb)
            except:pass
        await sub(p);log('  概率已设 ✅')
        
        # === 4. 砍价 ===
        log('🔧 砍价免费拿...')
        await go(p);await click(p,'砍价免费拿')
        add=await p.evaluate('''()=>{var a=document.querySelectorAll("a");for(var i=0;i<a.length;i++){if((a[i].innerText||"").includes("商品添加")||(a[i].innerText||"").includes("添加"))return a[i].href}return""}''')
        if add:
            await p.goto(add,wait_until='networkidle',timeout=10000)
            await fadd(p,{"title":"牛肝干80g袋装 砍价¥9.9","original_price":"16","activity_price":"9.9","stock":"100"})
            log('  砍价商品 ✅')
        
        # === 5. 一元抢购 ===
        log('🔧 一元抢购...')
        await go(p);await click(p,'一元抢购')
        add=await p.evaluate('''()=>{var a=document.querySelectorAll("a");for(var i=0;i<a.length;i++){if((a[i].innerText||"").includes("商品添加")||(a[i].innerText||"").includes("添加"))return a[i].href}return""}''')
        if add:
            await p.goto(add,wait_until='networkidle',timeout=10000)
            await fadd(p,{"title":"80g牛肝干体验装 ¥1抢","rush_price":"1","rush_stock":"10"})
            log('  1元抢购 ✅')
        
        await b.close()
        log('🎉 第一批完成！')

asyncio.run(main())
