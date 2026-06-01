import sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

env_file = Path(r"D:\Users\36050\Documents\New project牛香香优选商城\.env")
creds = {}
with open(env_file, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            creds[k.strip()] = v.strip().strip("\"'")

USERNAME = creds["JHF_USERNAME"]
PASSWORD = creds["JHF_PASSWORD"]
BASE_URL = "https://h2025.jihuifan.com"
LOGIN_URL = f"{BASE_URL}/web/index.php?c=user&a=login&"

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    print(">>> 登录后台...")
    page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)
    time.sleep(2)
    if "login" in page.url:
        page.fill("input[name=username]", USERNAME)
        page.fill("input[name=password]", PASSWORD)
        page.click("input[type=submit]")
        time.sleep(3)
    ok = "login" not in page.url
    print(f"登录: {'OK' if ok else 'FAIL'}")

    if not ok:
        print(f"当前URL: {page.url}")
        browser.close()
        sys.exit(1)

    # Products
    print("\n--- 商品管理 ---")
    url = f"{BASE_URL}/web/index.php?c=site&a=entry&do=selfMall&m=first_duoduokes&op=selfMall&tab_id=0"
    page.goto(url, wait_until="networkidle", timeout=20000)
    time.sleep(2)
    products = page.evaluate("""() => {
        var rows = document.querySelectorAll("table tr");
        var r = [];
        rows.forEach(function(row) {
            var cells = row.querySelectorAll("td");
            if (cells.length > 5) {
                var name = (cells[1] && cells[1].innerText || "").trim();
                var price = (cells[3] && cells[3].innerText || "").trim();
                var stock = (cells[4] && cells[4].innerText || "").trim();
                if (name && name.length > 2 && !name.match(/^[0-9]+$/))
                    r.push({name: name.substring(0,40), price: price, stock: stock});
            }
        });
        return r;
    }""")
    print(f"商品数: {len(products)}")
    for p in products:
        print(f"  📦 {p['name']} | ¥{p['price']} | 库存:{p['stock']}")
    if len(products) == 0:
        print("  ⚠️ 后台无商品！需上传")

    # Banners
    print("\n--- 首页轮播 ---")
    url = f"{BASE_URL}/web/index.php?c=site&a=entry&do=indexSwiper&m=first_duoduokes&op=indexSwiper&tab_id=0"
    page.goto(url, wait_until="networkidle", timeout=20000)
    time.sleep(2)
    banners = page.evaluate("""() => {
        var rows = document.querySelectorAll("table tr");
        var r = [];
        rows.forEach(function(row) {
            var cells = row.querySelectorAll("td");
            if (cells.length > 3) {
                var t = (cells[1] && cells[1].innerText || "").trim();
                if (t) r.push(t.substring(0,50));
            }
        });
        return r;
    }""")
    print(f"Banner数: {len(banners)}")
    for b in banners:
        print(f"  🖼️ {b}")
    if len(banners) == 0:
        print("  ⚠️ 无轮播图！需上传")

    # Announcements
    print("\n--- 公告管理 ---")
    url = f"{BASE_URL}/web/index.php?c=site&a=entry&do=notice&m=first_duoduokes&op=notice&tab_id=0"
    page.goto(url, wait_until="networkidle", timeout=20000)
    time.sleep(2)
    notices = page.evaluate("""() => {
        var rows = document.querySelectorAll("table tr");
        var r = [];
        rows.forEach(function(row) {
            var cells = row.querySelectorAll("td");
            if (cells.length > 3) {
                var t = (cells[1] && cells[1].innerText || "").trim();
                if (t) r.push(t.substring(0,50));
            }
        });
        return r;
    }""")
    print(f"公告数: {len(notices)}")
    for n in notices:
        print(f"  📢 {n}")
    if len(notices) == 0:
        print("  ⚠️ 无公告！需添加")

    # Bottom Nav
    print("\n--- 底部导航 ---")
    url = f"{BASE_URL}/web/index.php?c=site&a=entry&do=bottomnav&m=first_duoduokes&op=bottomnav&tab_id=0"
    page.goto(url, wait_until="networkidle", timeout=20000)
    time.sleep(2)
    navs = page.evaluate("""() => {
        var rows = document.querySelectorAll("table tr");
        var r = [];
        rows.forEach(function(row) {
            var cells = row.querySelectorAll("td");
            if (cells.length > 3) {
                var t = (cells[1] && cells[1].innerText || "").trim();
                if (t) r.push(t.substring(0,40));
            }
        });
        return r;
    }""")
    print(f"导航项数: {len(navs)}")
    for n in navs:
        print(f"  🧭 {n}")
    if len(navs) == 0:
        print("  ⚠️ 无导航！需配置")

    # Guides
    print("\n--- 新手攻略 ---")
    url = f"{BASE_URL}/web/index.php?c=site&a=entry&do=article&m=first_duoduokes&op=article&tab_id=0"
    page.goto(url, wait_until="networkidle", timeout=20000)
    time.sleep(2)
    articles = page.evaluate("""() => {
        var rows = document.querySelectorAll("table tr");
        var r = [];
        rows.forEach(function(row) {
            var cells = row.querySelectorAll("td");
            if (cells.length > 3) {
                var t = (cells[1] && cells[1].innerText || "").trim();
                if (t) r.push(t.substring(0,50));
            }
        });
        return r;
    }""")
    print(f"攻略数: {len(articles)}")
    for a in articles:
        print(f"  📖 {a}")
    if len(articles) == 0:
        print("  ⚠️ 无攻略！需添加")

    browser.close()
    print("\n=== 探查完成 ===")
