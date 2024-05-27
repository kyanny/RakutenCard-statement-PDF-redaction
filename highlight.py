import argparse
import re

import pymupdf
import mojimoji

parser = argparse.ArgumentParser()
parser.add_argument("pdf_path", help="Path to the PDF file")
parser.add_argument("--page", type=int, help="Page number to highlight")
parser.add_argument("--block", type=int, help="Block number to highlight")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

doc = pymupdf.open(args.pdf_path)
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

        if args.page is not None and page.number == args.page:
            if args.block is not None and block_no == args.block:
                page.add_highlight_annot((x0, y0, x1, y1))

out_path = args.pdf_path.replace(".pdf", "_highlighted.pdf")
doc.save(out_path)
print(out_path)
doc.close()
