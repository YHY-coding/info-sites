#!/usr/bin/env python3
"""3サイトを docs/ に静的生成する。 使い方: python3 build.py  (BASE_URL=https://xxx を付けると sitemap も出力)"""
import os, shutil, html
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
TODAY = date.today().isoformat()
written = []  # sitemap 用

CSS = """
:root{--bg:#fff;--fg:#1c2330;--sub:#5b6577;--line:#e3e7ee;--acc:#1d5fd1;--card:#f6f8fb}
@media(prefers-color-scheme:dark){:root{--bg:#10151d;--fg:#e8ecf3;--sub:#9aa5b8;--line:#243044;--acc:#6ea2ff;--card:#171e2a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.8 -apple-system,"Hiragino Sans","Noto Sans JP",sans-serif}
header,main,footer{max-width:760px;margin:0 auto;padding:0 16px}
header{padding-top:16px;padding-bottom:8px;border-bottom:1px solid var(--line)}
header a.logo{font-weight:700;color:var(--fg);text-decoration:none;font-size:1.1rem}
nav a{margin-right:14px;font-size:.9rem;color:var(--sub);text-decoration:none}
main{padding-top:20px;padding-bottom:32px}h1{font-size:1.5rem;line-height:1.4}h2{font-size:1.2rem;margin-top:2rem;border-left:4px solid var(--acc);padding-left:10px}
a{color:var(--acc)}table{border-collapse:collapse;width:100%;font-size:.95rem}td,th{border:1px solid var(--line);padding:6px 10px;text-align:left}th{background:var(--card)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:14px 0}
.note{font-size:.85rem;color:var(--sub)}input,select,button{font:inherit;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg)}
button{background:var(--acc);color:#fff;border:0;cursor:pointer}.big{font-size:1.6rem;font-weight:700}
ul.links{padding-left:1.2rem}footer{border-top:1px solid var(--line);padding-top:14px;padding-bottom:30px;font-size:.82rem;color:var(--sub)}
"""


def esc(s):
    return html.escape(s, quote=True)


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    if path.endswith(".html"):
        written.append(path)


def page(site, path, title, desc, body, nav, disclaimer):
    depth = path.count("/")
    up = "../" * depth
    navhtml = "".join(f'<a href="{up}{u}">{esc(t)}</a>' for t, u in nav)
    canon = f'<link rel="canonical" href="{BASE_URL}/{path}">' if BASE_URL else ""
    doc = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">{canon}
