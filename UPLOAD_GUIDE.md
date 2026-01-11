# 📱 Codespacesでアップロードする手順

**スマホで5分で完了！**

---

## 📦 アップロードすべきファイル

### ✅ 最小構成（10ファイル）- これだけでOK

```
stock_pattern_matcher/
├── __init__.py
├── pattern_matcher.py
├── visualizer.py
├── config.py
├── data_loader.py
├── indicators.py
└── utils.py

setup.py
requirements.txt
README.md
```

### ⭐ 推奨追加（+2ファイル）

```
.gitignore
.env.example
```

---

## 🚀 アップロード手順

### STEP 1: ブラウザでGitHubを開く

**Safari（iPhone）または Chrome（Android）:**

```
https://github.com/kabuist001/stock-pattern-matcher
```

ログインする

---

### STEP 2: Codespacesを起動

**1. 「Code」ボタン（緑）をタップ**

**2. 「Codespaces」タブを選択**

**3. 「Create codespace on main」をタップ**

**4. 待つ（30秒〜1分）**

```
Setting up your codespace...
  ↓
✅ VS Code（オンライン版）が起動
```

---

### STEP 3: フォルダを作成

**左側のエクスプローラー（📁アイコン）で:**

**1. 空白部分を右クリック**

**2. 「New Folder」を選択**

**3. フォルダ名を入力:**
```
stock_pattern_matcher
```

**4. Enterキー**

---

### STEP 4: ファイルをアップロード

#### 4-1. stock_pattern_matcher フォルダ内

**1. 「stock_pattern_matcher」フォルダを右クリック**

**2. 「Upload...」を選択**

**3. 以下の7ファイルを選択:**

```
✅ __init__.py
✅ pattern_matcher.py
✅ visualizer.py
✅ config.py
✅ data_loader.py
✅ indicators.py
✅ utils.py
```

**4. アップロード完了を待つ**

---

#### 4-2. ルートフォルダ

**1. フォルダツリーの最上位（リポジトリ名）を右クリック**

**2. 「Upload...」を選択**

**3. 以下の3ファイルを選択:**

```
✅ setup.py
✅ requirements.txt
✅ README.md
```

**（推奨: さらに2ファイル追加）**
```
⭐ .gitignore
⭐ .env.example
```

---

### STEP 5: コミット

**1. 左側のソースコントロールアイコン（🌿）をタップ**

**2. 変更ファイルを確認**

```
Changes (10)  ← または (12)

M stock_pattern_matcher/__init__.py
M stock_pattern_matcher/pattern_matcher.py
M stock_pattern_matcher/visualizer.py
...
M setup.py
M requirements.txt
M README.md
```

**3. 上部のメッセージボックスに入力:**

```
Initial commit: Stock Pattern Matcher v1.0.0
```

**4. 「✓」（コミット）ボタンをタップ**

確認ダイアログが出たら「Yes」

---

### STEP 6: プッシュ

**1. 「Sync Changes」ボタンをタップ**

または

**「⬆」（プッシュ）ボタンをタップ**

**2. 確認ダイアログ → 「OK」**

**3. 完了を待つ（10秒）**

```
✅ Successfully synced
```

---

## ✅ 確認

### ブラウザで確認

**新しいタブで開く:**
```
https://github.com/kabuist001/stock-pattern-matcher
```

**表示されていればOK:**
- ✅ stock_pattern_matcher/ フォルダ
- ✅ setup.py
- ✅ requirements.txt  
- ✅ README.md
- ✅ .gitignore
- ✅ .env.example

---

## 🎉 完成！

これでColabから使えます：

```python
# Google Colabで実行
!pip install git+https://github.com/kabuist001/stock-pattern-matcher.git

from stock_pattern_matcher import PatternMatcher, Visualizer

print("✅ 成功！")
```

---

## 💡 Tips

### Tip1: 複数ファイルを一度に選択

**スマホのファイル選択画面で:**
- iPhone: ファイルをタップしながら「選択」ボタン
- Android: ファイルを長押しして複数選択

---

### Tip2: ファイルが見つからない場合

**事前にGoogle Drive / iCloudに保存:**

1. PCでダウンロードした `stock-pattern-matcher-repo`
2. Google Drive または iCloud にアップロード
3. スマホのGoogle Drive / iCloud アプリで確認
4. Codespaces の「Upload」から選択

---

### Tip3: アップロード順序

**どの順番でもOKですが、分かりやすい順:**

1. stock_pattern_matcher/ フォルダ作成
2. stock_pattern_matcher/ 内の7ファイル
3. ルートの3ファイル（必須）
4. ルートの2ファイル（推奨）

---

### Tip4: エラーが出たら

**「Git not found」エラー:**
→ ページを再読み込み

**「Upload failed」エラー:**
→ ファイルサイズ確認（大きすぎないか）
→ ファイル名に特殊文字がないか確認

---

## ❓ トラブルシューティング

### 問題1: Codespacesが起動しない

**解決:**
1. ブラウザのキャッシュをクリア
2. Safari / Chrome を最新版に更新
3. プライベートブラウジングモードで試す

---

### 問題2: Uploadボタンが見つからない

**解決:**
1. 横画面にする（見やすくなる）
2. フォルダ/ファイル名を右クリック
3. メニューから「Upload...」を探す

---

### 問題3: Syncボタンが表示されない

**原因:** まだコミットしていない

**解決:**
1. 先に「✓ Commit」をタップ
2. その後「Sync Changes」が表示される

---

### 問題4: ファイルがアップロードされない

**確認:**
1. ファイルサイズ（各1MB以下推奨）
2. ファイル名（英数字のみ推奨）
3. インターネット接続

---

## 🔄 ファイルを後から追加する場合

**同じ手順で:**

1. Codespaces を開く
2. 「Upload...」
3. 追加ファイルを選択
4. Commit → Sync

いつでも追加・削除できます！

---

## 📋 チェックリスト

アップロード前:
- [ ] stock-pattern-matcher-repo をダウンロード済み
- [ ] Google Drive / iCloud に保存済み（推奨）
- [ ] GitHubにログイン済み

アップロード中:
- [ ] Codespaces 起動
- [ ] stock_pattern_matcher/ フォルダ作成
- [ ] 7ファイルをアップロード
- [ ] 3〜5ファイルをルートにアップロード
- [ ] Commit
- [ ] Sync

アップロード後:
- [ ] GitHubでファイル確認
- [ ] Colabでテスト

全てチェックできたら完了です！🎉
