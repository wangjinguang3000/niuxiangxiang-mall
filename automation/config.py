#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""牛香香优选商城 · 后端自动化总指挥"""

import asyncio, json, os, sys, time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

CONFIG = {
    "backend_url": "https://h2025.jihuifan.com",
    "login_url": "https://h2025.jihuifan.com/web/index.php?c=user&a=login&",
    "username": ""  # 从 .env 读取 JHF_USERNAME,
    "password": ""  # 从 .env 读取 JHF_PASSWORD,
    "output_dir": Path(r"D:\Users\36050\Documents\New project牛香香优选商城\automation\output"),
}
CONFIG["output_dir"].mkdir(parents=True, exist_ok=True)

PRODUCTS = [
    {"name": "牛肝干 80g 袋装", "price": "16.00", "stock": "999", "sort": "1", "commission": "10"},
    {"name": "牛肝干 240g 盒装（3袋）", "price": "48.00", "stock": "999", "sort": "2", "commission": "10"},
    {"name": "牛肝干 480g 礼盒装", "price": "88.00", "stock": "500", "sort": "3", "commission": "12"},
]
print("Config loaded OK")