<style>{CSS}</style></head><body>
<header><a class="logo" href="{up}{site['home']}">{esc(site['name'])}</a><nav>{navhtml}</nav></header>
<main>{body}</main>
<footer><p>{disclaimer}</p><p>最終更新: {TODAY}</p></footer></body></html>"""
    write(path, doc)


# ============================================================ サイト1: 手取り計算機
def calc_net(gross):
    """独身・扶養なし・協会けんぽ平均料率の概算 (令和7〜8年分の所得税制を前提)。"""
    g = gross
    if g <= 1_900_000: kd = 650_000
    elif g <= 3_600_000: kd = g * 0.3 + 80_000
    elif g <= 6_600_000: kd = g * 0.2 + 440_000
    elif g <= 8_500_000: kd = g * 0.1 + 1_100_000
    else: kd = 1_950_000
    kd = min(kd, g)
    shotoku = g - kd
    m = g / 12
    kenpo = min(m, 1_390_000) * 0.05 * 12
    nenkin = min(m, 650_000) * 0.0915 * 12
    koyo = g * 0.0055
    sha = kenpo + nenkin + koyo
    if shotoku <= 1_320_000: kiso = 950_000
    elif shotoku <= 3_360_000: kiso = 880_000
    elif shotoku <= 4_890_000: kiso = 680_000
    elif shotoku <= 6_550_000: kiso = 630_000
    else: kiso = 580_000
    t = max(0, shotoku - sha - kiso) // 1000 * 1000
    for lim, rate, ded in [(1_950_000, .05, 0), (3_300_000, .10, 97_500), (6_950_000, .20, 427_500),
                           (9_000_000, .23, 636_000), (18_000_000, .33, 1_536_000),
                           (40_000_000, .40, 2_796_000), (10**12, .45, 4_796_000)]:
        if t <= lim:
            tax = t * rate - ded
            break
    shotokuzei = tax * 1.021
    jt = max(0, shotoku - sha - 430_000) // 1000 * 1000
    jumin = jt * 0.10 + 5000
    net = g - sha - shotokuzei - jumin
    return dict(gross=g, sha=sha, kenpo=kenpo, nenkin=nenkin, koyo=koyo,
                shotokuzei=shotokuzei, jumin=jumin, net=net)


def yen(x):
    return f"{int(round(x)):,}円"


def man(x):
    return f"{x/10000:,.1f}万円"


CALC_JS = """
function calcNet(g){var kd;if(g<=1900000)kd=650000;else if(g<=3600000)kd=g*0.3+80000;else if(g<=6600000)kd=g*0.2+440000;else if(g<=8500000)kd=g*0.1+1100000;else kd=1950000;kd=Math.min(kd,g);
var s=g-kd,m=g/12,kenpo=Math.min(m,1390000)*0.05*12,nen=Math.min(m,650000)*0.0915*12,koyo=g*0.0055,sha=kenpo+nen+koyo,kiso;
if(s<=1320000)kiso=950000;else if(s<=3360000)kiso=880000;else if(s<=4890000)kiso=680000;else if(s<=6550000)kiso=630000;else kiso=580000;
var t=Math.floor(Math.max(0,s-sha-kiso)/1000)*1000,B=[[1950000,.05,0],[3300000,.10,97500],[6950000,.20,427500],[9000000,.23,636000],[18000000,.33,1536000],[40000000,.40,2796000],[1e12,.45,4796000]],tax=0;
for(var i=0;i<B.length;i++){if(t<=B[i][0]){tax=t*B[i][1]-B[i][2];break}}
var st=tax*1.021,jt=Math.floor(Math.max(0,s-sha-430000)/1000)*1000,jm=jt*0.10+5000;return{sha:sha,st:st,jm:jm,net:g-sha-st-jm}}
function fmt(x){return Math.round(x).toLocaleString('ja-JP')+'円'}
function run(){var g=parseFloat(document.getElementById('g').value)*10000;if(!(g>0)){return}
var r=calcNet(g);document.getElementById('out').innerHTML='<p class="big">手取り 年'+fmt(r.net)+'(月'+fmt(r.net/12)+')</p><table><tr><th>社会保険料</th><td>'+fmt(r.sha)+'</td></tr><tr><th>所得税(復興税込)</th><td>'+fmt(r.st)+'</td></tr><tr><th>住民税</th><td>'+fmt(r.jm)+'</td></tr><tr><th>手取り率</th><td>'+(r.net/g*100).toFixed(1)+'%</td></tr></table>'}
document.getElementById('btn').onclick=run;document.getElementById('g').addEventListener('keydown',function(e){if(e.key==='Enter')run()});run();
"""

S1 = dict(name="手取り・税金かんたん計算", home="index.html")
S1_NAV = [("手取り計算", "index.html"), ("年収別一覧", "nenshu/index.html"), ("副業の税金", "fukugyo.html")]
S1_DISC = ("本サイトの金額は、独身・扶養なし・協会けんぽ平均料率・賞与なしを仮定した<strong>概算</strong>です。"
           "実際の金額は勤務先・地域・家族構成で変わります。正確な額は給与明細や税務署・自治体で確認してください。")
NENSHU = list(range(200, 1000, 50)) + list(range(1000, 2100, 100))


def build_site1():
    d = "tekadori/"
    body = ("<h1>年収から手取りを計算</h1><p>年収(万円)を入れると、社会保険料・税金を引いた手取りの目安がわかります。</p>"
            '<div class="card"><label>年収(万円) <input id="g" type="number" value="400" min="1" step="10"></label> '
            '<button id="btn">計算する</button></div><div id="out" class="card"></div>'
            "<h2>計算の前提</h2><ul><li>給与のみ、独身、扶養なし、賞与は月給に均等割り</li>"
            "<li>健康保険5.0%、厚生年金9.15%、雇用保険0.55%(いずれも本人負担の概算)</li>"
            "<li>所得税は令和7年度税制改正後の給与所得控除・基礎控除を使用、復興特別所得税2.1%を加算</li>"
            "<li>住民税は所得割10%+均等割5,000円(自治体で差があります)</li></ul>"
            '<h2>年収別の手取り</h2><p><a href="nenshu/index.html">年収200万円〜2,000万円の手取り一覧を見る</a></p>'
            f"<script>{CALC_JS}</script>")
    page(S1, d + "index.html", "年収から手取りを計算|手取り・税金かんたん計算",
         "年収を入力するだけで、社会保険料・所得税・住民税を引いた手取り額の目安を計算できます。", body, S1_NAV, S1_DISC)
    rows = ""
    for n in NENSHU:
        r = calc_net(n * 10000)
        rows += f'<tr><td><a href="{n}.html">{n:,}万円</a></td><td>{man(r["net"])}</td><td>{yen(r["net"]/12)}</td><td>{r["net"]/r["gross"]*100:.1f}%</td></tr>'
    page(S1, d + "nenshu/index.html", "年収別 手取り一覧(200万〜2,000万円)",
         "年収200万円から2,000万円までの手取り額・月額・手取り率を一覧で確認できます。",
         "<h1>年収別 手取り一覧</h1><table><tr><th>年収</th><th>手取り(年)</th><th>手取り(月)</th><th>手取り率</th></tr>"
         + rows + "</table>", S1_NAV, S1_DISC)
    for i, n in enumerate(NENSHU):
        r = calc_net(n * 10000)
        near = [x for x in NENSHU if x != n][max(0, i - 3):max(0, i - 3) + 6]
        links = "".join(f'<li><a href="{x}.html">年収{x:,}万円の手取り</a></li>' for x in near)
        body = (f"<h1>年収{n:,}万円の手取りは約{man(r['net'])}</h1>"
                f"<p>年収{n:,}万円(独身・扶養なし・賞与なしの場合)の手取りは<strong>年{yen(r['net'])}、月{yen(r['net']/12)}</strong>、"
                f"手取り率は約{r['net']/r['gross']*100:.1f}%です。</p>"
                f"<h2>内訳</h2><table><tr><th>項目</th><th>年額</th></tr>"
                f"<tr><td>額面年収</td><td>{yen(r['gross'])}</td></tr>"
                f"<tr><td>健康保険料</td><td>{yen(r['kenpo'])}</td></tr>"
                f"<tr><td>厚生年金保険料</td><td>{yen(r['nenkin'])}</td></tr>"
                f"<tr><td>雇用保険料</td><td>{yen(r['koyo'])}</td></tr>"
                f"<tr><td>所得税(復興税込)</td><td>{yen(r['shotokuzei'])}</td></tr>"
                f"<tr><td>住民税</td><td>{yen(r['jumin'])}</td></tr>"
                f"<tr><th>手取り</th><th>{yen(r['net'])}</th></tr></table>"
                f"<p class='note'>住民税は前年の所得に対して翌年課税されるため、実際の月々の引かれ方とは時期がずれます。</p>"
                f"<h2>ほかの年収を見る</h2><ul class='links'>{links}</ul>"
                f'<p><a href="index.html">年収別一覧へ</a> / <a href="../index.html">自分の年収で計算する</a></p>')
        page(S1, d + f"nenshu/{n}.html", f"年収{n:,}万円の手取りは約{man(r['net'])}(月{yen(r['net']/12)})",
             f"年収{n:,}万円の手取りは年約{man(r['net'])}、月約{yen(r['net']/12)}。社会保険料・所得税・住民税の内訳つき。",
             body, S1_NAV, S1_DISC)
    body = """<h1>副業の税金|いくらから確定申告が必要?</h1>
