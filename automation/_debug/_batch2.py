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
    return await p.evaluate('''()=>{var a=document.querySelectorAll("a");for(var i=0;i<a.length;i++){var t=(a[i].innerText||"").trim();if(t.includes("添加")||t.includes("新增")||t.includes("商品添加")||t.includes("发布"))return a[i].href}return""}''')

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
        
        # === 1. 每日开奖 ===
        log('🔧 每日开奖...')
        await go(p);await click(p,'每日开奖')
        add=await find_add(p)
        if add:
            await p.goto(add,wait_until='networkidle',timeout=10000)
            await fill_and_sub(p,{"title":"牛肝干480g礼盒装","stock":"3"})
            log('  ✅')
        
        # === 2. 0元购 ===
        log('🔧 0元购...')
        await go(p);await click(p,'0元购')
        add=await find_add(p)
        if add:
            await p.goto(add,wait_until='networkidle',timeout=10000)
            await fill_and_sub(p,{"title":"满¥48返¥5红包"})
            log('  ✅')
        
        # === 3. 免单红包 ===
        log('🔧 免单红包...')
        await go(p);await click(p,'免单红包')
        add=await find_add(p)
        if add:
            await p.goto(add,wait_until='networkidle',timeout=10000)
            await fill_and_sub(p,{"probability":"5"})
            log('  ✅')
        
        # === 4. 任务管理 ===
        log('🔧 任务管理...')
        await go(p);await click(p,'任务管理')
        tasks=[{"title":"每日签到 领金币","reward":"10金币"},{"title":"分享商品到微信群","reward":"20金币"}]
        add=await find_add(p)
        for t in tasks:
            if add:
                await p.goto(add,wait_until='networkidle',timeout=10000)
                await fill_and_sub(p,t)
                log(f'  {t["title"][:15]} ✅')
        
        # === 5. 小编推荐 ===
        log('🔧 小编推荐...')
        await go(p);await click(p,'小编推荐')
        recs=[{"title":"🏆 草原人宠互动季报名开启！","content":"带着狗狗去草原奔跑！3天2晚蒙古包，4大赛事，8000元奖金池"},{"title":"🐂 牛肝干凭什么这么香？","content":"只用一个配料：新鲜牛肝！低温烘焙48小时，0添加0诱食剂"}]
        add=await find_add(p)
        for r in recs:
            if add:
                await p.goto(add,wait_until='networkidle',timeout=10000)
                await fill_and_sub(p,r)
                log(f'  {r["title"][:15]} ✅')
        
        # === 6. 题库管理 ===
        log('🔧 题库管理...')
        await go(p);await click(p,'题库管理')
        qs=[{"title":"狗狗每天吃多少牛肝干合适？","answer":"小型犬10-20g，中型犬20-40g，大型犬40-60g"},{"title":"牛肝干有几个零添加承诺？","answer":"4个：0防腐剂、0诱食剂、0谷物、0色素"}]
        add=await find_add(p)
        for q in qs:
            if add:
                await p.goto(add,wait_until='networkidle',timeout=10000)
                await fill_and_sub(p,q)
                log(f'  {q["title"][:15]} ✅')
        
        await b.close()
        log('🎉 第二批完成！')

asyncio.run(main())
