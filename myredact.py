import re

import fitz

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams, LTTextContainer
from pdfminer.converter import PDFPageAggregator
 
# class Redactor:
 
#     def __init__(self, path,outpath,redact_coords):
#         self.path = path
#         self.outpath = outpath
#         self.redact_coords = redact_coords
 
#     def redaction(self,page_nums):
#         # PDF開封
#         doc = fitz.open(self.path)
#         # 各ページをiterate
#         for i,page in enumerate(doc):
#             if i in page_nums:
#                 areas = [fitz.Rect(coord) for coord in self.redact_coords]
#                 [page.add_redact_annot(area, fill = (0, 0, 0)) for area in areas]
#                 # 黒塗りする
#                 page.apply_redactions()    
#         # 新しいPDFとして保存
#         doc.save(self.outpath)
#         print("Successfully redacted")


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

with open(path, 'rb') as input:
    with PDFPageAggregator(manager, laparams=LAParams()) as device:
        # PDFPageInterpreterオブジェクトの取得
        iprtr = PDFPageInterpreter(manager, device)

        # 1. まず全ページの全テキストレイアウトを走査して、黒塗りしない箇所の座標を取得する
        # 2. 次に、もう一度全ページの全テキストレイアウトを走査して、1で取得した座標と同じ高さのアイテムは除外しつつ、黒塗りする箇所の座標を取得する

        print('a')

        # 一回目の全ページ走査
        # 黒塗りしないアイテム名のY座標を取得する
        pages = list(PDFPage.get_pages(input))
        not_redact_coords_pages = []
        for page_number, page in enumerate(pages):
            not_redact_coords_page = []
            not_redact_coords = []
            iprtr.process_page(page)
            layouts = device.get_result()
            for layout_number, layout in enumerate(layouts):
                if isinstance(layout, LTTextContainer):
                    text = layout.get_text().strip()
                    x0 = layout.x0
                    x1 = layout.x1
                    y0 = layout.y0
                    y1 = layout.y1

                    mupdf_y0 = 842 - y1
                    mupdf_y1 = 842 - y0

                    go_to_next_layout = False
                    for item_name in not_redact_item_name:
                        if re.search(item_name, text):
                            print(f'xyz {item_name} {text} {mupdf_y0} {mupdf_y1}')
                            not_redact_coords.append((int(mupdf_y0), int(mupdf_y1)))
                            go_to_next_layout = True
                            break

                    if go_to_next_layout:
                        print('-------------')
                        not_redact_coords_page.append(not_redact_coords)
                        print(not_redact_coords_page)
                        continue

            print(not_redact_coords_page)
            not_redact_coords_pages.append(not_redact_coords_page)


        print(len(not_redact_coords_pages))
        print(not_redact_coords_pages)

        # 二回目の全ページ走査
        # 黒塗りする箇所の座標を取得する
#        pages = list(PDFPage.get_pages(input))
        for page_number, page in enumerate(pages):
            # 一回目の走査で見つけた、このページ内の黒塗りしないアイテムのY座標を復元する
            not_redact_coords = not_redact_coords_pages[page_number]
            print(not_redact_coords)

            redact_coords = []
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

                    mupdf_y0 = 842 - y1
                    mupdf_y1 = 842 - y0

                    # 黒塗りしないアイテムのY座標と同じ高さのアイテムは黒塗りしない
                    go_to_next_layout = False
                    for not_redact_coord in not_redact_coords:

#                        print([page_number, not_redact_coord[0], int(mupdf_y0), not_redact_coord[1], int(mupdf_y1), text])
                        if int(mupdf_y0) == not_redact_coord[0] and int(mupdf_y1) == not_redact_coord[1]:
#                            print(text)
                            go_to_next_layout = True
                            break
                    if go_to_next_layout:
                        continue

                    redact_coords.append((x0, mupdf_y0, x1, mupdf_y1))
            
            redact_coords_pages.append(redact_coords)


