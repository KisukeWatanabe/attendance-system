# 👨‍💼 勤怠管理Webアプリ (仮名: Attendance System)

## 🌟 プロジェクト概要

自営業のお店で実際に使用するために開発した勤怠管理Webアプリです。出勤、退勤、休憩、復帰をボタン一つで簡単に打刻でき、月ごとの給与計算も自動化しました。

---

## 🔧 使用技術

- Python (Flask)
- HTML / CSS / JavaScript
- SQLite / SQLAlchemy
- Render (本番環境ホスティング)

---

## ✨ 主な機能

## ✨ 主な機能

**【一般従業員向け機能】**
- 出勤 / 退勤 / 休憩 / 復帰の打刻管理
---

**【管理者専用機能】**
- 打刻データの訂正機能（ミス打刻の修正）
- 作業時間・休憩時間を考慮した給与自動計算
- 出退勤履歴の一覧表示
- 月ごとの出勤日数・労働時間・給与合計の集計表示

---

## 🔍 セットアップ手順

1. リポジトリをクローン
2. 仮想環境(バーチャル環境)を作成
3. 必要なパッケージをインストール
4. アプリを起動

```bash
# クローン
git clone https://github.com/KisukeWatanabe/attendance-system.git
cd attendance-system

# 仮想環境作成
python -m venv venv
source venv/bin/activate   # Windowsは venv\Scripts\activate

# パッケージインストール
pip install -r requirements.txt

# Flask起動
flask run
```

---

## 🌐 本番環境URL (Render)

(実際にデプロイ完了後に貼り付け)

```
https://your-app.onrender.com
```

---

## 📷 スクリーンショット

(打刻画面や給与計算画面などを貼り付けると更に体験値UP)

---

## 💡 作成者
