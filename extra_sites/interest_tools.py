"""単利・複利の計算ツール集。規約: META と build(page, write) を持つ。出力は docs/interest-tools/ 配下。"""
import html
from math import log

META = dict(slug="interest-tools", name="単利・複利計算ツール集", desc="単利、複利、毎月の積立の将来額、目標額までの年数をブラウザだけで試せる無料計算ツールと、利息計算の仕組みの解説(計算のみ・助言はしません)")
SITE = dict(name=META["name"], home="index.html")
NAV = [("単利", "simple.html"), ("複利", "compound.html"), ("積立", "accumulate.html"), ("目標年数", "years.html"), ("倍になる年数", "rule72.html"),
       ("基本", "basics.html"), ("単利と複利", "simple-vs-compound.html"), ("つまずき", "pitfalls.html"), ("用語", "glossary.html")]
DISC = ("本サイトの結果は概算・目安です。税金・手数料・実際の利率の変動は考慮していません。特定の商品の選択や運用の判断をすすめるものではありません。"
        "実際の条件は、各金融機関や公式の情報で確認してください。入力した値は、ブラウザの中だけで計算され、送信されません。")


def esc(s):
    return html.escape(s, quote=True)


# ---- Python側の基準実装(ブラウザ側JSと一致することを node で確認する) ----
def simple(p, r, n):
    return p * (1 + r / 100 * n)


def compound(p, r, n, m):
    return p * (1 + r / 100 / m) ** (m * n)


def accumulate(c, r, years):
    i = r / 100 / 12
    k = round(years * 12)
    return c * k if i == 0 else c * ((1 + i) ** k - 1) / i


def years_to(p, t, r, m):
    if p <= 0 or t <= 0 or r <= 0 or t < p:
        return None
    return log(t / p) / (m * log(1 + r / 100 / m))


def double_years(r):
    return None if r <= 0 else log(2) / log(1 + r / 100)


LIB = """
function num(s){s=String(s).trim().replace(/,/g,'');if(!/^-?[0-9]+(\\.[0-9]+)?$/.test(s))return null;return parseFloat(s)}
function simple(p,r,n){return p*(1+r/100*n)}
function compound(p,r,n,m){return p*Math.pow(1+r/100/m,m*n)}
function accumulate(c,r,y){var i=r/100/12,k=Math.round(y*12);return i===0?c*k:c*(Math.pow(1+i,k)-1)/i}
function yearsTo(p,t,r,m){if(p<=0||t<=0||r<=0||t<p)return null;return Math.log(t/p)/(m*Math.log(1+r/100/m))}
function doubleYears(r){return r<=0?null:Math.log(2)/Math.log(1+r/100)}
function yen(x){return Math.round(x).toLocaleString('ja-JP')}
function f1(x){return x.toFixed(1)}
function $(id){return document.getElementById(id)}
"""

BAD = "入力を確認してください(数字で入力。カンマは使えます)"

SIMPLE_JS = """
function run(){var p=num($('p').value),r=num($('r').value),n=num($('n').value);
if(p===null||r===null||n===null||p<0||n<0){$('out').textContent='"""+BAD+"""';return}
var t=simple(p,r,n);
$('out').innerHTML='<p>元本 '+yen(p)+' を年利 '+r+'%(単利)で '+n+' 年 → <strong class="big">'+yen(t)+'</strong></p><p>利息の合計 '+yen(t-p)+'</p>'}
$('btn').onclick=run;run();
"""

COMP_JS = """
function run(){var p=num($('p').value),r=num($('r').value),n=num($('n').value),m=parseInt($('m').value,10);
if(p===null||r===null||n===null||p<0||n<0){$('out').textContent='"""+BAD+"""';return}
var t=compound(p,r,n,m),s=simple(p,r,n);
$('out').innerHTML='<p>元本 '+yen(p)+' を年利 '+r+'%(複利)で '+n+' 年 → <strong class="big">'+yen(t)+'</strong></p><p>利息の合計 '+yen(t-p)+'(同条件の単利との差 '+yen(t-s)+')</p>'}
$('btn').onclick=run;run();
"""

