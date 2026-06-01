import sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    LOGIN_URL = "https://h2025.jihuifan.com/web/index.php?c=user&a=login&"
    page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)
    time.sleep(3)

    # Get all inputs
    inputs = page.evaluate("""() => {
        var els = document.querySelectorAll("input, button, select, textarea");
        var r = [];
        els.forEach(function(el) {
            r.push({
                tag: el.tagName,
                type: el.type || "",
                name: el.name || "",
                id: el.id || "",
                placeholder: (el.placeholder || "").substring(0,40),
                value: (el.value || "").substring(0,20),
                className: (el.className || "").substring(0,40)
            });
        });
        return r;
    }""")
    for i in inputs:
        print(f"  {i['tag']} name='{i['name']}' id='{i['id']}' type='{i['type']}' placeholder='{i['placeholder']}'")

    # Screenshot
    page.screenshot(path=r"D:\Users\36050\Documents\New project牛香香优选商城\automation\output\login_page.png")
    print("\n截图保存: login_page.png")

    browser.close()
