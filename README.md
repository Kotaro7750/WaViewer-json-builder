# 話ビューアー用works.json生成ツール
[話ビューアー](https://github.com/Kotaro7750/WaViewer)が内部で使うworks.jsonを半自動で生成するためのツールです。

## 使い方
[JPdfBookmarks](https://flavianopetrocchi.blogspot.com/)というツールに依存しているので先にそちらをインストールして下さい。

あらかじめ、話ビューアーの`pdf`ディレクトリ以下のpdfファイルのそれぞれの「話」の先頭に"しおり"や"ブックマーク"と呼ばれるアノテーションをつけて下さい。

話ビューアーの`pdf`ディレクトリの絶対パスを`base_dir_path`とし、古いworks.jsonへの絶対パスを`input_json_path`とします。まだworks.jsonがない場合には指定しなくて構いません。
デフォルトでは結果は標準出力に出されるので、リダイレクトで適切なファイルに保存して下さい。

```python
python3 ./json-builder.py base_dir_path input_json_path > new_json_path
```

このようにすることで以前のworks.jsonにあった「話」同士のつながりを維持したまま新たにworks.jsonを生成することができます。
なお、新しく追加された「話」同士のつながりは当然ながら考慮することができません。手動で追加して下さい。