ACC_JS = """
function run(){var c=num($('c').value),r=num($('r').value),y=num($('y').value);
if(c===null||r===null||y===null||c<0||y<0){$('out').textContent='"""+BAD+"""';return}
var t=accumulate(c,r,y),k=Math.round(y*12)*c;
$('out').innerHTML='<p>毎月 '+yen(c)+' を年利 '+r+'%(月複利・月末積立)で '+y+' 年 → <strong class="big">'+yen(t)+'</strong></p><p>積立の合計 '+yen(k)+' / 増えた分 '+yen(t-k)+'</p>'}
$('btn').onclick=run;run();
"""

YRS_JS = """
function run(){var p=num($('p').value),t=num($('t').value),r=num($('r').value),m=parseInt($('m').value,10);
if(p===null||t===null||r===null){$('out').textContent='"""+BAD+"""';return}
var y=yearsTo(p,t,r,m);if(y===null){$('out').textContent='元本・目標は正の数で、目標は元本以上、年利は0より大きい値にしてください';return}
$('out').innerHTML='<p>元本 '+yen(p)+' が年利 '+r+'%(複利)で '+yen(t)+' に届くまで 約 <strong class="big">'+f1(y)+'</strong> 年</p>'}
$('btn').onclick=run;run();
"""

R72_JS = """
function run(){var r=num($('r').value);
if(r===null){$('out').textContent='"""+BAD+"""';return}
var d=doubleYears(r);if(d===null){$('out').textContent='年利は0より大きい値にしてください';return}
$('out').innerHTML='<p>年利 '+r+'%(年1回複利)で2倍になるまで 約 <strong class="big">'+f1(d)+'</strong> 年</p><p>72の法則の目安: 72 ÷ '+r+' = '+f1(72/r)+' 年</p>'}
$('btn').onclick=run;run();
"""


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)
    inp = lambda i, label, v: f"<label>{label} <input id='{i}' type='text' value='{v}'></label><br>"
    sel = "<label>1年あたりの複利の回数 <select id='m'><option value='1'>年1回</option><option value='2'>年2回</option><option value='4'>年4回</option><option value='12' selected>月1回(年12回)</option></select></label><br>"
    btn = "<br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"

    p("index.html", "単利・複利計算ツール集|積立・目標年数・倍になる年数",
      "単利、複利、毎月の積立の将来額、目標額までの年数、元本が2倍になる年数をブラウザだけで計算できる無料ツールと、利息計算の仕組みの解説です。",
      "<h1>単利・複利計算ツール集</h1><p>利息計算の「仕組みを確かめる」ためのサイトです。入力した値はブラウザの中だけで計算され、送信されません。特定の商品や運用の助言はしません。</p>"
      "<h2>ツール</h2>"
      "<div class='card'><a href='simple.html'><strong>単利の計算</strong></a><br>元本・年利・年数から総額</div>"
      "<div class='card'><a href='compound.html'><strong>複利の計算</strong></a><br>複利の回数を選んで総額と単利との差を見る</div>"
      "<div class='card'><a href='accumulate.html'><strong>毎月積立の計算</strong></a><br>毎月一定額を積み立てた場合の将来額</div>"
      "<div class='card'><a href='years.html'><strong>目標額までの年数</strong></a><br>元本が目標額に届くまでの年数</div>"
      "<div class='card'><a href='rule72.html'><strong>2倍になる年数と72の法則</strong></a><br>年利から倍になる年数の目安</div>"
      "<h2>解説</h2><ul class='links'><li><a href='basics.html'>利息と利率の基本</a></li><li><a href='simple-vs-compound.html'>単利と複利の違い</a></li>"
      "<li><a href='pitfalls.html'>利息計算のつまずきやすい点</a></li><li><a href='glossary.html'>用語集</a></li></ul>")

    p("simple.html", "単利の計算ツール|元本・年利・年数から総額",
      "元本、年利、年数から、単利で計算した総額と利息の合計を求めます。",
      "<h1>単利の計算</h1><p>利息が元本にだけかかる方式です。</p>"
      "<div class='card'>" + inp("p", "元本", "1,000,000") + inp("r", "年利(%)", "2") + inp("n", "年数", "10") + btn +
      "<h2>式</h2><p>総額 = 元本 × (1 + 年利/100 × 年数)。毎年の利息は一定です。複利との違いは<a href='simple-vs-compound.html'>こちら</a>。税金・手数料は含みません。</p>"
      f"<script>{LIB}{SIMPLE_JS}</script>")

    p("compound.html", "複利の計算ツール|複利の回数を選んで総額を計算",
      "元本、年利、年数、複利の回数から、複利で計算した総額と、単利との差を求めます。",
      "<h1>複利の計算</h1><p>利息を元本に組み入れて、次の期間の利息を計算する方式です。</p>"
      "<div class='card'>" + inp("p", "元本", "1,000,000") + inp("r", "年利(%)", "2") + inp("n", "年数", "10") + sel + btn +
      "<h2>式</h2><p>総額 = 元本 × (1 + 年利/100 ÷ 回数)^(回数 × 年数)。複利の回数が多いほど、わずかに総額が増えます。</p>"
      "<p>実際の商品の利息の計算方法(日割り、端数処理など)は異なる場合があるため、公式の情報で確認してください。</p>"
      f"<script>{LIB}{COMP_JS}</script>")

    p("accumulate.html", "毎月積立の計算ツール|将来額の目安",
      "毎月一定額を積み立て、月ごとに複利で増えると仮定した場合の将来額と、積立合計を計算します。",
      "<h1>毎月積立の計算</h1><p>毎月末に一定額を積み立て、年利を12で割った月利で複利計算する簡易モデルです。</p>"
      "<div class='card'>" + inp("c", "毎月の積立額", "30,000") + inp("r", "年利(%)", "3") + inp("y", "年数", "20") + btn +
      "<h2>式</h2><p>将来額 = 積立額 × ((1 + 月利)^月数 − 1) ÷ 月利。月利は 年利/100 ÷ 12 です。年利が0%のときは 積立額 × 月数 です。</p>"
      "<p>これは単純化した計算です。実際の利率は変動することがあり、結果を保証するものではありません。</p>"
      f"<script>{LIB}{ACC_JS}</script>")

    p("years.html", "目標額までの年数の計算ツール|複利で何年かかるか",
      "元本と目標額、年利から、複利で目標額に届くまでのおおよその年数を計算します。",
      "<h1>目標額までの年数</h1><p>追加の入金なしで、元本だけが複利で増える場合の年数です。</p>"
      "<div class='card'>" + inp("p", "元本", "1,000,000") + inp("t", "目標額", "1,500,000") + inp("r", "年利(%)", "2") + sel + btn +
      "<h2>式</h2><p>年数 = ln(目標額 ÷ 元本) ÷ (回数 × ln(1 + 年利/100 ÷ 回数))。結果は小数第1位までの概算です。</p>"
      f"<script>{LIB}{YRS_JS}</script>")

    p("rule72.html", "2倍になる年数と72の法則|年利から目安を計算",
      "年利から元本が2倍になる年数を計算し、「72の法則」の目安と比べます。",
      "<h1>2倍になる年数と72の法則</h1><p>年利(年1回複利)から、元本が2倍になるまでの年数を求めます。</p>"
      "<div class='card'>" + inp("r", "年利(%)", "3") + btn +
      "<h2>72の法則とは</h2><p>72を年利(%)で割ると、2倍になる年数のおおよその目安になる、という経験則です。年利が低〜中程度のときに近い値になりますが、あくまで目安で、正確な値は上のツールの式で求めます。</p>"
      f"<script>{LIB}{R72_JS}</script>")

    p("basics.html", "利息と利率の基本|元本・年利・期間",
      "元本、利率、期間という利息計算の三要素と、年利・月利・日割りの関係を解説します。",
      "<h1>利息と利率の基本</h1>"
      "<h2>三つの要素</h2><p>利息は「元本」「利率」「期間」で決まります。元本はもとになるお金、利率は元本に対する利息の割合、期間は預ける(借りる)長さです。</p>"
      "<h2>年利と月利</h2><p>利率は多くの場合「年利(年あたり)」で示されます。1か月あたりに直すときは、おおまかに年利を12で割ります。日割りで計算する場合は、年利を365(または366)で割る考え方が使われることがありますが、方法は商品や契約ごとに異なります。</p>"
      "<h2>基本の式(1年・単利)</h2><p>利息 = 元本 × 年利 ÷ 100。元本100万円、年利2%なら、1年の利息は2万円です(税金などは含まない)。</p>"
      "<p>実際の取り扱いは公式の情報で確認してください。計算は<a href='simple.html'>単利のツール</a>で試せます。</p>")

    p("simple-vs-compound.html", "単利と複利の違い|仕組みを例で比較",
      "単利と複利の仕組みの違いを、同じ元本・年利・年数で比べた例と、期間が長いほど差が広がる理由で解説します。",
      "<h1>単利と複利の違い</h1>"
      "<p>単利は元本にだけ利息がつきます。複利は、ついた利息も元本に加えて、次の期間の利息を計算します。</p>"
      "<h2>例: 元本100万円・年利2%・3年(年1回)</h2>"
      "<table><tr><th>年</th><th>単利の総額</th><th>複利の総額</th></tr><tr><td>1年後</td><td>1,020,000円</td><td>1,020,000円</td></tr>"
      "<tr><td>2年後</td><td>1,040,000円</td><td>1,040,400円</td></tr><tr><td>3年後</td><td>1,060,000円</td><td>1,061,208円</td></tr></table>"
      "<p>1年目は同じで、2年目以降に差が出ます。期間が長くなるほど、差は広がります。</p>"
      "<h2>比べてみる</h2><p><a href='compound.html'>複利のツール</a>は、同条件の単利との差も表示します。</p>")

    p("pitfalls.html", "利息計算のつまずきやすい点|年利・回数・税金",
      "年利と月利の取り違え、複利の回数、積立の入金タイミング、税金や手数料を含まない点など、利息計算でよくあるつまずきを解説します。",
      "<h1>利息計算のつまずきやすい点</h1>"
      "<h2>1. 年利を月にそのまま使う</h2><p>年利3%を、毎月3%として計算してしまうと大きくずれます。月あたりにするときは年利を12で割ります。</p>"
      "<h2>2. 年利を12倍・12で割る関係は厳密ではない</h2><p>年利3%の月複利は、1年あたりの実質の増え方がちょうど3%にはなりません(わずかに多くなります)。表示の年利が何の回数を前提にしているかは、公式の情報で確認が必要です。</p>"
      "<h2>3. 積立のタイミング</h2><p>月初に入金するか月末かで、結果が少し変わります。本サイトの積立ツールは月末入金のモデルです。</p>"
      "<h2>4. 税金・手数料は別</h2><p>実際の受取額は、税金や手数料で変わることがあります。本サイトの結果には含まれません。</p>"
      "<h2>5. 将来の利率は変わりうる</h2><p>変動する利率の場合、同じ率が続く前提の計算結果は、あくまで目安です。</p>")

    terms = [("元本", "利息を計算するもとになる金額"), ("利率", "元本に対する利息の割合"), ("年利", "1年あたりで表した利率"), ("単利", "元本にだけ利息がつく方式"),
             ("複利", "利息も元本に加えて次の利息を計算する方式"), ("月利", "1か月あたりの利率。おおまかに年利÷12"), ("満期", "預ける・借りる期間の終わり"),
             ("積立", "毎月など定期的に一定額を入金すること"), ("72の法則", "72÷年利(%)で2倍になる年数を見積もる経験則"), ("将来額", "ある時点で見込まれる総額")]
    p("glossary.html", "利息計算の用語集",
      "元本・利率・年利・単利・複利・積立・72の法則など、利息計算に出てくる基本用語をまとめました。",
      "<h1>利息計算の用語集</h1><table><tr><th>用語</th><th>意味</th></tr>"
      + "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in terms) + "</table>"
      "<p><a href='basics.html'>基本</a> / <a href='simple-vs-compound.html'>単利と複利</a></p>")
