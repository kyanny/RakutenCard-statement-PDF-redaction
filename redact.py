import pprint
import fitz
import sys
import mojimoji
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("pdf_path", help="Path to the PDF file")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

# Check if debug mode is enabled
if args.debug:
    print("Debug mode enabled")

# Rest of the code...
keep_items = [
    "ソフトバンクエム",
    "ドコモご利用料金",
]
keep_block_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18]

pdf_path = args.pdf_path
doc = fitz.open(pdf_path)
for page in doc:
    blocks = page.get_text("blocks")
    for block in blocks:
        x0, y0, x1, y1, text, block_no = block[:6]
        # Do something with the coordinates
        # Add your code here to process the coordinates
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

        # if (page.number == 0) and (block_no not in keep_block_numbers):
        #     page.add_redact_annot((x0, y0, x1, y1), fill=(0, 0, 0))
        #     page.apply_redactions()
        #     continue

        # if not re.search("|".join(keep_items), zenkaku_text):
        #     page.add_redact_annot((x0, y0, x1, y1), fill=(0, 0, 0))
        #     page.apply_redactions()

doc.save("out.pdf")
doc.close()
