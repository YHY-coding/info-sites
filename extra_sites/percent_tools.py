"""割合・比率・増減率の計算ツール集。規約: META と build(page, write) を持つ。出力は docs/percent-tools/ 配下。"""
import html
from math import gcd

META = dict(slug="percent-tools", name="割合・増減率計算ツール集", desc="割合(○%はいくつ)、何%にあたるか、増減率、元の値の逆算、比の簡約と按分をブラウザだけで試せる無料ツールと解説")
SITE = dict(name=META["name"], home="index.html")
NAV = [("割合の値", "percent-of.html"), ("何%か", "what-percent.html"), ("増減率", "change-rate.html"), ("逆算", "reverse.html"), ("比", "ratio.html"),
       ("基本", "basics.html"), ("%とポイント", "percent-vs-point.html"), ("つまずき", "pitfalls.html"), ("手計算", "manual.html"), ("用語", "glossary.html")]
DISC = ("本サイトの結果は概算・目安です。契約・会計・申告などで使う前には、公式の情報や各組織の規定で確認してください。"
        "入力した値は、ブラウザの中だけで計算され、送信されません。")


def esc(s):
    return html.escape(s, quote=True)


# ---- Python側の基準実装(ブラウザ側JSと一致することを node で確認する) ----
def pct_of(p, b):
    return b * p / 100


def what_pct(a, b):
    return None if b == 0 else a / b * 100


def change_rate(old, new):
    return None if old == 0 else (new - old) / old * 100


def apply_change(base, rate):
    return base * (1 + rate / 100)


def reverse(after, rate):
    return None if rate == -100 else after / (1 + rate / 100)