#        not_redact_coords_pages.append(not_redact_coords)
    
        print('b')

        # ページごとで処理を実行
        pages = list(PDFPage.get_pages(input))
        for page_number, page in enumerate(pages):
            break

            # このページの黒塗り箇所の座標
            redact_coords = []

            # 黒塗りしない行の座標を保存するデータ構造
            not_redact_coords = []

            iprtr.process_page(page)
            # ページ内の各テキストのレイアウト
            layouts = device.get_result()
            layout_number = -1
            for layout in layouts:
                layout_number += 1

                # 罫線などのオブジェクトが含まれているとエラーになるのを防ぐため
                if isinstance(layout, LTTextContainer):
                    # don't redact
                    text = layout.get_text().strip()

                    print(f'{layout_number}, # "{text}"')

                    # 最後のページは全部黒塗りする
                    if page_number != len(pages)-1:
                        go_to_next_text = False
                        for pattern in not_redact_text:
                            if re.search(pattern, text):
                                go_to_next_text = True
                                break
                        if go_to_next_text:
                            continue

                        if page_number == 0:
                            if layout_number in page_1_not_redact_layout_number:
                                continue

                    

                    # 各ページの左下を原点としている
                    # x0: テキストの左端のx座標
                    # x1: テキストの右端のx座標
                    # y0: テキストの下端のy座標
                    # y1: テキストの上端のy座標
                    # width: テキストの幅(x1 - x0)
                    # height: テキストの高さ(y1 - y0)
 #                   print(f'{layout.get_text().strip()}, x0={layout.x0:.2f}, x1={layout.x1:.2f}, y0={layout.y0:.2f}, y1={layout.y1:.2f}, width={layout.width:.2f}, height={layout.height:.2f}')

                    # これを pymupdf の座標形式に変換
                    x0 = layout.x0
                    x1 = layout.x1
                    y0 = layout.y0
                    y1 = layout.y1

                    # この 842 って何？どこから来た値？
                    # この 842 は、A4サイズのPDFの縦の長さを表しています。PDFの座標系は左下が原点で、上に向かってy座標が増えます。しかし、多くの画像処理ライブラリでは左上が原点で、下に向かってy座標が増えます。このため、PDFの座標系を画像の座標系に変換するために、A4サイズの縦の長さである 842 からPDFのy座標を引いています。

                    # 792ではなくて？
                    # あなたが指摘した通り、A4サイズの縦の長さは通常72ポイント/インチの解像度で792ポイントです。しかし、MuPDFはデフォルトで96DPIを使用しているため、A4サイズの縦の長さは842ポイントとなります。
                    #
                    # したがって、あなたのコードのコンテキストによりますが、もし72DPIを使用している場合は、792 - y1が正しいかもしれません。

                    mupdf_y0 = 842 - y1
                    mupdf_y1 = 842 - y0

                    go_to_next_item_flag_1 = False
                    for item_name in not_redact_item_name:
                        if re.search(item_name, text):
                            not_redact_coord_tuple = (int(mupdf_y0), int(mupdf_y1))
                            not_redact_coords.append(not_redact_coord_tuple )
                            go_to_next_item_flag_1 = True
                            break

                    if go_to_next_item_flag_1:
                        continue

                    # if re.search('スギ薬局', text):
                    #     sugi_tuple = (int(mupdf_y0), int(mupdf_y1))
                    #     sugi_coordinates.append(sugi_tuple)
                    #     continue

                    go_to_next_item_flag_2 = False
                    for not_redact_coord_tuple in not_redact_coords:
                        if int(mupdf_y0) == not_redact_coord_tuple[0] and int(mupdf_y1) == not_redact_coord_tuple[1]:
                            go_to_next_item_flag_2 = True
                            break

                    if go_to_next_item_flag_2:
                        continue

                    # for sugi_tuple in sugi_coordinates:
                    #     sugi_y0 = sugi_tuple[0]
                    #     sugi_y1 = sugi_tuple[1]
                    #     if int(mupdf_y0) == sugi_y0 and int(mupdf_y1) == sugi_y1:
                    #         continue_outer_loop = True
                    #         break

                    # if continue_outer_loop == True:
                    #     continue

                    redact_coords.append((x0, mupdf_y0, x1, mupdf_y1))
            
            page_area.append(redact_coords)


#黒塗り箇所を2ヶ所指定
#座標形式：(右上のx座標、右上のy座標、左下のx座標、左下のy座標)
##redact_coords = [(37,80,550,219),(37,220,289,242)]

# 長永　健介 様, x0=22.86, x1=132.66, y0=778.77, y1=804.49, width=109.80, height=25.73
#redact_coords = [(132, 804, 22, 776)]
##redact_coords = [(22, 131, 50, 50)]

#print(redact_coords)

# 黒塗りページ
#pages_to_redact = [0]

page_area = redact_coords_pages
pages_to_redact = range(len(page_area))


#redactor = Redactor(path,outpath,redact_coords)
#redactor.redaction(pages_to_redact)

# PDF開封
doc = fitz.open(path)
# 各ページをiterate
for i,page in enumerate(doc):
    if i in pages_to_redact:
        redact_coords = page_area[i]
        areas = [fitz.Rect(coord) for coord in redact_coords]
        [page.add_redact_annot(area, fill = (0, 0, 0)) for area in areas]
        # 黒塗りする
        page.apply_redactions()
# 新しいPDFとして保存
doc.save(outpath)
print("Successfully redacted")