<p>会社員が副業で収入を得た場合の基本ルールをまとめます。</p>
<h2>確定申告が必要になる目安</h2>
<ul><li>給与以外の<strong>所得</strong>(収入−必要経費)が年<strong>20万円を超える</strong>と、所得税の確定申告が必要です。</li>
<li>20万円以下でも、<strong>住民税の申告</strong>は別に必要になることがあります。お住まいの自治体の案内を確認してください。</li>
<li>「収入」ではなく「所得」で判断します。経費がある場合は差し引けます。</li></ul>
<h2>副業が会社に知られにくくするには</h2>
<p>確定申告書の「住民税の徴収方法」で「自分で納付(普通徴収)」を選ぶ方法がありますが、自治体の運用によっては対応できない場合があります。会社の就業規則で副業が認められているかの確認が先です。</p>
<h2>経費にできるものの例</h2>
<ul><li>サーバー・ドメイン代、ソフトウェア利用料</li><li>仕事に使った通信費・消耗品の按分</li><li>書籍・教材費(業務に関係するもの)</li></ul>
<p class="note">制度は変わります。申告の判断は国税庁の最新情報か、税務署・税理士に確認してください。</p>
<p><a href="index.html">年収から手取りを計算する</a></p>"""
    page(S1, d + "fukugyo.html", "副業の税金|いくらから確定申告が必要?", "会社員の副業で確定申告が必要になる目安(所得20万円超)と、住民税・経費の基本をわかりやすく解説。",
         body, S1_NAV, S1_DISC)


# ============================================================ サイト2: IT資格ノート
S2 = dict(name="IT資格 学習ノート", home="index.html")
S2_NAV = [("ITパスポート", "itpass/index.html"), ("AZ-104", "az104/index.html")]
S2_DISC = ("本サイトは非公式の学習ノートです。試験内容・出題範囲は変更されるため、必ず公式の最新情報を確認してください。"
           "各社の商標は各権利者に帰属します。")

ITPASS = [
    ("exam", "ITパスポート試験の概要と合格の目安",
     "<p>ITパスポートは、ITを利用するすべての社会人・学生に必要な基礎知識を問う国家試験です。</p>"
     "<ul><li>形式: CBT方式(パソコンで受験)、100問、試験時間120分</li>"
     "<li>分野: ストラテジ系(経営全般)、マネジメント系(プロジェクト・サービス管理)、テクノロジ系(基礎理論・技術)</li>"
     "<li>合格基準: 総合評価点600点以上(1,000点満点)かつ、各分野別評価点が300点以上</li>"
     "<li>受験は通年で可能。詳細は公式サイトで確認してください</li></ul>"
     "<p>範囲が広いため、全分野を浅く押さえつつ、分野別の足切りを避けることが大切です。</p>"),
    ("security-3", "情報セキュリティの3要素(機密性・完全性・可用性)",
     "<p>情報セキュリティの基本は、次の3つを守ることです。</p>"
     "<table><tr><th>要素</th><th>意味</th><th>脅かす例</th></tr>"
     "<tr><td>機密性</td><td>許可された人だけが情報にアクセスできる</td><td>情報漏えい、盗み見</td></tr>"
     "<tr><td>完全性</td><td>情報が正確で改ざんされていない</td><td>データ改ざん</td></tr>"
     "<tr><td>可用性</td><td>必要なときに情報を使える</td><td>システム停止、DoS攻撃</td></tr></table>"
     "<p>試験では「この対策はどの要素を守るものか」という形で出題されやすい項目です。</p>"),
    ("malware", "ランサムウェア・フィッシングなど主な攻撃手法",
     "<ul><li><strong>ランサムウェア</strong>: データを暗号化して使えなくし、元に戻すことと引き換えに金銭を要求する</li>"
     "<li><strong>フィッシング</strong>: 本物そっくりの偽サイト・偽メールでIDやパスワードを盗む</li>"
     "<li><strong>標的型攻撃</strong>: 特定の組織を狙い、業務を装ったメールなどで侵入する</li>"
     "<li><strong>DoS攻撃</strong>: 大量のアクセスを送りつけてサービスを止める</li>"
     "<li><strong>SQLインジェクション</strong>: 入力欄から不正なSQL文を送り、データベースを不正操作する</li></ul>"),
    ("auth", "認証方式と多要素認証",
     "<p>認証の要素は大きく3種類です。</p>"
     "<ul><li>知識情報: パスワード、PIN</li><li>所持情報: スマホ、ICカード、ワンタイムパスワード</li><li>生体情報: 指紋、顔</li></ul>"
     "<p><strong>多要素認証</strong>は、種類の異なる要素を2つ以上組み合わせます(例: パスワード+スマホのワンタイムコード)。"
     "同じ種類の要素(パスワード2つ)を重ねても多要素認証にはなりません。</p>"),
    ("crypto", "共通鍵暗号と公開鍵暗号",
     "<table><tr><th></th><th>共通鍵暗号</th><th>公開鍵暗号</th></tr>"
     "<tr><td>鍵</td><td>暗号化と復号で同じ鍵</td><td>公開鍵と秘密鍵のペア</td></tr>"
     "<tr><td>速度</td><td>速い</td><td>遅い</td></tr>"
     "<tr><td>課題</td><td>鍵を安全に渡す必要がある</td><td>鍵の管理・配布が楽</td></tr></table>"
     "<p>公開鍵暗号では、<strong>相手の公開鍵で暗号化し、相手の秘密鍵で復号</strong>します。デジタル署名は逆で、自分の秘密鍵で署名し、公開鍵で検証します。</p>"),
    ("cloud", "クラウドのIaaS・PaaS・SaaSの違い",
     "<p>クラウド事業者がどこまで管理するかの違いです。</p>"
     "<table><tr><th>種類</th><th>提供されるもの</th><th>例</th></tr>"
     "<tr><td>IaaS</td><td>サーバー・ネットワークなどの基盤</td><td>仮想マシン</td></tr>"
     "<tr><td>PaaS</td><td>アプリを動かす実行環境</td><td>アプリのホスティング基盤</td></tr>"
     "<tr><td>SaaS</td><td>完成したアプリケーション</td><td>メール、オンライン会議</td></tr></table>"
     "<p>IaaS→PaaS→SaaSの順に、利用者が管理する範囲が小さくなります。</p>"),
    ("network", "IPアドレスとDNS",
     "<ul><li><strong>IPアドレス</strong>: ネットワーク上の機器を識別する番号(例: IPv4は32ビット、IPv6は128ビット)</li>"
     "<li><strong>DNS</strong>: ドメイン名(例: example.com)をIPアドレスに変換する仕組み</li>"
     "<li><strong>DHCP</strong>: 機器にIPアドレスなどを自動で割り当てる仕組み</li>"
     "<li><strong>プライベートIPアドレス</strong>: 社内ネットワークなどで使う、インターネットに直接出ないアドレス</li></ul>"),
    ("binary", "2進数と16進数の基本",
     "<p>コンピュータは0と1の2進数で情報を扱います。</p>"
     "<ul><li>2進数の1011は、8+0+2+1=<strong>11</strong>(10進数)</li>"
     "<li>16進数は0〜9とA〜F(A=10、F=15)で表す。16進数のFFは15×16+15=<strong>255</strong></li>"
     "<li>1バイト=8ビット。8ビットで表せる値は0〜255の256通り</li></ul>"),
    ("backup", "バックアップとRAID",
     "<ul><li><strong>RAID0</strong>: 複数ディスクに分散して書き込み、高速化。1台壊れるとデータを失う</li>"
     "<li><strong>RAID1</strong>: 同じデータを2台に書き込む(ミラーリング)。1台壊れても継続できる</li>"
     "<li><strong>RAID5</strong>: データとパリティを分散。1台の故障までは復旧できる</li></ul>"
     "<p>バックアップの種類は、<strong>フルバックアップ</strong>(全部)、<strong>差分</strong>(前回のフル以降の変更分)、"
     "<strong>増分</strong>(前回のバックアップ以降の変更分)があります。復元は増分が最も手間がかかります。</p>"),
]

AZ = [
    ("exam", "AZ-104(Azure Administrator)試験の概要",
     "<p>AZ-104は、Azureの管理者向け認定資格(Microsoft Certified: Azure Administrator Associate)の試験です。</p>"
     "<p>出題範囲は大きく次の5領域で、配点の割合は改訂のたびに変わります。必ずMicrosoft Learnの最新の「試験の学習ガイド」を確認してください。</p>"
     "<ul><li>Azure IDとガバナンスの管理</li><li>ストレージの実装と管理</li><li>Azureコンピューティングリソースのデプロイと管理</li>"
     "<li>仮想ネットワークの実装と管理</li><li>Azureリソースの監視とバックアップ</li></ul>"
     "<p>実機での操作経験が問われるため、無料アカウントや無料枠で実際に触って学ぶのが近道です。操作後は課金を避けるため、リソースを必ず削除してください。</p>"),
    ("entra-rbac", "Microsoft Entra IDとAzure RBAC",
     "<ul><li><strong>Microsoft Entra ID</strong>(旧Azure AD): ユーザー・グループ・アプリのIDを管理するクラウドのID基盤</li>"
     "<li><strong>Azure RBAC</strong>: リソースに対する操作権限を「ロール」で付与する仕組み。スコープは管理グループ→サブスクリプション→リソースグループ→リソースの階層で、権限は下位に継承される</li>"
     "<li>代表的な組み込みロール: 所有者(Owner)、共同作成者(Contributor)、閲覧者(Reader)</li></ul>"
     "<p>混同しやすい点: Entra IDのロール(ディレクトリ操作用)と、Azure RBACのロール(Azureリソース操作用)は<strong>別物</strong>です。</p>"),
    ("governance", "Azure Policy・リソースロック・タグ",
     "<table><tr><th>機能</th><th>役割</th></tr>"
     "<tr><td>Azure Policy</td><td>リソースが組織のルールに沿うかを評価・強制する(例: 許可リージョンの制限)</td></tr>"
     "<tr><td>リソースロック</td><td>誤削除・誤変更を防ぐ。CanNotDelete(削除不可)とReadOnly(読み取り専用)</td></tr>"
     "<tr><td>タグ</td><td>リソースに名前と値のラベルを付けて整理・コスト集計に使う</td></tr></table>"
     "<p>Azure Policyは「何をしてよいか(何を禁止するか)」、RBACは「誰が操作してよいか」を決める点が違いです。</p>"),
    ("storage", "ストレージアカウントの冗長性とアクセス層",
     "<p>データのコピーの持ち方で冗長性が決まります。</p>"
     "<table><tr><th>種類</th><th>概要</th></tr>"
     "<tr><td>LRS</td><td>1つのデータセンター内で3コピー</td></tr>"
     "<tr><td>ZRS</td><td>同一リージョン内の3つの可用性ゾーンにコピー</td></tr>"
     "<tr><td>GRS</td><td>LRSに加え、遠く離れたペアリージョンにも非同期でコピー</td></tr>"
     "<tr><td>GZRS</td><td>ZRS+ペアリージョンへのコピー</td></tr></table>"
     "<p>Blobのアクセス層には、ホット、クール、コールド、アーカイブがあります。アクセス頻度が低いほど保管料は安く、取り出しコストや待ち時間が増えます(アーカイブは取り出しに「リハイドレート」が必要)。</p>"),
    ("compute", "仮想マシンの可用性とスケールセット",
     "<ul><li><strong>可用性セット</strong>: 同一データセンター内で障害ドメイン・更新ドメインに分散して配置する</li>"
     "<li><strong>可用性ゾーン</strong>: 物理的に分かれたゾーンにVMを分散し、データセンター単位の障害に備える</li>"
     "<li><strong>仮想マシンスケールセット(VMSS)</strong>: 同じVMを負荷に応じて自動で増減させる</li></ul>"
     "<p>可用性ゾーンのほうが可用性セットより広い範囲の障害に耐えられます。</p>"),
    ("vnet", "仮想ネットワーク・NSG・ピアリング",
     "<ul><li><strong>仮想ネットワーク(VNet)</strong>: Azure上のプライベートなネットワーク。サブネットに分割して使う</li>"
     "<li><strong>NSG(ネットワークセキュリティグループ)</strong>: 受信/送信の通信を、優先度付きの規則で許可・拒否する。サブネットまたはNICに関連付け</li>"
     "<li><strong>VNetピアリング</strong>: 2つのVNetを接続し、プライベートIPで通信可能にする。推移的ではない(AとB、BとCをつないでもAとCは通信できない)</li></ul>"
     "<p>NSGの規則は優先度の数字が小さいほど先に評価されます。</p>"),
    ("monitor", "Azure MonitorとAzure Backup",
     "<ul><li><strong>Azure Monitor</strong>: メトリックとログを収集・分析し、アラートを出す監視基盤。ログはLog Analyticsワークスペースで、KQLというクエリ言語で検索する</li>"
     "<li><strong>Azure Backup</strong>: Recovery Servicesコンテナーを使って、VMなどをバックアップ・復元する</li></ul>"
     "<p>バックアップの保管先コンテナーと対象リソースのリージョンの関係(同一リージョンが原則)は、試験で問われやすい点です。</p>"),
]


def build_site2():
    d = "it-shikaku/"
    for sec, items, label in (("itpass", ITPASS, "ITパスポート"), ("az104", AZ, "AZ-104")):
        lis = "".join(f'<li><a href="{s}.html">{esc(t)}</a></li>' for s, t, _ in items)
        page(S2, d + f"{sec}/index.html", f"{label} 学習ノート一覧", f"{label}の要点を項目別にまとめた学習ノートの一覧です。",
             f"<h1>{label} 学習ノート</h1><ul class='links'>{lis}</ul>", S2_NAV, S2_DISC)
        for i, (slug, title, bodyhtml) in enumerate(items):
            nxt = items[(i + 1) % len(items)]
            page(S2, d + f"{sec}/{slug}.html", f"{title}|{label}", f"{label}対策: {title}の要点を整理。",
                 f"<h1>{esc(title)}</h1>{bodyhtml}<h2>次に読む</h2><p><a href='{nxt[0]}.html'>{esc(nxt[1])}</a> / <a href='index.html'>{label}の一覧へ</a></p>",
                 S2_NAV, S2_DISC)
    page(S2, d + "index.html", "IT資格 学習ノート|ITパスポート・AZ-104",
         "ITパスポートとAZ-104の要点を、短く読める形でまとめた非公式の学習ノート。",
         "<h1>IT資格 学習ノート</h1><p>ITパスポートとAZ-104(Azure Administrator)の要点を、1ページ1テーマでまとめています。</p>"
         "<div class='card'><a href='itpass/index.html'><strong>ITパスポート</strong></a><br>基礎用語・セキュリティ・ネットワーク</div>"
         "<div class='card'><a href='az104/index.html'><strong>AZ-104</strong></a><br>ID・ストレージ・VM・ネットワーク・監視</div>",
         S2_NAV, S2_DISC)


# ============================================================ サイト3: 補助金ガイド
S3 = dict(name="補助金・助成金ガイド", home="index.html")
S3_NAV = [("基礎知識", "basics.html"), ("主な制度", "programs.html"), ("申請の流れ", "flow.html")]
S3_DISC = ("本サイトは情報提供を目的とした非公式のガイドです。補助額・補助率・締切・要件は公募回ごとに変わります。"
           "申請前に必ず公式の公募要領をご確認ください。")


def build_site3():
    d = "hojokin/"
    page(S3, d + "index.html", "補助金・助成金ガイド|はじめての申請準備",
         "個人事業主・中小企業向けに、補助金と助成金の違い、主な制度、申請の流れをやさしく整理したガイド。",
         "<h1>補助金・助成金ガイド</h1><p>個人事業主・中小企業が、補助金・助成金を調べて申請するまでの基本をまとめています。</p>"
         "<div class='card'><a href='basics.html'><strong>補助金と助成金の違い</strong></a></div>"
         "<div class='card'><a href='programs.html'><strong>主な補助金・助成金の種類と探し方</strong></a></div>"
         "<div class='card'><a href='flow.html'><strong>申請の流れと準備するもの</strong></a></div>"
         "<div class='card'><a href='mistakes.html'><strong>よくある失敗と注意点</strong></a></div>", S3_NAV, S3_DISC)
    page(S3, d + "basics.html", "補助金と助成金の違い|何がどう違う?", "補助金と助成金の違いを、採択・受給の仕組み、窓口、公募期間の観点で整理。",
         "<h1>補助金と助成金の違い</h1>"
         "<table><tr><th></th><th>補助金</th><th>助成金</th></tr>"
         "<tr><td>主な窓口</td><td>経済産業省系・自治体など</td><td>厚生労働省系(雇用関係)など</td></tr>"
         "<tr><td>選ばれ方</td><td>審査があり、採択された人だけ</td><td>要件を満たせば原則受給できる</td></tr>"
         "<tr><td>募集</td><td>期間・予算枠が限られる</td><td>通年のものも多い</td></tr>"
         "<tr><td>難しさ</td><td>事業計画書の質が結果に影響する</td><td>要件・書類の不備に注意</td></tr></table>"
         "<p>どちらも<strong>原則として後払い</strong>です。先に自分で費用を支払い、実績を報告して審査を受けたあとに入金されます。つなぎ資金の手当てが必要です。</p>"
         "<p><a href='programs.html'>主な制度を見る</a></p>", S3_NAV, S3_DISC)
    page(S3, d + "programs.html", "主な補助金・助成金の種類と探し方", "代表的な補助金の種類と、公募情報を探せる公式サイトをまとめました。",
         "<h1>主な補助金・助成金の種類と探し方</h1>"
         "<p>制度名や上限額は年度で変わるため、ここでは<strong>種類と探し方</strong>を紹介します。金額・締切は必ず公式サイトで確認してください。</p>"
         "<h2>代表的な種類</h2><ul>"
         "<li><strong>設備投資・新製品開発向け</strong>: 「ものづくり補助金」など</li>"
         "<li><strong>販路開拓・小規模事業者向け</strong>: 「小規模事業者持続化補助金」など</li>"
         "<li><strong>ITツール導入向け</strong>: 「IT導入補助金」の系統の制度</li>"
         "<li><strong>省力化・自動化機器向け</strong>: 省力化投資に関する補助金</li>"
         "<li><strong>雇用・人材育成向け</strong>: 厚生労働省系の各種助成金</li>"
         "<li><strong>自治体独自</strong>: 都道府県・市区町村の創業支援、家賃補助など</li></ul>"
         "<h2>探すときの公式サイト</h2><ul class='links'>"
         "<li><a href='https://www.jgrants-portal.go.jp/' rel='noopener'>Jグランツ(補助金申請システム・公募情報)</a></li>"
         "<li><a href='https://j-net21.smrj.go.jp/' rel='noopener'>J-Net21(中小企業基盤整備機構の支援情報)</a></li>"
         "<li><a href='https://portal.monodukuri-hojo.jp/' rel='noopener'>ものづくり補助金 総合サイト</a></li>"
         "<li><a href='https://it-shien.smrj.go.jp/' rel='noopener'>IT導入補助金</a></li></ul>"
         "<p>自治体の制度は、お住まいの自治体のホームページや商工会議所・商工会の窓口でも案内されています。</p>", S3_NAV, S3_DISC)
    page(S3, d + "flow.html", "補助金の申請の流れと準備するもの", "補助金の公募確認から申請、採択、事業実施、報告、入金までの流れと、事前準備をまとめました。",
         "<h1>申請の流れと準備するもの</h1><ol>"
         "<li><strong>公募情報の確認</strong>: 対象者・対象経費・締切を公募要領で確認</li>"
         "<li><strong>電子申請の準備</strong>: 多くの制度で<strong>GビズIDプライム</strong>のアカウントが必要。発行に時間がかかるため早めに申請</li>"
         "<li><strong>事業計画書の作成</strong>: 何に使い、どんな効果を見込むかを具体的に書く</li>"
         "<li><strong>申請・審査</strong>: 期限内に電子申請。審査結果(採択/不採択)を待つ</li>"
         "<li><strong>交付決定後に事業を実施</strong>: 原則、交付決定前の発注・支払いは対象外</li>"
         "<li><strong>実績報告・入金</strong>: 領収書など証拠書類をそろえて報告し、確定後に入金</li></ol>"
         "<h2>準備しておくとよいもの</h2><ul><li>決算書または確定申告書の控え</li><li>事業内容を説明できる資料</li><li>見積書(対象経費の根拠)</li><li>GビズIDの取得</li></ul>", S3_NAV, S3_DISC)
    page(S3, d + "mistakes.html", "補助金申請のよくある失敗と注意点", "交付決定前の発注、後払いの資金繰り、対象経費の誤解など、補助金申請でよくある失敗を整理。",
         "<h1>よくある失敗と注意点</h1><ul>"
         "<li><strong>交付決定前に発注・支払いをしてしまう</strong>: 補助対象外になることが多い</li>"
         "<li><strong>後払いを想定していない</strong>: 入金までの資金繰りを事前に確認</li>"
         "<li><strong>対象経費の勘違い</strong>: 汎用品(パソコンなど)は対象外の制度がある</li>"
         "<li><strong>締切直前の申請</strong>: 電子申請の混雑・GビズID発行の遅れで間に合わないことがある</li>"
         "<li><strong>「必ず採択される」とうたう業者</strong>: 採択は審査によるため、保証はできません。高額な成功報酬などには注意してください</li></ul>"
         "<p>不安な場合は、商工会議所・商工会、よろず支援拠点などの公的な無料相談窓口の利用も検討してください。</p>", S3_NAV, S3_DISC)


# ============================================================ ハブ・sitemap
def build_hub():
    body = ("<h1>サイト一覧</h1><div class='card'><a href='tekadori/index.html'>手取り・税金かんたん計算</a></div>"
            "<div class='card'><a href='it-shikaku/index.html'>IT資格 学習ノート</a></div>"
            "<div class='card'><a href='hojokin/index.html'>補助金・助成金ガイド</a></div>")
    page(dict(name="サイト一覧", home="index.html"), "index.html", "サイト一覧", "3つの情報サイトへのリンク", body, [], "")


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    build_site1(); build_site2(); build_site3(); build_hub()
    write(".nojekyll", "")
    if BASE_URL:
        urls = "".join(f"<url><loc>{BASE_URL}/{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in sorted(written))
        write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
        write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    print(f"generated {len(written)} pages -> {OUT}")


if __name__ == "__main__":
    main()