def simplify(a, b):
    g = gcd(a, b)
    return None if g == 0 else (a // g, b // g)


def split(total, a, b):
    return None if a + b == 0 else (total * a / (a + b), total * b / (a + b))


LIB = """
function num(s){s=String(s).trim().replace(/,/g,'');if(!/^-?[0-9]+(\\.[0-9]+)?$/.test(s))return null;return parseFloat(s)}
function int(s){s=String(s).trim();if(!/^[0-9]+$/.test(s))return null;return parseInt(s,10)}
function gcd(a,b){while(b){var t=a%b;a=b;b=t}return a}
function pctOf(p,b){return b*p/100}
function whatPct(a,b){return b===0?null:a/b*100}
function changeRate(o,n){return o===0?null:(n-o)/o*100}
function applyChange(b,r){return b*(1+r/100)}
function reverse(a,r){return r===-100?null:a/(1+r/100)}
function simplify(a,b){var g=gcd(a,b);return g===0?null:[a/g,b/g]}
function split(t,a,b){return a+b===0?null:[t*a/(a+b),t*b/(a+b)]}
function f2(x){return x.toFixed(2)}
function $(id){return document.getElementById(id)}
"""

BAD = "入力を確認してください(数字で入力。カンマは使えます)"

POF_JS = """
function run(){var p=num($('p').value),b=num($('b').value);
if(p===null||b===null){$('out').textContent='"""+BAD+"""';return}
$('out').innerHTML='<p>'+b+' の '+p+'% = <strong class="big">'+f2(pctOf(p,b))+'</strong></p>'
+'<p>'+b+' を '+p+'% 増やす → '+f2(applyChange(b,p))+'</p><p>'+b+' を '+p+'% 減らす → '+f2(applyChange(b,-p))+'</p>'}
$('btn').onclick=run;run();
"""

WP_JS = """
function run(){var a=num($('a').value),b=num($('b').value);
if(a===null||b===null){$('out').textContent='"""+BAD+"""';return}
var r=whatPct(a,b);if(r===null){$('out').textContent='基準の値が0のときは計算できません';return}
$('out').innerHTML='<p>'+a+' は '+b+' の <strong class="big">'+f2(r)+'%</strong></p>'}
$('btn').onclick=run;run();
"""

CR_JS = """
function run(){var o=num($('o').value),n=num($('n').value);
if(o===null||n===null){$('out').textContent='"""+BAD+"""';return}
var r=changeRate(o,n);if(r===null){$('out').textContent='変化前が0のときは増減率を計算できません';return}
$('out').innerHTML='<p>増減率 <strong class="big">'+(r>=0?'+':'')+f2(r)+'%</strong></p><p>差 '+f2(n-o)+'</p>'}
$('btn').onclick=run;run();
"""

REV_JS = """
function run(){var a=num($('a').value),r=num($('r').value);
if(a===null||r===null){$('out').textContent='"""+BAD+"""';return}
var v=reverse(a,r);if(v===null){$('out').textContent='-100%の変化からは元の値を求められません';return}
$('out').innerHTML='<p>変化後が '+a+'、変化率が '+r+'% のとき、元の値は <strong class="big">'+f2(v)+'</strong></p>'}
$('btn').onclick=run;run();
"""

RAT_JS = """
function run(){var a=int($('a').value),b=int($('b').value),t=num($('t').value);
if(a===null||b===null||t===null){$('out').textContent='比は0以上の整数、合計は数字で入力してください';return}
var s=simplify(a,b),sp=split(t,a,b);if(s===null||sp===null){$('out').textContent='比の両方が0のときは計算できません';return}
$('out').innerHTML='<p>'+a+' : '+b+' = <strong>'+s[0]+' : '+s[1]+'</strong>(最も簡単な整数比)</p><p>'+t+' を '+a+' : '+b+' に分ける → <strong>'+f2(sp[0])+'</strong> と <strong>'+f2(sp[1])+'</strong></p>'}
$('btn').onclick=run;run();
"""


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)
    inp = lambda i, label, v: f"<label>{label} <input id='{i}' type='text' value='{v}'></label><br>"

    p("index.html", "割合・増減率計算ツール集|何%か・増減率・逆算・比",
      "割合の値、何%にあたるか、増減率、元の値の逆算、比の簡約と按分をブラウザだけで計算できる無料ツールと、割合の基本解説をまとめたサイトです。",
      "<h1>割合・増減率計算ツール集</h1><p>入力した値は、ブラウザの中だけで計算されます。サーバーには送信されません。</p>"
      "<h2>ツール</h2>"
      "<div class='card'><a href='percent-of.html'><strong>○%はいくつ(割合の値)</strong></a><br>基準の値の○%、○%増・○%減した値</div>"
      "<div class='card'><a href='what-percent.html'><strong>何%にあたるか</strong></a><br>AはBの何%かを計算</div>"
      "<div class='card'><a href='change-rate.html'><strong>増減率の計算</strong></a><br>変化前と変化後から増減率を計算</div>"
      "<div class='card'><a href='reverse.html'><strong>元の値の逆算</strong></a><br>○%増えた後の値から元の値を求める</div>"
      "<div class='card'><a href='ratio.html'><strong>比の簡約と按分</strong></a><br>整数比を簡単にし、合計を比で分ける</div>"
      "<h2>解説</h2><ul class='links'><li><a href='basics.html'>割合・百分率・歩合の基本</a></li><li><a href='percent-vs-point.html'>%とポイントの違い</a></li>"
      "<li><a href='pitfalls.html'>割合計算のつまずきやすい点</a></li><li><a href='manual.html'>割合計算の手計算</a></li><li><a href='glossary.html'>用語集</a></li></ul>")

    p("percent-of.html", "○%はいくつ?割合の値の計算ツール|増やす・減らすも",
      "基準の値の○%がいくつか、また○%増やした値・○%減らした値を計算します。",
      "<h1>○%はいくつ(割合の値)</h1><p>基準の値と割合(%)を入力します。</p>"
      "<div class='card'>" + inp("b", "基準の値", "8000") + inp("p", "割合(%)", "15") + "<br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>式</h2><p>基準の値 × 割合 ÷ 100。○%増やすときは × (1 + 割合/100)、減らすときは × (1 − 割合/100) です。</p>"
      "<p>逆に「AはBの何%か」は<a href='what-percent.html'>こちら</a>。結果は小数第2位までの概算です。</p>"
      f"<script>{LIB}{POF_JS}</script>")

    p("what-percent.html", "AはBの何%?割合を求める計算ツール",
      "ある値が基準の値の何%にあたるかを計算します。",
      "<h1>何%にあたるか</h1><p>比べる値(A)と、基準の値(B)を入力します。</p>"
      "<div class='card'>" + inp("a", "比べる値 A", "36") + inp("b", "基準の値 B", "120") + "<br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>式</h2><p>A ÷ B × 100。基準は「もとにする量」である B です。どちらを基準にするかで答えが変わるので注意してください(<a href='pitfalls.html'>つまずきやすい点</a>)。</p>"
      f"<script>{LIB}{WP_JS}</script>")

    p("change-rate.html", "増減率の計算ツール|変化前と変化後から求める",
      "変化前の値と変化後の値から、増減率(%)と差を計算します。",
      "<h1>増減率の計算</h1><p>変化前と変化後の値を入力します。減った場合はマイナスで表示されます。</p>"
      "<div class='card'>" + inp("o", "変化前", "2500") + inp("n", "変化後", "2000") + "<br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>式</h2><p>(変化後 − 変化前) ÷ 変化前 × 100。基準は常に「変化前」です。</p>"
      "<p>注意: 20%減った後に20%増えても元には戻りません(<a href='pitfalls.html'>理由</a>)。</p>"
      f"<script>{LIB}{CR_JS}</script>")

    p("reverse.html", "元の値の逆算ツール|○%増えた後の値から元を求める",
      "変化後の値と変化率(%)から、変化前の元の値を逆算します。",
      "<h1>元の値の逆算</h1><p>変化後の値と、変化率(増加は正、減少は負の%)を入力します。</p>"
      "<div class='card'>" + inp("a", "変化後の値", "1150") + inp("r", "変化率(%)", "15") + "<br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>式</h2><p>変化後 ÷ (1 + 変化率/100)。「15%引いた値から元を求めたい」ときは、変化率に −15 と入力します。</p>"
      "<p>変化後の値から変化率を単純に引き算しても、元の値にはなりません(<a href='pitfalls.html'>つまずきやすい点</a>)。</p>"
      f"<script>{LIB}{REV_JS}</script>")

    p("ratio.html", "比の簡約と按分ツール|整数比を簡単にして合計を分ける",
      "2つの整数比を最も簡単な整数比に直し、合計の値をその比で分けます。",
      "<h1>比の簡約と按分</h1><p>比 A : B(0以上の整数)と、分けたい合計の値を入力します。</p>"
      "<div class='card'>" + inp("a", "A", "12") + inp("b", "B", "18") + inp("t", "合計の値", "1000") + "<br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>考え方</h2><ul><li>簡約: AとBを最大公約数で割る</li><li>按分: 合計 × A ÷ (A+B) と 合計 × B ÷ (A+B)</li></ul>"
      "<p>費用の分担などに使う場合の取り決めは、当事者間の合意や公式の規定で確認してください。</p>"
      f"<script>{LIB}{RAT_JS}</script>")

    p("basics.html", "割合・百分率・歩合の基本",
      "割合の三要素(くらべる量・もとにする量・割合)と、百分率・歩合・小数の対応を解説します。",
      "<h1>割合・百分率・歩合の基本</h1>"
      "<h2>割合の三要素</h2><p>割合 = くらべる量 ÷ もとにする量。三つのうち二つがわかれば残りが求まります。</p>"
      "<ul><li>くらべる量 = もとにする量 × 割合</li><li>もとにする量 = くらべる量 ÷ 割合</li></ul>"
      "<h2>表し方の対応</h2><table><tr><th>小数</th><th>百分率</th><th>歩合</th></tr><tr><td>1</td><td>100%</td><td>10割</td></tr>"
      "<tr><td>0.5</td><td>50%</td><td>5割</td></tr><tr><td>0.25</td><td>25%</td><td>2割5分</td></tr><tr><td>0.1</td><td>10%</td><td>1割</td></tr>"
      "<tr><td>0.01</td><td>1%</td><td>1分</td></tr></table>"
      "<p>百分率は小数を100倍して「%」を付けたものです。実際の計算は<a href='percent-of.html'>割合の値のツール</a>で試せます。</p>")

    p("percent-vs-point.html", "%とポイントの違い|割合の差の表し方",
      "「5%から8%」のような割合どうしの差は「3ポイント」と表す理由と、増加率(%)との違いを解説します。",
      "<h1>%とポイントの違い</h1>"
      "<p>割合(%)どうしの差は、「ポイント」で表すのが一般的です。たとえば 5% が 8% になったとき、差は <strong>3ポイント</strong> です。</p>"
      "<h2>増加率との違い</h2><p>同じ変化を「増加率」で表すと、(8 − 5) ÷ 5 × 100 = 60% の増加です。「3ポイント上がった」と「60%増えた」は、どちらも正しい別の言い方です。</p>"
      "<table><tr><th>表現</th><th>意味</th><th>この例での値</th></tr><tr><td>ポイント</td><td>割合どうしの差</td><td>3ポイント</td></tr><tr><td>増加率</td><td>変化前を基準にした増え方</td><td>60%</td></tr></table>"
      "<p>文章を読むときは、どちらの意味かを確認しましょう。増加率は<a href='change-rate.html'>増減率ツール</a>で計算できます。</p>")

    p("pitfalls.html", "割合計算のつまずきやすい点|増えて減る・基準の取り違え",
      "20%増えて20%減っても元に戻らない理由、基準の取り違え、逆算の間違いなど、割合計算でよくあるつまずきを例つきで解説します。",
      "<h1>割合計算のつまずきやすい点</h1>"
      "<h2>1. 増えて減っても元に戻らない</h2><p>100を20%増やすと120。120を20%減らすと96で、元の100には戻りません。減らすときの基準が、増えた後の120になるためです。</p>"
      "<h2>2. 基準の取り違え</h2><p>「AはBの何%」と「BはAの何%」は別の答えです。36は120の30%ですが、120は36の約333%です。何を基準(もとにする量)にしているかを必ず確認します。</p>"
      "<h2>3. 逆算で割合を引き算してしまう</h2><p>15%増えて1150になったとき、元は 1150 − 15% ではありません。1150 ÷ 1.15 = 1000 です。<a href='reverse.html'>逆算ツール</a>で確かめられます。</p>"
      "<h2>4. 連続する割合は足せない</h2><p>10%増の後に10%増は、20%増ではなく21%増(1.1 × 1.1 = 1.21)です。</p>"
      "<p>丸めの扱いは場面ごとに決まりが異なるため、実務では公式の情報や規定で確認してください。</p>")

    p("manual.html", "割合計算の手計算のやり方",
      "暗算・筆算で割合を求めるコツ(10%、1%を基準にする方法)と、検算の方法を例つきで解説します。",
      "<h1>割合計算の手計算のやり方</h1>"
      "<h2>10%と1%を基準にする</h2><p>10%は10で割る、1%は100で割ることで求まります。例: 8,000円の15% → 10%は800、5%はその半分の400、合わせて1,200。</p>"
      "<h2>約分で割合を出す</h2><p>36は120の何%か: 36/120 を約分して 3/10 → 30%。</p>"
      "<h2>増減後の値</h2><p>○%増は (1 + ○/100) 倍、○%減は (1 − ○/100) 倍します。例: 2,500円の20%減 → 2,500 × 0.8 = 2,000円。</p>"
      "<h2>検算</h2><p>逆算で元に戻るか確かめます。2,000 ÷ 0.8 = 2,500。計算結果は<a href='percent-of.html'>割合の値のツール</a>と見比べてください。</p>")

    terms = [("百分率", "全体を100としたときの割合。単位は%"), ("歩合", "割・分・厘で表す割合の表し方"), ("もとにする量", "割合の基準となる量"),
             ("くらべる量", "基準と比べる量"), ("増減率", "変化量を変化前で割った割合"), ("ポイント", "割合どうしの差を表す単位"),
             ("比", "2つ以上の量の大きさの関係を a:b で表したもの"), ("按分", "合計を比に応じて分けること"), ("最大公約数", "複数の整数に共通する約数のうち最大のもの"),
             ("逆算", "結果から元の値を求めること")]
    p("glossary.html", "割合計算の用語集",
      "百分率・歩合・増減率・ポイント・按分など、割合計算に出てくる基本用語をまとめました。",
      "<h1>割合計算の用語集</h1><table><tr><th>用語</th><th>意味</th></tr>"
      + "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in terms) + "</table>"
      "<p><a href='basics.html'>基本</a> / <a href='percent-vs-point.html'>%とポイント</a></p>")
