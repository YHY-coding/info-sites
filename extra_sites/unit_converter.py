"""単位換算ツール集(長さ・重さ・面積・温度・データ容量)。規約: META と build(page, write) を持つ。出力は docs/unit-converter/ 配下。"""
import html
import json

META = dict(slug="unit-converter", name="単位換算ツール集", desc="長さ・重さ・面積・温度・データ容量の単位を、ブラウザだけで換算できる無料ツール。尺貫法や坪にも対応")
SITE = dict(name=META["name"], home="index.html")
NAV = [("長さ", "length.html"), ("重さ", "weight.html"), ("面積", "area.html"), ("温度", "temperature.html"), ("データ容量", "data.html"), ("解説", "jp-units.html")]
DISC = ("本サイトの換算結果は概算・目安です(表示は有効数字10桁まで)。取引・証明・製品仕様など正確さが必要な場面では、公式の基準や取扱説明書で確認してください。"
        "入力した数値は、ブラウザの中だけで計算され、送信されません。")


def esc(s):
    return html.escape(s, quote=True)


# 各単位の「基準単位あたりの大きさ」。基準: 長さ=m、重さ=kg、面積=m²、データ=バイト
TABLES = {
    "length": {"base": "m", "units": [
        ("mm", "ミリメートル(mm)", 0.001), ("cm", "センチメートル(cm)", 0.01), ("m", "メートル(m)", 1.0), ("km", "キロメートル(km)", 1000.0),
        ("in", "インチ(in)", 0.0254), ("ft", "フィート(ft)", 0.3048), ("yd", "ヤード(yd)", 0.9144), ("mi", "マイル(mile)", 1609.344),
        ("shaku", "尺", 10 / 33), ("ken", "間", 60 / 33), ("ri", "里", 0.0)]},
    "weight": {"base": "kg", "units": [
        ("mg", "ミリグラム(mg)", 1e-6), ("g", "グラム(g)", 0.001), ("kg", "キログラム(kg)", 1.0), ("t", "トン(t)", 1000.0),
        ("oz", "オンス(oz)", 0.028349523125), ("lb", "ポンド(lb)", 0.45359237), ("monme", "匁", 3.75 / 1000), ("kan", "貫", 3.75)]},
    "area": {"base": "m²", "units": [
        ("m2", "平方メートル(m²)", 1.0), ("a", "アール(a)", 100.0), ("ha", "ヘクタール(ha)", 10000.0), ("km2", "平方キロメートル(km²)", 1e6),
        ("tsubo", "坪", 400 / 121), ("ft2", "平方フィート(ft²)", 0.09290304), ("acre", "エーカー(acre)", 4046.8564224)]},
    "data": {"base": "B", "units": [
        ("bit", "ビット(bit)", 1 / 8), ("B", "バイト(B)", 1.0), ("KB", "キロバイト(KB=1000B)", 1e3), ("MB", "メガバイト(MB=10^6B)", 1e6),
        ("GB", "ギガバイト(GB=10^9B)", 1e9), ("TB", "テラバイト(TB=10^12B)", 1e12),
        ("KiB", "キビバイト(KiB=1024B)", 1024.0), ("MiB", "メビバイト(MiB)", 1048576.0), ("GiB", "ギビバイト(GiB)", 1073741824.0), ("TiB", "テビバイト(TiB)", 1099511627776.0)]},
}
# 里は36町=2160間(1間=6尺)
TABLES["length"]["units"][-1] = ("ri", "里", 2160 * 60 / 33)

TEMPS = [("C", "摂氏(℃)"), ("F", "華氏(℉)"), ("K", "ケルビン(K)")]


# ---- Python側の基準実装(ブラウザ側JSと一致することを確認する) ----
def convert(table, v, frm, to):
    f = {u[0]: u[2] for u in TABLES[table]["units"]}
    return v * f[frm] / f[to]


