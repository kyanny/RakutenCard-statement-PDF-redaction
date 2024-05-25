# 楽天カード明細黒塗り君

楽天カードの利用明細 PDF を黒塗りする Python スクリプト

指定した明細だけ黒塗りせず残せるので、経費精算のためにクレジットカードの明細を提出するとき便利です

## Prerequisites

- Python3

## Installation

```
git clone https://github.com/kyanny/RakutenCard-statement-PDF-redaction
cd RakutenCard-statement-PDF-redaction
python3 -m venv venv
. ./venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

1. [楽天e-NAVI](https://www.rakuten-card.co.jp/e-navi/)にログインして[ご利用明細の印刷・ダウンロード](https://www.rakuten-card.co.jp/e-navi/members/statement/download-list.xhtml)から PDF をダウンロードする
2. ダウンロードした PDF ファイルをこのディレクトリに置く
3. `redact.py` を実行する

    ```
    python3 redact.py statement_YYYYMM.pdf
    ```

4. 黒塗り済みの `statement_YYYYMM_redacted.pdf` が作られる
