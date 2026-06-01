import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright

EDIT_URL = "https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=offNoticeEdit&m=first_duoduokes&op=offNoticeEdit&version_id=0"

UPDATES = [
    {"title":"Grassland Pet Interaction Season S1 - Sign Up Now!",
     "content":"NiuXiangXiang Grassland Pet Interaction Season S1 is now open!\n\nDate: July 2026\nLocation: Duolun, Xilingol, Inner Mongolia\nCapacity: 60-100 groups (1 person + 1 dog)\nFee: 1980/group (Early bird 1780, limited 20)\n\n4 Events: Willpower Challenge, Fetch Relay, Fun Obstacle, Talent Show\n\nIncludes: Mongolian yurt 3D2N, all meals + roast lamb, 8000 prize pool, pro photographer, beef liver gift pack.\n\nRegister on homepage! Contact: Manager Wang 13145294218"},
    {"title":"NiuXiangXiang Beef Liver Jerky - Launched!",
     "content":"NiuXiangXiang Beef Liver Jerky is now available!\n\nMade with human food standards:\n- Ingredients: fresh beef liver. Just that.\n- Zero additives: no preservatives, attractants, grains, coloring\n- High protein: 29g/100g\n- Low-temp baked, natural meat aroma\n\n3 Sizes:\n- 80g pack: 16 yuan\n- 240g box (3 packs): 48 yuan\n- 480g gift (6 packs): 88 yuan\n\nOwn factory | SC10415255102074 | Xilingol, Inner Mongolia"},
    {"title":"Join NiuXiangXiang - City Partners Wanted!",
     "content":"NiuXiangXiang is looking for pet-loving city partners!\n\nWe Offer:\n- Own factory direct supply, quality guaranteed\n- Complete brand story + marketing materials\n- Solo-operation possible, asset-light model\n- Event IP empowerment\n\n3 Cooperation Modes:\n1. Dropshipping (zero inventory, 20-30% profit)\n2. Regional Agent (exclusive territory, 35-45% profit)\n3. Brand Co-branding (custom packaging)\n\nContact: Manager Wang 13145294218\nEmail: niuxiangxiang@163.com"},
]

async def update_announce(page, num, data):
    print(f"  Updating #{num}: {data['title']}")
    # Edit links - the 3rd, 4th, 5th "编辑" links on page (skipping the main nav)
    edit_links = page.locator("text=编辑")
    count = await edit_links.count()
    print(f"    Edit links found: {count}")
    
    # The first few "编辑" are in the announcements table
    # Try clicking the Nth one
    idx = num - 1  # 0-based
    if idx < count:
        await edit_links.nth(idx).click()
        await asyncio.sleep(2)
        
        # Check form
        fields = await page.evaluate("""() => {
            var els = document.querySelectorAll("input, textarea, select");
            return Array.from(els).map(function(el) {
                return {tag:el.tagName, type:el.type, name:el.name};
            });
        }""")
        print(f"    Fields: {[(f['tag']+'['+f['name']+']') for f in fields if f['name']]}")
        
        try:
            for f in fields:
                name = f["name"].lower()
                if "title" in name or "name" in name:
                    await page.locator(f"[name='{f['name']}']").fill(data["title"])
                elif "content" in name or "desc" in name or "info" in name:
                    await page.locator(f"[name='{f['name']}']").fill(data["content"])
            
            await page.locator("input[type=submit]").first.click()
            await asyncio.sleep(2)
            print(f"    Done!")
        except Exception as e:
            print(f"    Fail: {e}")
    else:
        print(f"    Not enough edit links")

async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page(viewport={"width":1440,"height":900})
    
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=user&a=login&", wait_until="load", timeout=15000)
    await asyncio.sleep(1)
    await page.fill("input[name=username]", "w15024998286")
    await page.fill("input[name=password]", "w12345678")
    await page.click("input[type=submit]")
    await asyncio.sleep(3)
    
    print("Updating announcements...")
    await page.goto("https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=offNoticeManage&m=first_duoduokes&op=offNoticeManage&version_id=0", wait_until="domcontentloaded", timeout=10000)
    await asyncio.sleep(2)
    
    for i, update in enumerate(UPDATES):
        # Navigate back to list
        await page.goto("https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=offNoticeManage&m=first_duoduokes&op=offNoticeManage&version_id=0", wait_until="domcontentloaded", timeout=10000)
        await asyncio.sleep(1)
        await update_announce(page, i+1, update)
    
    print("\n=== Announcements Updated! ===")
    await browser.close()
    await pw.stop()

asyncio.run(main())