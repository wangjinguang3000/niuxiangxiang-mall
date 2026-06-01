import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright

ANNOUNCEMENTS = [
    {"title":"Grassland Pet Interaction Season Starts!",
     "content":"NiuXiangXiang Grassland Pet Interaction Season S1 is now open for registration!\n\nDate: July 2026\nLocation: Duolun County, Xilingol, Inner Mongolia\nCapacity: 60-100 groups (1 person + 1 dog)\nFee: 1980/group (Early bird 1780, limited 20)\n\n4 Events:\n1. Willpower Challenge - Stay still facing steak\n2. Fetch Relay - Run on grassland\n3. Fun Obstacle - Tunnel and jumps\n4. Talent Show - Anything goes!\n\nIncludes: Mongolian yurt 3D2N, all meals (roast lamb), 8000 prize pool, pro photographer, beef liver gift pack.\n\nRegister: Click event entry on homepage\nContact: Manager Wang 13145294218","sort":"1"},
    {"title":"Beef Liver Jerky Officially Launched!",
     "content":"NiuXiangXiang Beef Liver Jerky is now available!\n\nWe make pet treats with human food standards.\n\nWhy beef liver?\n- High protein: 29g/100g\n- Rich in iron, zinc, Vitamin A\n- Natural meat aroma, no attractants needed\n\nZero Additives Promise:\n- 0 preservatives\n- 0 attractants\n- 0 grains\n- 0 coloring\nIngredients: Fresh beef liver. Just that.\n\n3 sizes:\n- 80g pack: 16 yuan\n- 240g box (3 packs): 48 yuan\n- 480g gift box (6 packs): 88 yuan\n\nOwn factory | SC10415255102074\nXilingol, Inner Mongolia","sort":"2"},
    {"title":"Looking for City Partners - Join Us!",
     "content":"NiuXiangXiang is looking for pet-loving city partners!\n\nWe offer:\n- Own factory direct supply\n- Complete brand story\n- Solo-operation possible, asset-light model\n- Event IP empowerment\n\nWho fits?\n- Pet shop owners\n- Pet influencers\n- Community group leaders\n\nCooperation modes:\n1. Dropshipping (zero inventory)\n2. Regional agent (exclusive territory)\n3. Brand co-branding (custom packaging)\n\nContact: Manager Wang 13145294218","sort":"3"},
]

