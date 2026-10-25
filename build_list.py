#!/usr/bin/env python3
"""สแกนโฟลเดอร์ files/ แล้วสร้าง files.json ให้หน้าเว็บอ่าน

โครงสร้างที่รองรับ:
  files/
    1 - จันทร์ 26 ต.ค. 2569/
      บันทึกข้อความ-ขออนุญาตลาเรียน-303431.pdf
    2 - พฤหัสบดี 29 ต.ค. 2569/
      ...

รัน:  python3 build_list.py
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES_DIR = ROOT / "files"
OUTPUT = ROOT / "files.json"
TITLE = "ขออนุญาตลาเรียน"


def nfc(text):
    # macOS เก็บชื่อไฟล์ภาษาไทยแบบ NFD บางครั้ง แปลงเป็น NFC ให้ค้นหาได้ถูก
    return unicodedata.normalize("NFC", text)


def day_info(folder_name):
    m = re.match(r"^\s*(\d+)\s*-\s*(.+)$", folder_name)
    if m:
        return int(m.group(1)), m.group(2).strip()
    return 999, folder_name.strip()


def course_from(file_name):
    stem = Path(file_name).stem
    # เอาส่วนหลังขีด "-" ตัวสุดท้าย เช่น ...-ขออนุญาตลาเรียน-CWI01 4100 -> CWI01 4100
    return stem.rsplit("-", 1)[-1].strip()


def main():
    if not FILES_DIR.is_dir():
        raise SystemExit(f"ไม่พบโฟลเดอร์ {FILES_DIR}")

    days = []
    for folder in FILES_DIR.iterdir():
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        order, label = day_info(nfc(folder.name))
        files = []
        for pdf in sorted(folder.iterdir(), key=lambda p: nfc(p.name)):
            if pdf.suffix.lower() != ".pdf":
                continue
            files.append({
                # git บน macOS เก็บชื่อแบบ NFC (core.precomposeunicode) จึงใช้ NFC ใน path ด้วย
                "file": nfc(f"files/{folder.name}/{pdf.name}"),
                "name": nfc(pdf.name),
                "course": nfc(course_from(pdf.name)),
                "size": pdf.stat().st_size,
            })
        if files:
            days.append({"order": order, "label": label, "files": files})

    days.sort(key=lambda d: d["order"])
    OUTPUT.write_text(
        json.dumps({"title": TITLE, "days": days}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    total = sum(len(d["files"]) for d in days)
    print(f"สร้าง files.json แล้ว: {len(days)} วัน, {total} ไฟล์")


if __name__ == "__main__":
    main()