def temp(v, frm, to):
    k = v + 273.15 if frm == "C" else (v - 32) * 5 / 9 + 273.15 if frm == "F" else v
    return k - 273.15 if to == "C" else (k - 273.15) * 9 / 5 + 32 if to == "F" else k


# ---- ブラウザ側JS ----
CORE_JS = """
var T=%s;
function convert(t,v,a,b){var f={};T[t].units.forEach(function(u){f[u[0]]=u[2]});return v*f[a]/f[b]}
function temp(v,a,b){var k=a==='C'?v+273.15:a==='F'?(v-32)*5/9+273.15:v;return b==='C'?k-273.15:b==='F'?(k-273.15)*9/5+32:k}
function $(id){return document.getElementById(id)}
function fmt(x){if(!isFinite(x))return '-';if(x===0)return '0';var a=Math.abs(x);if(a>=1e15||a<1e-9)return x.toExponential(6);return Number(x.toPrecision(10)).toLocaleString('ja-JP',{maximumSignificantDigits:10})}
""" % json.dumps({k: {"units": v["units"]} for k, v in TABLES.items()}, ensure_ascii=True)

GEN_JS = """
function init(t){var us=T[t].units,s1=$('a'),s2=$('b');
us.forEach(function(u,i){s1.add(new Option(u[1],u[0]));s2.add(new Option(u[1],u[0]))});
s1.selectedIndex=%d;s2.selectedIndex=%d;
function run(){var v=parseFloat($('v').value);if(isNaN(v)){$('out').textContent='数値を入力してください';return}
var r=convert(t,v,s1.value,s2.value),h='<p class="big">'+fmt(r)+'</p><table><tr><th>単位</th><th>値</th></tr>';
us.forEach(function(u){h+='<tr><td>'+u[1]+'</td><td>'+fmt(convert(t,v,s1.value,u[0]))+'</td></tr>'});
$('out').innerHTML=h+'</table>'}
['v','a','b'].forEach(function(i){$(i).oninput=run;$(i).onchange=run});run()}
"""

