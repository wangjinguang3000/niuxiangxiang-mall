import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path

BASE='https://h2025.jihuifan.com';L=f'{BASE}/web/index.php?c=user&a=login&'
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

async def count_table(p):
    return await p.evaluate('''()=>{var c=0;document.querySelectorAll("table tr").forEach(function(tr){var tds=tr.querySelectorAll("td");if(tds.length>=2&&tds[0].innerText.trim())c++});return c}''')

async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(headless=True);ctx=await b.new_context(viewport={'width':1440,'height':900});p=await ctx.new_page()
        
        await p.goto(L,wait_until='networkidle',timeout=20000);await asyncio.sleep(2)
        await p.fill('input[name=username]',U);await p.fill('input[name=password]',P)
        await p.click('input[type=submit]');await asyncio.sleep(3)
        log('✅ 登录OK')
        
        modules=['自营商城','商品分类','底部导航','公告管理','新手攻略','小编推荐','转盘抽奖','砍价免费拿','一元抢购','每日开奖','0元购','免单红包','任务管理','邀请海报','分享图设计','营销素材','广告跳转','用户晒单','题库管理']
        
        print('\n📊 牛香香优选商城 · 最终状态')
        print('='*50)
        for m in modules:
            try:
                await go(p);await click(p,m)
                cnt=await count_table(p)
                status='✅' if cnt>0 else '⚠️'
                print(f'  {status} {m}: {cnt}条')
            except:
                print(f'  ❌ {m}: 失败')
        
        await b.close()
        print('='*50)
        print('🎉 验证完成！')

asyncio.run(main())
