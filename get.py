# PythonでPDFのテキスト毎の座標を取得する #Python - Qiita
# https://qiita.com/76r6qo698/items/8d7f7a644385a18e21db

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams, LTTextContainer
from pdfminer.converter import PDFPageAggregator

def main():
    manager = PDFResourceManager()

    with open('statement_202402.pdf', 'rb') as input:
        with PDFPageAggregator(manager, laparams=LAParams()) as device:
            # PDFPageInterpreterオブジェクトの取得
            iprtr = PDFPageInterpreter(manager, device)
            # ページごとで処理を実行
            for page in PDFPage.get_pages(input):
                iprtr.process_page(page)
                # ページ内の各テキストのレイアウト
                layouts = device.get_result()
                for layout in layouts:
                    # 罫線などのオブジェクトが含まれているとエラーになるのを防ぐため
                    if isinstance(layout, LTTextContainer):
                        # 各ページの左下を原点としている
                        # x0: テキストの左端のx座標
                        # x1: テキストの右端のx座標
                        # y0: テキストの下端のy座標
                        # y1: テキストの上端のy座標
                        # width: テキストの幅(x1 - x0)
                        # height: テキストの高さ(y1 - y0)
                        print(f'{layout.get_text().strip()}, x0={layout.x0:.2f}, x1={layout.x1:.2f}, y0={layout.y0:.2f}, y1={layout.y1:.2f}, width={layout.width:.2f}, height={layout.height:.2f}')

if __name__ == '__main__':
    main()
