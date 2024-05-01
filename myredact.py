import re

import fitz

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams, LTTextContainer
from pdfminer.converter import PDFPageAggregator
 

# 入力PDF
path = 'statement_202402.pdf'
# 出力PDF
outpath = 'out.pdf'

pages_to_redact = []
page_area = []
redact_coords_pages = []

not_redact_item_name = [
    "ｿﾌﾄﾊﾞﾝｸｴﾑ",
    "ドコモご利用料金",
    "スギ薬局",
]
not_redact_text = [
    'ご利用代金請求明細書',
    '楽天カード株式会社',
    '東京都港区南青山二丁目6番21号',
    '代表',
    'ご利用カード',
    'お支払い日',
    '返済方法',
    '引き落とし口座',
    '請求確定日',
    '利用獲得ポイント',
    '調整額',
    '返金額',
    '口座振替',
    'ご利用明細',
    '単位',
    "利用日 利用店名",
    "利用者",
    "支払方法",
    "利用金額",
    "手数料",
    "支払総額",
    "当月請求額 翌月繰越残高",
    "※ポイント支払いサービスをご利用された場合、ご利用ポイント分を差し引いた金額がご請求予定金額として表示されます。"

]
page_1_not_redact_layout_number = [
    1,
    5,
    15,
    18,
]

manager = PDFResourceManager()

# key = ページ番号, value = ページ内の黒塗りしないアイテムのY座標のリスト
notredactdict = {}
# key = ページ番号, value = ページ内の黒塗りするアイテムのタプル(x0, y0, x1, y1)のリスト
redactdict = {}

with open(path, 'rb') as input:
    with PDFPageAggregator(manager, laparams=LAParams()) as device:
        # PDFPageInterpreterオブジェクトの取得
        iprtr = PDFPageInterpreter(manager, device)

        # 1. まず全ページの全テキストレイアウトを走査して、黒塗りしない箇所の座標を取得する
        # 2. 次に、もう一度全ページの全テキストレイアウトを走査して、1で取得した座標と同じ高さのアイテムは除外しつつ、黒塗りする箇所の座標を取得する

        # 一回目の全ページ走査
        # 黒塗りしないアイテム名のY座標を取得する
        pages = list(PDFPage.get_pages(input))
        not_redact_coords_pages = []
        for page_number, page in enumerate(pages):
            notredactdict[page_number] = []

            iprtr.process_page(page)
            layouts = device.get_result()
            for layout_number, layout in enumerate(layouts):
                if isinstance(layout, LTTextContainer):
                    text = layout.get_text().strip()
                    x0 = layout.x0
                    x1 = layout.x1
                    y0 = layout.y0
                    y1 = layout.y1

                    # https://pymupdf.readthedocs.io/ja/latest/app3.html#coordinates
                    # https://pymupdf.readthedocs.io/ja/latest/app3.html#origin-point-point-size-and-y-axis
                    mupdf_y0 = 842 - y1
                    mupdf_y1 = 842 - y0

                    _y0 = int(mupdf_y0)

                    go_to_next_layout = False
                    for item_name in not_redact_item_name:
                        if re.search(item_name, text):

                            print(f'xyz {item_name} {text} {_y0}')

                            notredactdict[page_number].append(_y0)
                            go_to_next_layout = True
                            break

                    if go_to_next_layout:
                        continue

        print('== dump notredactdict ==')
        print(notredactdict)

        # 二回目の全ページ走査
        # 黒塗りする箇所の座標を取得する
        for page_number, page in enumerate(pages):
            print(f'+++ PAGE {page_number}')
            # 一回目の走査で見つけた、このページ内の黒塗りしないアイテムのY座標を復元する
            coords = notredactdict[page_number]

            redactdict[page_number] = []
            iprtr.process_page(page)
            layouts = device.get_result()
            for layout_number, layout in enumerate(layouts):
                if isinstance(layout, LTTextContainer):
                    text = layout.get_text().strip()

                    # 最後のページ以外は条件に応じて黒塗りするかどうかを判定する
                    # 最後のページは全てのテキストを黒塗りする
                    if page_number != len(pages)-1:
                        go_to_next_text = False
                        # 黒塗りしないテキストが含まれている場合はスキップ
                        for pattern in not_redact_text:
                            if re.search(pattern, text):
                                go_to_next_text = True
                                break
                        if go_to_next_text:
                            continue

                        # 一ページ目の場合は、特定のレイアウト番号のテキストは黒塗りしない
                        if page_number == 0:
                            if layout_number in page_1_not_redact_layout_number:
                                continue

                    x0 = layout.x0
                    x1 = layout.x1
                    y0 = layout.y0
                    y1 = layout.y1

                    # https://pymupdf.readthedocs.io/ja/latest/app3.html#coordinates
                    # https://pymupdf.readthedocs.io/ja/latest/app3.html#origin-point-point-size-and-y-axis
                    mupdf_y0 = 842 - y1
                    mupdf_y1 = 842 - y0

                    _y0 = int(mupdf_y0)

                    # 黒塗りしないアイテムのY座標と同じ高さのアイテムは黒塗りしない

                    found = any(y0 == _y0 for y0 in notredactdict[page_number])
                    if found:
                        print(f'found={found} skip {coords[0]} {_y0} {text}')
                        continue

                    redactdict[page_number].append((x0, mupdf_y0, x1, mupdf_y1))


#黒塗り箇所を2ヶ所指定
#座標形式：(右上のx座標、右上のy座標、左下のx座標、左下のy座標)
##redact_coords = [(37,80,550,219),(37,220,289,242)]

# 長永　健介 様, x0=22.86, x1=132.66, y0=778.77, y1=804.49, width=109.80, height=25.73
#redact_coords = [(132, 804, 22, 776)]
##redact_coords = [(22, 131, 50, 50)]

#print(redact_coords)

# 黒塗りページ

#redactor = Redactor(path,outpath,redact_coords)
#redactor.redaction(pages_to_redact)

# PDF開封
doc = fitz.open(path)
# 各ページをiterate
for i,page in enumerate(doc):
    areas = [fitz.Rect(coord) for coord in redactdict[i]]
    [page.add_redact_annot(area, fill = (0, 0, 0)) for area in areas]
    # 黒塗りする
    page.apply_redactions()

# 新しいPDFとして保存
doc.save(outpath)
print("Successfully redacted")
