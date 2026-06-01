#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''牛香香品牌 · 双项目巡检脚本 v1.0
用法: python health_check.py
检查: 官网可达性、商城产品状态、Banner状态
'''

import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime
from playwright.sync_api import sync_playwright

SITE_URL = 'https://wangjinguang3000.github.io/niuxiangxiang/'
PAGES = ['', 'event.html', 'register.html', 'products.html', 'cooperation.html', 'franchise.html']

def check_website():
    print('=' * 50)
    print('🐕 网站巡检')
    print('=' * 50)
    issues = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for pname in PAGES:
            url = SITE_URL + pname
            try:
                resp = page.goto(url, timeout=15000)
                title = page.title()
                print(f'  ✅ {pname or "首页"}: HTTP {resp.status} | {title[:50]}')
            except Exception as e:
                print(f'  ❌ {pname or "首页"}: {str(e)[:60]}')
                issues.append(pname)
        browser.close()
    return issues

def check_mall():
    print('\n' + '=' * 50)
    print('🛒 商城巡检')
    print('=' * 50)
    issues = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Login
        try:
            page.goto('https://h2025.jihuifan.com/web/index.php?c=user&a=login&', timeout=20000)
            page.fill('input[name=username]', 'w15024998286')
            page.fill('input[name=password]', 'w12345678')
            page.click('input[type=submit]')
            page.wait_for_timeout(3000)
            print('  ✅ 登录成功')
        except Exception as e:
            print(f'  ❌ 登录失败: {str(e)[:60]}')
            browser.close()
            return ['LOGIN_FAILED']

        # Products
        try:
            page.goto('https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=selfMall&m=first_duoduokes&op=selfMall&tab_id=0', timeout=20000)
            page.wait_for_timeout(2000)
            products = page.evaluate('''() => {
                var rows = document.querySelectorAll('table tr');
                var r = [];
                rows.forEach(function(row) {
                    var cells = row.querySelectorAll('td');
                    if (cells.length > 5) {
                        var t = (cells[1] && cells[1].innerText || '').trim();
                        if (t && t.length > 2 && !t.match(/^[0-9]+$/))
                            r.push(t.substring(0,30));
                    }
                });
                return r;
            }''')
            print(f'  产品数: {len(products)}')
            for p in products:
                print(f'    - {p}')
            if len(products) < 3:
                print(f'  ⚠️ 产品不足3个！')
                issues.append('PRODUCTS_LOW')
        except Exception as e:
            print(f'  ❌ 产品检查失败: {str(e)[:60]}')
            issues.append('PRODUCTS_FAIL')

        # Banners
        try:
            page.goto('https://h2025.jihuifan.com/web/index.php?c=site&a=entry&do=indexSwiper&m=first_duoduokes&op=indexSwiper&tab_id=0', timeout=20000)
            page.wait_for_timeout(2000)
            banners = page.evaluate('''() => {
                var rows = document.querySelectorAll('table tr');
                var r = [];
                rows.forEach(function(row) {
                    var cells = row.querySelectorAll('td');
                    if (cells.length > 3) {
                        var t = (cells[1] && cells[1].innerText || '').trim();
                        if (t) r.push(t.substring(0,30));
                    }
                });
                return r;
            }''')
            print(f'  Banner数: {len(banners)}')
            for b in banners:
                print(f'    - {b}')
            if len(banners) < 3:
                print(f'  ⚠️ Banner不足3个！')
                issues.append('BANNERS_LOW')
        except Exception as e:
            print(f'  ❌ Banner检查失败: {str(e)[:60]}')
            issues.append('BANNERS_FAIL')

        browser.close()
    return issues

if __name__ == '__main__':
    print(f'牛香香品牌巡检 · {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    site_issues = check_website()
    mall_issues = check_mall()
    all_issues = site_issues + mall_issues
    print('\n' + '=' * 50)
    if all_issues:
        print(f'⚠️ 发现问题 {len(all_issues)} 个: {all_issues}')
    else:
        print('✅ 一切正常，双项目运行良好！')
    print('=' * 50)
