

import fitz
 
class Redactor:
 
    def __init__(self, path,outpath,redact_coords):
        self.path = path
        self.outpath = outpath
        self.redact_coords = redact_coords
 
    def redaction(self,page_nums):
        # PDF開封
        doc = fitz.open(self.path)
        # 各ページをiterate
        for i,page in enumerate(doc):
            if i in page_nums:
                areas = [fitz.Rect(coord) for coord in self.redact_coords]
                [page.add_redact_annot(area, fill = (0, 0, 0)) for area in areas]
                # 黒塗りする
                page.apply_redactions()    
        # 新しいPDFとして保存
        doc.save(self.outpath)
        print("Successfully redacted")


# 入力PDF
path = 'statement_202402.pdf'
# 出力PDF
outpath = 'out.pdf'

#黒塗り箇所を2ヶ所指定
#座標形式：(右上のx座標、右上のy座標、左下のx座標、左下のy座標)
redact_coords = [(37,80,550,219),(37,220,289,242)]

# 長永　健介 様, x0=22.86, x1=132.66, y0=778.77, y1=804.49, width=109.80, height=25.73
#redact_coords = [(132, 804, 22, 776)]
redact_coords = [(22, 131, 50, 50)]


# 黒塗りページ
pages_to_redact = [0]

redactor = Redactor(path,outpath,redact_coords)
redactor.redaction(pages_to_redact)

