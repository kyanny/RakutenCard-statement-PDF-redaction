import argparse
import re

import fitz
import mojimoji

parser = argparse.ArgumentParser()
parser.add_argument("pdf_path", help="Path to the PDF file")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

# 黒塗りしない「利用店名」
# 明細に半角カタカナで書いてあっても全角カタカナで指定してください
keep_items = [
    "ソフトバンクエム",
    "ドコモご利用料金",
]
# 黒塗りしないテキストのブロック番号
# ブロック番号は --debug オプション付きで実行するとわかります
keep_block_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18]

doc = fitz.open(args.pdf_path)
for page in doc:
    blocks = page.get_text("blocks")
    for block in blocks:
        x0, y0, x1, y1, text, block_no = block[:6]
        zenkaku_text = mojimoji.han_to_zen(text, ascii=False, digit=False, kana=True)

        if args.debug:
            print(f"Page number: {page.number}")
            print(f"Block number: {block_no}")
            print(f"Coordinates: ({x0}, {y0}, {x1}, {y1})")
            print(f"Text: {zenkaku_text}")
            print()

        if page.number == 0 and block_no in keep_block_numbers:
            pass
        elif re.search("|".join(keep_items), zenkaku_text):
            pass
        else:
            page.add_redact_annot((x0, y0, x1, y1), fill=(0, 0, 0))
            page.apply_redactions()

out_path = args.pdf_path.replace(".pdf", "_redacted.pdf")
doc.save(out_path)
print(out_path)
doc.close()