TEMP_JS = """
var N={C:'摂氏(℃)',F:'華氏(℉)',K:'ケルビン(K)'};
function run(){var v=parseFloat($('v').value),a=$('a').value,b=$('b').value;if(isNaN(v)){$('out').textContent='数値を入力してください';return}
var k=a==='C'?v+273.15:a==='F'?(v-32)*5/9+273.15:v;
if(k<0){$('out').textContent='絶対零度(0K=-273.15℃)より低い値は存在しません';return}
var h='<p class="big">'+fmt(temp(v,a,b))+'</p><table><tr><th>単位</th><th>値</th></tr>';
['C','F','K'].forEach(function(u){h+='<tr><td>'+N[u]+'</td><td>'+fmt(temp(v,a,u))+'</td></tr>'});
$('out').innerHTML=h+'</table>'}
['v','a','b'].forEach(function(i){$(i).oninput=run;$(i).onchange=run});run();
"""


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)

    def conv_page(path, t, title, desc, h1, v0, i1, i2, extra):
        sel = "<select id='%s'></select>"
        body = (f"<h1>{h1}</h1><div class='card'><label>数値 <input id='v' type='number' value='{v0}' step='any'></label><br>"
                f"<label>換算元 {sel % 'a'}</label> <label>換算先 {sel % 'b'}</label></div><div id='out' class='card'></div>" + extra
                + f"<script>{CORE_JS}{GEN_JS % (i1, i2)}init('{t}');</script>")
        p(path, title, desc, body)

    p("index.html", "単位換算ツール集|長さ・重さ・面積・温度・データ容量",
      "長さ、重さ、面積、温度、データ容量の単位を換算できる無料ツール集です。尺貫法や坪、KBとKiBの違いの解説もあります。",
      "<h1>単位換算ツール集</h1><p>入力した数値は、ブラウザの中だけで計算されます。サーバーには送信されません。</p>"
      "<div class='card'><a href='length.html'><strong>長さの換算</strong></a><br>mm・cm・m・km・インチ・フィート・ヤード・マイル・尺・間・里</div>"
      "<div class='card'><a href='weight.html'><strong>重さの換算</strong></a><br>mg・g・kg・t・オンス・ポンド・匁・貫</div>"
      "<div class='card'><a href='area.html'><strong>面積の換算</strong></a><br>m²・アール・ヘクタール・km²・坪・平方フィート・エーカー</div>"
      "<div class='card'><a href='temperature.html'><strong>温度の換算</strong></a><br>摂氏・華氏・ケルビン</div>"
      "<div class='card'><a href='data.html'><strong>データ容量の換算</strong></a><br>bit・バイト・KB/MB/GB/TB・KiB/MiB/GiB/TiB</div>"
      "<h2>解説ページ</h2><ul class='links'><li><a href='jp-units.html'>尺貫法の単位(尺・間・坪・貫)</a></li><li><a href='si-prefix.html'>SI接頭辞(キロ・メガ・ミリ など)</a></li>"
      "<li><a href='bits-bytes.html'>ビットとバイト、KBとKiBの違い</a></li><li><a href='temperature-scales.html'>摂氏・華氏・ケルビンの関係</a></li></ul>")

    conv_page("length.html", "length", "長さの換算|cm・インチ・フィート・尺", "mm、cm、m、km、インチ、フィート、ヤード、マイル、尺、間、里の間で長さを換算します。",
              "長さの換算", 1, 2, 5,
              "<h2>よく使う目安</h2><ul><li>1インチ = 2.54cm(定義)</li><li>1フィート = 12インチ = 30.48cm(定義)</li><li>1マイル = 1609.344m(定義)</li><li>1尺 = 10/33m(約30.30cm)</li></ul>"
              "<p class='note'>尺貫法の単位は、<a href='jp-units.html'>尺貫法の単位</a>を参照してください。</p>")
    conv_page("weight.html", "weight", "重さの換算|kg・ポンド・オンス・貫", "mg、g、kg、トン、オンス、ポンド、匁、貫の間で重さ(質量)を換算します。",
              "重さの換算", 1, 2, 5,
              "<h2>よく使う目安</h2><ul><li>1ポンド = 0.45359237kg(定義)</li><li>1オンス = 約28.35g(1ポンドの16分の1)</li><li>1貫 = 3.75kg、1匁 = 3.75g</li></ul>"
              "<p class='note'>ここでの「重さ」は質量の単位として換算しています。宝石や貴金属で使われるトロイオンスなど、別の定義の単位は含みません。</p>")
    conv_page("area.html", "area", "面積の換算|㎡・坪・ヘクタール・エーカー", "平方メートル、アール、ヘクタール、平方キロメートル、坪、平方フィート、エーカーの間で面積を換算します。",
              "面積の換算", 1, 0, 4,
              "<h2>よく使う目安</h2><ul><li>1坪 = 400/121㎡(約3.306㎡)</li><li>1アール = 100㎡、1ヘクタール = 10,000㎡</li><li>1エーカー = 約4,046.86㎡</li></ul>"
              "<p class='note'>畳(帖)の広さは地域や建物によって異なるため、このツールには含めていません。不動産の面積表示は、公式の基準や表示ルールで確認してください。</p>")
    conv_page("data.html", "data", "データ容量の換算|KB・MB・GB・KiB", "ビット、バイト、KB・MB・GB・TB(10進)とKiB・MiB・GiB・TiB(2進)の間でデータ容量を換算します。",
              "データ容量の換算", 1, 4, 8,
              "<h2>注意点</h2><ul><li>KB・MB・GBは1000倍ずつ(10進)、KiB・MiB・GiBは1024倍ずつ(2進)で計算しています</li>"
              "<li>機器やOSの表示では、1024倍ずつの数え方をKB・GBと表記する場合があります。違いは<a href='bits-bytes.html'>ビットとバイト、KBとKiBの違い</a>を参照してください</li></ul>")

    p("temperature.html", "温度の換算|摂氏・華氏・ケルビン",
      "摂氏(℃)、華氏(℉)、ケルビン(K)の間で温度を換算します。",
      "<h1>温度の換算</h1><div class='card'><label>数値 <input id='v' type='number' value='20' step='any'></label><br>"
      "<label>換算元 <select id='a'><option value='C'>摂氏(℃)</option><option value='F'>華氏(℉)</option><option value='K'>ケルビン(K)</option></select></label> "
      "<label>換算先 <select id='b'><option value='F'>華氏(℉)</option><option value='C'>摂氏(℃)</option><option value='K'>ケルビン(K)</option></select></label></div>"
      "<div id='out' class='card'></div><h2>計算式</h2><ul><li>華氏 = 摂氏 × 9/5 + 32</li><li>ケルビン = 摂氏 + 273.15</li></ul>"
      "<p class='note'>考え方は<a href='temperature-scales.html'>摂氏・華氏・ケルビンの関係</a>を参照してください。</p>"
      f"<script>{CORE_JS}{TEMP_JS}</script>")

    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in [
        ("1尺", "10/33m(約30.30cm)", "1寸の10倍"), ("1間", "6尺 = 60/33m(約1.818m)", "建築や土地でよく使う"), ("1里", "36町 = 2160間(約3.927km)", "1町 = 60間"),
        ("1坪", "1間×1間 = 400/121㎡(約3.306㎡)", "土地・建物の面積"), ("1匁", "3.75g", "真珠などの重さにも使われる"), ("1貫", "1000匁 = 3.75kg", "")])
    p("jp-units.html", "尺貫法の単位|尺・間・坪・匁・貫の換算",
      "尺貫法の長さ・面積・重さの単位(尺、間、里、坪、匁、貫)と、メートル法への換算を解説します。",
      "<h1>尺貫法の単位</h1><p>尺貫法は、長さを尺、重さを貫で表す日本の伝統的な単位系です。現在、取引や証明に使える単位はメートル法が基本ですが、建築や不動産、工芸などで昔の単位が話題に出ることがあります。</p>"
      "<table><tr><th>単位</th><th>メートル法での大きさ</th><th>メモ</th></tr>" + rows + "</table>"
      "<p class='note'>尺貫法の単位をメートル法に直す関係は、法令で定められた換算値にもとづくものです。取引や証明で使う場合は、公式の基準で確認してください。</p>"
      "<p><a href='length.html'>長さ</a> / <a href='area.html'>面積</a> / <a href='weight.html'>重さ</a>のツールで換算できます。</p>")

    pre = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in [
        ("キロ(k)", "10の3乗", "1000倍"), ("メガ(M)", "10の6乗", "100万倍"), ("ギガ(G)", "10の9乗", "10億倍"), ("テラ(T)", "10の12乗", "1兆倍"),
        ("ミリ(m)", "10の−3乗", "1000分の1"), ("マイクロ(μ)", "10の−6乗", "100万分の1"), ("ナノ(n)", "10の−9乗", "10億分の1"),
        ("センチ(c)", "10の−2乗", "100分の1"), ("ヘクト(h)", "10の2乗", "100倍")])
    p("si-prefix.html", "SI接頭辞|キロ・メガ・ミリ・マイクロ",
      "キロ、メガ、ギガ、ミリ、マイクロなどSI接頭辞の意味と、単位換算での使い方を解説します。",
      "<h1>SI接頭辞(キロ・メガ・ミリ など)</h1><p>メートルやグラムなどの単位の前に付けて、10の何乗倍かを表す言葉です。接頭辞と単位の組み合わせで、大きな量も小さな量も表せます。</p>"
      "<table><tr><th>接頭辞</th><th>10の累乗</th><th>倍率</th></tr>" + pre + "</table>"
      "<h2>換算の手順</h2><ol><li>接頭辞を、倍率に置き換える(例:3km = 3 × 1000 m)</li><li>基準の単位(m、g など)に直す</li><li>目的の接頭辞の倍率で割る</li></ol>"
      "<p class='note'>データ容量のKB・MBは、1000倍の意味と1024倍の意味で使われることがあります。<a href='bits-bytes.html'>ビットとバイト、KBとKiBの違い</a>を参照してください。</p>")

    p("bits-bytes.html", "ビットとバイト、KBとKiBの違い",
      "ビットとバイトの関係、10進のKB・MB・GBと2進のKiB・MiB・GiBの違い、容量の表示が食い違う理由を解説します。",
      "<h1>ビットとバイト、KBとKiBの違い</h1>"
      "<h2>ビットとバイト</h2><p>ビット(bit)は情報の最小単位で、0か1のどちらかを表します。1バイト(B)は8ビットです。通信の速さはビット毎秒、ファイルの大きさはバイトで表すことが多いため、数字を比べるときは単位に注意が必要です。</p>"
      "<h2>10進と2進</h2><table><tr><th>表記</th><th>大きさ</th><th>倍率</th></tr><tr><td>KB・MB・GB・TB</td><td>1000バイト、100万バイト…</td><td>1000倍ずつ</td></tr>"
      "<tr><td>KiB・MiB・GiB・TiB</td><td>1024バイト、1,048,576バイト…</td><td>1024倍ずつ</td></tr></table>"
      "<p>コンピュータの内部では2のべき乗が扱いやすいため、1024倍の数え方が使われてきました。それとは別に、SIの接頭辞と同じ1000倍の意味もあるため、区別する表記としてKiBなどが作られました。</p>"
      "<h2>表示が食い違う理由</h2><ul><li>製品の容量表示は1000倍ずつで、OSの表示は1024倍ずつで計算している場合があり、同じ容量でも数字が小さく見えることがあります</li>"
      "<li>どちらの数え方を使っているかは、製品の仕様や公式の説明で確認してください</li></ul>"
      "<p><a href='data.html'>データ容量の換算ツール</a>で、両方の単位に換算できます。</p>")

    p("temperature-scales.html", "摂氏・華氏・ケルビンの関係",
      "摂氏、華氏、ケルビンの基準と換算式、絶対零度の意味を解説します。",
      "<h1>摂氏・華氏・ケルビンの関係</h1>"
      "<table><tr><th>温度の目盛り</th><th>特徴</th></tr><tr><td>摂氏(℃)</td><td>水が凍る温度を0度、沸騰する温度を100度とする目盛りの考え方にもとづく(気圧の条件があります)。日本の日常で使う</td></tr>"
      "<tr><td>華氏(℉)</td><td>アメリカなどで日常的に使われる。摂氏0度は華氏32度、摂氏100度は華氏212度</td></tr>"
      "<tr><td>ケルビン(K)</td><td>科学で使う絶対温度。目盛りの間隔は摂氏と同じで、0Kが絶対零度</td></tr></table>"
      "<h2>換算式</h2><ul><li>華氏 = 摂氏 × 9/5 + 32、摂氏 = (華氏 − 32) × 5/9</li><li>ケルビン = 摂氏 + 273.15</li></ul>"
      "<h2>換算の例</h2><table><tr><th>摂氏</th><th>華氏</th><th>ケルビン</th></tr><tr><td>0℃</td><td>32℉</td><td>273.15K</td></tr><tr><td>20℃</td><td>68℉</td><td>293.15K</td></tr>"
      "<tr><td>100℃</td><td>212℉</td><td>373.15K</td></tr></table>"
      "<p class='note'>絶対零度は約−273.15℃で、これより低い温度は存在しません。温度の差(○度の違い)を換算するときは、32や273.15の足し算は不要で、華氏は摂氏の9/5倍になります。</p>"
      "<p><a href='temperature.html'>温度の換算ツール</a></p>")