GUIDES = [
    {"title":"Competition Guide - Full Strategy",
     "content":"[Preparation]\n1. Confirm registration (1 person + 1 dog)\n2. WeChat group created 7 days before\n3. Bring dog health certificate (vaccine book)\n4. Pack dog daily supplies (food, water bowl, leash)\n\n[Transportation]\n- Self-drive: Beijing ~4-5 hours (G95 highway)\n- Bus: to Duolun county, we shuttle to camp\n- Train+shuttle: to Zhangjiakou, we arrange\n\n[Accommodation]\n- Mongolian yurt (2 per yurt or family yurt)\n- Private bathroom yurts prioritized\n- Bring jacket (grassland nights are cool)\n\n[Competition Rules]\n- Willpower: dog stays still facing steak, longest wins\n- Fetch: fastest retrieve wins\n- Obstacle: fastest complete wins\n- Talent: audience voting\n\n[Q&A]\nQ: Does my dog need competition experience?\nA: No! This is for fun, not professional.\nQ: Can big/small dogs join?\nA: All breeds welcome!\nQ: Can I bring 2 dogs?\nA: Yes! Extra dog +300 yuan (includes bandana+insurance+photo)\nQ: What if weather is bad?\nA: We check 7 days before, postpone if extreme.","sort":"1"},
    {"title":"Feeding Guide - Beef Liver Jerky",
     "content":"[Recommended Serving]\n- Small dogs (<10kg): 10-20g daily\n- Medium dogs (10-25kg): 20-40g daily\n- Large dogs (>25kg): 40-60g daily\n\n[Feeding Tips]\n- Use as high-value training reward\n- Crumble on dog food to boost appetite\n- Soak in warm water for senior dogs\n- Carry on walks\n\n[Precautions]\n- Liver treats are great but dont overfeed\n- Keep within 10% of daily food intake\n- Puppies under 6 months: small amounts\n- Seal after opening, avoid moisture\n\n[Why dogs love beef liver?]\nLiver has natural meat aroma from Maillard reaction. Our low-temp baking preserves this natural fragrance.\n\n[Money-Saving Tips]\n- 480g gift box has lowest unit price (0.18/g)\n- Event-period discounts\n- Refer friends for mutual rewards","sort":"2"},
    {"title":"Franchise Guide - City Partner",
     "content":"[NiuXiangXiang City Partner Program]\n\nMode 1: Dropshipping (Zero threshold)\n- Zero inventory: we ship\n- Profit: 20-30% of retail\n- Best for: pet bloggers, group leaders, solo entrepreneurs\n- Start: just apply and verify\n\nMode 2: Regional Agent\n- Exclusive territory: 1-3 agents per city\n- Profit: 35-45% of retail\n- First order: 3000 yuan min\n- Best for: pet shops, offline channels\n\nMode 3: Brand Co-branding\n- Custom packaging with your brand\n- Profit: negotiated\n- Min order: 1000 boxes\n- Best for: pet brands, MCN agencies\n\n[We Provide]\n- Own factory, quality guaranteed\n- Full marketing materials (images+videos)\n- Event IP empowerment\n- After-sales guarantee (quality issues: refund)\n- Regular training\n\n[Process]\n1. Submit application\n2. Phone consultation\n3. Sign agreement\n4. Start!\n\nContact: Manager Wang 13145294218\nEmail: niuxiangxiang@163.com","sort":"3"},
    {"title":"Startup Diary - Building a Brand Solo",
     "content":"[NiuXiangXiang Startup Diary]\n\nDay 1 - Why Beef Liver?\nI have a dog and when I looked at pet treat ingredient lists, I got scared. Our factory makes beef jerky for humans. One day I thought: why not make dog treats with human food standards? Beef liver is the simplest - just one ingredient, no additives needed.\n\nDay 30 - First Batch\nOur first batch came out. The factory chef said this is good enough for humans. We all tried it - it tastes like beef jerky, just without seasoning. Dogs went crazy for it.\n\nDay 60 - Naming\nAfter much thought: NiuXiangXiang - simple, memorable, instantly says beef snacks.\n\nDay 90 - Grassland Inspiration\nVisited Xilingol to check beef liver source. Saw dogs running on endless grassland. Thought: why not host a grassland dog event? Not professional competition, just dogs and owners having fun.\n\nDay 120 - Solo Event Planning\nFrom venue, lodging, food, competitions, promotion - all solo. Biggest lesson: just do it. One person can make things happen.\n\nDay 150 - Today\nMini-program online, products listed, event registration open. Looking back, one person power is bigger than expected. Next goal: let more dog lovers know NiuXiangXiang.","sort":"4"},
]

