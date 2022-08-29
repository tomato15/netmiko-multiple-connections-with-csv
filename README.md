# netmiko-multiple-connections-with-csv


## 使い方
### 1. hostlist.csvに接続先の情報を書く
- hostの列はIPアドレスを記入します。名前解決できるならホスト名でも大丈夫なようです。

- usernameとpasswordは接続先にログインするための認証情報を記入します。
- secretはenable時に求められるパスワードです。Junosでは不要。
- カンマの後にスペースを入れないよう注意してください。' cisco'という文字列で認証しようとするため。

### 2. commandlist.csvに実行したいコマンドを書く
- ter len 0やenableは処理はnetmikoで実行してくれるので書く必要はないです。

### 3. pythonを実行する
- 二つのcsvファイルがあるディレクトリで、`python3 netmiko-multiple-connections.py`を実行する。

- 他のディレクトリから実行したい場合は、.pyの中のHOSTLISTとCOMMANDLISTでパスを書き換える必要があります。


# 応用例
- hostlist.csvやcommandlist.csvの列を増やして読みませるパラメータの拡張ができます。

- genie parserやtextfsmでパースして必要な情報の抽出や正誤の判定。genieでパースできるコマンドは[こちら](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers)で調べられます。
- 複数機器で同じconfigを変更することもできます。（netmikoにメソッドあり）
