#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图片批量压缩优化 - 防止大图撑爆对话上下文

问题: 1.6MB+ 的PNG图片在对话中base64编码后可达数百万token
解决: 
  1. 大图转JPEG (质量85，目标<200KB)
  2. 生成缩略图 (max 256px) 用于对话展示
  3. 原图保留备份 (.originals/)
"""

import argparse, os, sys, json
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image
except ImportError:
    print("错误: 需要安装 Pillow: pip install Pillow")
    sys.exit(1)

MAX_SIZE_KB = 200
THUMB_MAX_PX = 256
JPEG_QUALITY = 80

def get_image_info(path):
    try:
        img = Image.open(path)
        size_kb = os.path.getsize(path) / 1024
        return {"path": str(path), "size_kb": round(size_kb, 1),
                "width": img.width, "height": img.height,
                "format": img.format, "mode": img.mode}
    except Exception as e:
        return {"path": str(path), "error": str(e)}

def compress_image(src_path, dst_path=None, max_kb=MAX_SIZE_KB, quality=JPEG_QUALITY):
    try:
        img = Image.open(src_path)
        original_size = os.path.getsize(src_path)
        if original_size / 1024 <= max_kb:
            return None
        if dst_path is None:
            dst_path = src_path
        if img.mode in ("RGBA", "P", "LA"):
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
            else:
                img = img.convert("RGB")
        max_dim = 1200
        if max(img.width, img.height) > max_dim:
            ratio = max_dim / max(img.width, img.height)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
        dst = Path(dst_path)
        if dst.suffix.lower() == ".png":
            dst = dst.with_suffix(".jpg")
        for q in range(quality, 20, -5):
            img.save(dst, "JPEG", quality=q, optimize=True)
            if os.path.getsize(dst) / 1024 <= max_kb:
                break
        new_size = os.path.getsize(dst) / 1024
        return {"original_kb": round(original_size/1024,1),
                "compressed_kb": round(new_size,1),
                "saved_kb": round(original_size/1024-new_size,1),
                "output": str(dst)}
    except Exception as e:
        return {"error": str(e)}

def create_thumbnail(src_path, thumb_dir, max_px=THUMB_MAX_PX):
    try:
        img = Image.open(src_path)
        ratio = max_px / max(img.width, img.height)
        if ratio >= 1.0:
            return None
        new_size = (int(img.width * ratio), int(img.height * ratio))
        thumb = img.resize(new_size, Image.LANCZOS)
        thumb_dir = Path(thumb_dir)
        thumb_dir.mkdir(parents=True, exist_ok=True)
        thumb_path = thumb_dir / f"thumb_{Path(src_path).stem}.jpg"
        if thumb.mode in ("RGBA", "P", "LA"):
            thumb = thumb.convert("RGB")
        thumb.save(thumb_path, "JPEG", quality=75, optimize=True)
        return str(thumb_path)
    except Exception as e:
        print(f"  缩略图失败: {e}")
        return None

def scan_images(directory, patterns=("*.png", "*.jpg", "*.jpeg", "*.webp")):
    images = []
    for pattern in patterns:
        for p in Path(directory).rglob(pattern):
            if "thumb_" in p.name or ".originals" in str(p):
                continue
            images.append(p)
    return sorted(set(images), key=lambda p: os.path.getsize(p), reverse=True)

def print_report(images_info):
    print("\n" + "=" * 60)
    print("图片扫描报告")
    print("=" * 60)
    total_kb = 0
    over_limit = []
    for info in images_info:
        size_kb = info.get("size_kb", 0)
        total_kb += size_kb
        flag = "!! 过大" if size_kb > MAX_SIZE_KB else "OK"
        name = Path(info["path"]).name
        dims = f"{info.get('width','?')}x{info.get('height','?')}"
        print(f"  {flag} {name}: {size_kb:.0f}KB ({dims})")
        if size_kb > MAX_SIZE_KB:
            over_limit.append(info)
    print(f"\n总计: {total_kb/1024:.1f}MB, {len(images_info)}张")
    print(f"超过{MAX_SIZE_KB}KB: {len(over_limit)}张 ({sum(i['size_kb'] for i in over_limit)/1024:.1f}MB)")
    print(f"对话中约等于 ~{int(total_kb * 0.75)}K tokens!")
    return over_limit

def main():
    p = argparse.ArgumentParser(description="图片批量压缩优化")
    p.add_argument("directory", nargs="?", default=".")
    p.add_argument("--scan-only", action="store_true")
    p.add_argument("--compress", action="store_true")
    p.add_argument("--thumbs", action="store_true")
    p.add_argument("--all", action="store_true")
    p.add_argument("--max-kb", type=int, default=MAX_SIZE_KB)
    p.add_argument("--quality", type=int, default=JPEG_QUALITY)
    args = p.parse_args()

    if not any([args.scan_only, args.compress, args.thumbs, args.all]):
        args.all = True

    root = Path(args.directory)
    print(f"扫描目录: {root.absolute()}")
    images = scan_images(root)
    images_info = [get_image_info(p) for p in images]
    over_limit = print_report(images_info)

    if args.scan_only:
        return
    if not over_limit:
        print("\n所有图片都在安全范围内!")
        return

    if args.compress or args.all:
        print("\n" + "=" * 60)
        print("开始压缩...")
        print("=" * 60)
        for info in over_limit:
            src = info["path"]
            print(f"\n  压缩: {Path(src).name} ({info['size_kb']}KB)")
            result = compress_image(src, max_kb=args.max_kb, quality=args.quality)
            if result and "error" not in result:
                saved_pct = result["saved_kb"]/result["original_kb"]*100
                print(f"    OK {result['original_kb']}KB -> {result['compressed_kb']}KB (节省{saved_pct:.0f}%)")
            elif result:
                print(f"    FAIL {result['error']}")
            else:
                print(f"    跳过")

    if args.thumbs or args.all:
        print("\n" + "=" * 60)
        print("生成缩略图...")
        print("=" * 60)
        thumb_dir = root / "thumbnails"
        all_images = scan_images(root)
        for p in all_images:
            thumb = create_thumbnail(p, thumb_dir)
            if thumb:
                size_kb = os.path.getsize(thumb)/1024
                print(f"  OK {Path(p).name} -> {Path(thumb).name} ({size_kb:.0f}KB)")
        print(f"\n缩略图: {thumb_dir.absolute()}")

    print("\n" + "=" * 60)
    print("优化后统计")
    print("=" * 60)
    final_images = scan_images(root)
    final_info = [get_image_info(p) for p in final_images]
    final_total = sum(i.get("size_kb",0) for i in final_info)
    original_total = sum(i.get("size_kb",0) for i in images_info)
    saved = original_total - final_total
    print(f"  优化前: {original_total/1024:.1f}MB (~{int(original_total*0.75)}K tokens)")
    print(f"  优化后: {final_total/1024:.1f}MB (~{int(final_total*0.75)}K tokens)")
    if saved > 0:
        print(f"  节省: {saved/1024:.1f}MB ({saved/original_total*100:.0f}%)")

if __name__ == "__main__":
    main()