async def do_announcements(page):
    print("\n=== Announcements ===")
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=module&a=welcome&module_name=first_duoduokes", wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(1)
    await page.click("text=更多设置")
    await asyncio.sleep(1)
    await page.click("text=公告管理")
    await asyncio.sleep(2)
    print(f"  URL: {page.url[:100]}")
    
    add_btn = await page.evaluate("""() => {
        var links = document.querySelectorAll("a");
        for (var i=0; i<links.length; i++) {
            if (links[i].innerText && links[i].innerText.trim() === "添加") {
                return links[i].href;
            }
        }
        return null;
    }""")
    print(f"  Add URL: {add_btn}")
    
    if not add_btn:
        print("  Cannot find add button")
        return
    
    for i, a in enumerate(ANNOUNCEMENTS):
        print(f"  Adding {i+1}: {a['title']}")
        await page.goto(add_btn, wait_until="domcontentloaded", timeout=10000)
        await asyncio.sleep(1)
        try:
            # Check form fields
            fields = await page.evaluate("""() => {
                var els = document.querySelectorAll("input, textarea, select");
                return Array.from(els).map(function(el) {
                    return {tag:el.tagName, type:el.type, name:el.name};
                });
            }""")
            print(f"    Fields: {[(f['tag']+'['+f['name']+']') for f in fields if f['name']]}")
            
            # Try filling common fields
            for f in fields:
                name = f["name"].lower()
                try:
                    if "title" in name or "name" in name:
                        await page.locator(f"[name='{f['name']}']").fill(a["title"])
                    elif "content" in name or "desc" in name or "info" in name or "detail" in name:
                        await page.locator(f"[name='{f['name']}']").fill(a["content"])
                    elif "sort" in name or "order" in name:
                        await page.locator(f"[name='{f['name']}']").fill(a["sort"])
                except:
                    pass
            
            # Submit
            submit_btn = page.locator("input[type=submit]")
            if await submit_btn.count() > 0:
                await submit_btn.first.click()
                await asyncio.sleep(2)
                print(f"    Submitted!")
            else:
                print(f"    No submit found")
        except Exception as e:
            print(f"    Fail: {e}")

async def do_guides(page):
    print("\n=== Guides ===")
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=module&a=welcome&module_name=first_duoduokes", wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(1)
    await page.click("text=更多设置")
    await asyncio.sleep(1)
    await page.click("text=新手攻略")
    await asyncio.sleep(2)
    print(f"  URL: {page.url[:100]}")
    
    add_btn = await page.evaluate("""() => {
        var links = document.querySelectorAll("a");
        for (var i=0; i<links.length; i++) {
            if (links[i].innerText && (links[i].innerText.trim() === "添加" || links[i].innerText.includes("添加"))) {
                return links[i].href;
            }
        }
        return null;
    }""")
    print(f"  Add URL: {add_btn}")
    
    if not add_btn:
        print("  Cannot find add button")
        return
    
    for i, g in enumerate(GUIDES):
        print(f"  Adding {i+1}: {g['title']}")
        await page.goto(add_btn, wait_until="domcontentloaded", timeout=10000)
        await asyncio.sleep(1)
        try:
            fields = await page.evaluate("""() => {
                var els = document.querySelectorAll("input, textarea, select");
                return Array.from(els).map(function(el) {
                    return {tag:el.tagName, type:el.type, name:el.name};
                });
            }""")
            print(f"    Fields: {[(f['tag']+'['+f['name']+']') for f in fields if f['name']]}")
            
            for f in fields:
                name = f["name"].lower()
                try:
                    if "title" in name or "name" in name:
                        await page.locator(f"[name='{f['name']}']").fill(g["title"])
                    elif "content" in name or "desc" in name or "info" in name:
                        await page.locator(f"[name='{f['name']}']").fill(g["content"])
                    elif "sort" in name or "order" in name:
                        await page.locator(f"[name='{f['name']}']").fill(g["sort"])
                except:
                    pass
            
            submit_btn = page.locator("input[type=submit]")
            if await submit_btn.count() > 0:
                await submit_btn.first.click()
                await asyncio.sleep(2)
                print(f"    Submitted!")
            else:
                print(f"    No submit found")
        except Exception as e:
            print(f"    Fail: {e}")

async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page(viewport={"width":1440,"height":900})
    
    print("Login...")
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=user&a=login&", wait_until="load", timeout=15000)
    await asyncio.sleep(1)
    await page.fill("input[name=username]", "w15024998286")
    await page.fill("input[name=password]", "w12345678")
    await page.click("input[type=submit]")
    await asyncio.sleep(3)
    print("OK")
    
    await do_announcements(page)
    await do_guides(page)
    
    print("\n=== ALL CONTENT DONE! ===")
    await browser.close()
    await pw.stop()

asyncio.run(main())