"""燃費・ガソリン代・移動コストの計算ツール。
規約: META と build(page, write) を持つ。出力は docs/fuel-calc/ 配下。"""
import html

META = dict(slug="fuel-calc", name="燃費・ガソリン代・移動コストの計算ツール",
            desc="燃費(km/L)の計算、走行距離からのガソリン代、往復や割り勘を含む移動コスト、2台の年間燃料費の比較を、ブラウザだけで計算できる無料ツール")
SITE = dict(name=META["name"], home="index.html")
NAV = [("燃費", "economy.html"), ("ガソリン代", "cost.html"), ("移動コスト", "trip.html"), ("年間比較", "compare.html"),
       ("式の解説", "formulas.html"), ("燃費が変わる要因", "factors.html"), ("間違いやすい点", "pitfalls.html"), ("用語", "terms.html"), ("FAQ", "faq.html")]
DISC = ("本サイトの計算結果は概算・目安です。実際の燃費は、運転のしかた、道路状況、積載、気温などで変わります。"
        "燃料価格や高速料金は、各スタンド・道路会社の公式情報で確認してください。"
        "入力した数値は、ブラウザの中だけで計算され、送信されません。")


def esc(s):
    return html.escape(s, quote=True)


# ---- Python側の基準実装(ブラウザ側JSと一致することを node で確認する) ----
def economy(km, liters):
    return km / liters


def liters_needed(km, kmpl):
    return km / kmpl


def fuel_cost(km, kmpl, price):
    return km / kmpl * price


def l_per_100km(kmpl):
    return 100 / kmpl


def trip_total(km, kmpl, price, toll, roundtrip):
    n = 2 if roundtrip else 1
    return n * (km / kmpl * price + toll)


def per_person(total, people):
    return total / people


def annual_cost(km_year, kmpl, price):
    return km_year / kmpl * price


def annual_diff(km_year, kmpl_a, kmpl_b, price):
    return annual_cost(km_year, kmpl_a, price) - annual_cost(km_year, kmpl_b, price)


# ---- ブラウザ側JS ----
CORE_JS = """
function economy(km,l){return km/l}
function litersNeeded(km,e){return km/e}
function fuelCost(km,e,p){return km/e*p}
function lPer100km(e){return 100/e}
function tripTotal(km,e,p,toll,rt){var n=rt?2:1;return n*(km/e*p+toll)}
function perPerson(t,n){return t/n}
function annualCost(k,e,p){return k/e*p}
function annualDiff(k,a,b,p){return annualCost(k,a,p)-annualCost(k,b,p)}
function fmt(x){if(!isFinite(x))return '-';var a=Math.abs(x);if(a!==0&&(a<0.001||a>=1e9))return x.toExponential(3);return (Math.round(x*100)/100).toLocaleString('ja-JP',{maximumFractionDigits:2})}
function yen(x){return Math.round(x).toLocaleString('ja-JP')+'円'}
function $(id){return document.getElementById(id)}
if(typeof module!=='undefined')module.exports={economy:economy,litersNeeded:litersNeeded,fuelCost:fuelCost,lPer100km:lPer100km,tripTotal:tripTotal,perPerson:perPerson,annualCost:annualCost,annualDiff:annualDiff};
"""

ECON_JS = """
if(typeof document!=='undefined'){
function run(){var km=parseFloat($('km').value),l=parseFloat($('l').value);
if(!(km>=0)||!(l>0)){$('out').textContent='距離と、0より大きい給油量を入力してください';return}
var e=economy(km,l);
$('out').innerHTML='燃費は <span class="big">'+fmt(e)+' km/L</span>'+(e>0?'(100kmあたり '+fmt(lPer100km(e))+' L)':'')}
$('btn').onclick=run;run()}
"""

COST_JS = """
if(typeof document!=='undefined'){
function run(){var km=parseFloat($('km').value),e=parseFloat($('e').value),p=parseFloat($('p').value);
if(!(km>=0)||!(e>0)||!(p>=0)){$('out').textContent='距離、0より大きい燃費、単価を入力してください';return}
$('out').innerHTML='<table><tr><th>必要な燃料</th><td>'+fmt(litersNeeded(km,e))+' L</td></tr><tr><th>ガソリン代の目安</th><td><span class="big">'+yen(fuelCost(km,e,p))+'</span></td></tr><tr><th>1kmあたり</th><td>'+fmt(p/e)+' 円</td></tr></table>'}
$('btn').onclick=run;run()}
"""

TRIP_JS = """
if(typeof document!=='undefined'){
function run(){var km=parseFloat($('km').value),e=parseFloat($('e').value),p=parseFloat($('p').value),toll=parseFloat($('toll').value)||0,n=parseInt($('n').value,10),rt=$('rt').checked;
if(!(km>=0)||!(e>0)||!(p>=0)||!(toll>=0)||!(n>=1)){$('out').textContent='入力を確認してください(人数は1以上、燃費は0より大きい数)';return}
var t=tripTotal(km,e,p,toll,rt);
$('out').innerHTML='<table><tr><th>合計(燃料代+料金)</th><td><span class="big">'+yen(t)+'</span></td></tr><tr><th>1人あたり('+n+'人で割った場合)</th><td>'+yen(perPerson(t,n))+'</td></tr></table>'}
$('btn').onclick=run;run()}
"""

CMP_JS = """
if(typeof document!=='undefined'){
function run(){var k=parseFloat($('k').value),a=parseFloat($('a').value),b=parseFloat($('b').value),p=parseFloat($('p').value);
if(!(k>=0)||!(a>0)||!(b>0)||!(p>=0)){$('out').textContent='年間距離、0より大きい燃費2つ、単価を入力してください';return}
var d=annualDiff(k,a,b,p);
$('out').innerHTML='<table><tr><th>Aの年間燃料費</th><td>'+yen(annualCost(k,a,p))+'</td></tr><tr><th>Bの年間燃料費</th><td>'+yen(annualCost(k,b,p))+'</td></tr><tr><th>差(A − B)</th><td><span class="big">'+yen(d)+'</span></td></tr></table><p class="note">'+(d>0?'Bのほうが年間で約'+yen(d)+'安い計算です。':d<0?'Aのほうが年間で約'+yen(-d)+'安い計算です。':'差はありません。')+'</p>'}
$('btn').onclick=run;run()}
"""


def script(extra):
    return f"<script>{CORE_JS}{extra}</script>"


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)

    p("index.html", "燃費・ガソリン代・移動コストの計算ツール|km/L・往復・割り勘",
      "満タン法の燃費計算、走行距離からのガソリン代、往復と割り勘を含む移動コスト、2台の年間燃料費の比較をブラウザだけで計算できます。",
      "<h1>燃費・ガソリン代・移動コストの計算ツール</h1><p>車での移動にかかる燃料代を見積もるための計算ツールと解説です。入力した数字は、ブラウザの中だけで計算され、送信されません。</p>"
      "<div class='card'><a href='economy.html'><strong>燃費の計算</strong></a><br>走行距離と給油量からkm/Lを求める</div>"
      "<div class='card'><a href='cost.html'><strong>ガソリン代の計算</strong></a><br>距離・燃費・単価から燃料代を求める</div>"
      "<div class='card'><a href='trip.html'><strong>移動コストの計算</strong></a><br>往復・高速料金・人数割りを含める</div>"
      "<div class='card'><a href='compare.html'><strong>2台の年間燃料費の比較</strong></a><br>燃費の違いが年間でいくらの差になるか</div>"
      "<h2>解説</h2><ul class='links'><li><a href='formulas.html'>式の解説</a></li><li><a href='factors.html'>燃費が変わる要因</a></li>"
      "<li><a href='pitfalls.html'>間違いやすい点</a></li><li><a href='terms.html'>用語集</a></li><li><a href='faq.html'>よくある質問</a></li></ul>")

    p("economy.html", "燃費の計算|満タン法でkm/Lを求める",
      "走行距離と給油量から燃費(km/L)を計算します。100kmあたりの消費量も表示します。",
      "<h1>燃費の計算(満タン法)</h1><p>満タンにしてから、次に満タンにするまでの走行距離と給油量を入力してください。</p>"
      "<div class='card'><label>走行距離(km) <input id='km' type='number' value='420' min='0' step='any'></label><br>"
      "<label>給油量(L) <input id='l' type='number' value='30' min='0' step='any'></label><br><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<p class='note'>満タンの基準(給油機が止まる位置)をそろえると、誤差が小さくなります。カタログの燃費値とは測り方が違うため、同じ数字にはなりません。</p>"
      "<p><a href='cost.html'>ガソリン代の計算へ</a> / <a href='factors.html'>燃費が変わる要因</a></p>" + script(ECON_JS))

    p("cost.html", "ガソリン代の計算|距離・燃費・単価から燃料代",
      "走行距離、燃費(km/L)、ガソリン単価(円/L)から、必要な燃料と燃料代の目安を計算します。",
      "<h1>ガソリン代の計算</h1><p>単価は説明用の初期値です。実際の価格は、スタンドの表示や公式の情報で確認してください。</p>"
      "<div class='card'><label>距離(km) <input id='km' type='number' value='100' min='0' step='any'></label><br>"
      "<label>燃費(km/L) <input id='e' type='number' value='15' min='0' step='any'></label><br>"
      "<label>単価(円/L) <input id='p' type='number' value='170' min='0' step='any'></label><br><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<p><a href='trip.html'>往復や料金を含める</a> / <a href='formulas.html'>式の解説</a></p>" + script(COST_JS))

    p("trip.html", "移動コストの計算|往復・高速料金・人数割り",
      "片道距離、燃費、単価、高速料金などから、往復を含めた移動コストと1人あたりの金額を計算します。",
      "<h1>移動コストの計算</h1><p>燃料代と、片道ぶんの料金(高速道路・駐車場など)を足して、人数で割った目安を出します。</p>"
      "<div class='card'><label>片道の距離(km) <input id='km' type='number' value='150' min='0' step='any'></label><br>"
      "<label>燃費(km/L) <input id='e' type='number' value='15' min='0' step='any'></label><br>"
      "<label>単価(円/L) <input id='p' type='number' value='170' min='0' step='any'></label><br>"
      "<label>片道の料金(円) <input id='toll' type='number' value='0' min='0' step='any'></label><br>"
      "<label>人数 <input id='n' type='number' value='2' min='1' step='1'></label><br>"
      "<label><input id='rt' type='checkbox' checked> 往復で計算する</label><br><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<p class='note'>料金は、ここでは片道ぶんをそのまま往復で2倍します。実際の料金・割引は、道路会社などの公式情報で確認してください。車の維持費(保険・税・整備・減価)は含みません。</p>"
      + script(TRIP_JS))

    p("compare.html", "2台の年間燃料費の比較|燃費の違いはいくらの差か",
      "年間の走行距離と2台の燃費から、年間の燃料費の差を計算します。買い替えの検討材料にどうぞ。",
      "<h1>2台の年間燃料費の比較</h1><p>燃費の違いが、年間の燃料費でどれくらいの差になるかを見ます。</p>"
      "<div class='card'><label>年間の走行距離(km) <input id='k' type='number' value='8000' min='0' step='any'></label><br>"
      "<label>Aの燃費(km/L) <input id='a' type='number' value='12' min='0' step='any'></label><br>"
      "<label>Bの燃費(km/L) <input id='b' type='number' value='20' min='0' step='any'></label><br>"
      "<label>単価(円/L) <input id='p' type='number' value='170' min='0' step='any'></label><br><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<p class='note'>購入価格、税金、保険、整備費などは含みません。買い替えの判断は、燃料費以外も含めて総合的に行ってください。</p>" + script(CMP_JS))

    p("formulas.html", "燃費・ガソリン代の式|km/LとL/100kmの関係",
      "燃費、必要燃料、ガソリン代、100kmあたりの消費量(L/100km)の式を整理しました。",
      "<h1>燃費・ガソリン代の式</h1>"
      "<h2>基本の式</h2><ol><li><strong>燃費(km/L) = 走行距離(km) ÷ 給油量(L)</strong></li><li><strong>必要な燃料(L) = 距離(km) ÷ 燃費(km/L)</strong></li>"
      "<li><strong>燃料代 = 必要な燃料(L) × 単価(円/L)</strong></li><li><strong>L/100km = 100 ÷ 燃費(km/L)</strong></li></ol>"
      "<h2>計算例(説明用の数字)</h2><p>420km走って30L入ったなら、燃費は 420 ÷ 30 = 14km/L。この燃費で100km走ると 100 ÷ 14 ≒ 7.14L、単価が170円/Lなら約1,214円です。</p>"
      "<h2>1kmあたりの燃料代</h2><p>単価 ÷ 燃費で求まります。170円/L ÷ 14km/L ≒ 12.1円/kmです。</p>"
      "<h2>km/LとL/100kmは逆数の関係</h2><p>国によってはL/100kmで表します。数字が大きいほど燃費が悪い点が、km/Lと逆です。</p>"
      "<p><a href='economy.html'>燃費の計算</a> / <a href='cost.html'>ガソリン代の計算</a></p>")

    p("factors.html", "燃費が変わる要因|運転・道路・積載・季節",
      "同じ車でも燃費が変わる一般的な要因(発進・加速、渋滞、積載、タイヤの空気圧、気温、エアコン)を整理しました。",
      "<h1>燃費が変わる要因</h1><p>一般に知られている要因を挙げます。影響の大きさは車種や条件で変わるため、数字は示しません。</p>"
      "<ul><li><strong>発進と加速</strong>: 急な発進や加速が多いと、燃料を多く使う傾向があります</li>"
      "<li><strong>渋滞・停止の多さ</strong>: 発進と停止の繰り返しや、長いアイドリングは燃費を下げる方向に働きます</li>"
      "<li><strong>速度</strong>: 速度が高いほど空気抵抗が増える傾向があります</li>"
      "<li><strong>積載</strong>: 荷物や人が増えて重くなると、燃費は下がる方向に働きます。ルーフ上の荷物は空気抵抗も増やします</li>"
      "<li><strong>タイヤの空気圧</strong>: 適正値より低いと転がり抵抗が増えます。適正値は車の取扱説明書で確認してください</li>"
      "<li><strong>気温・季節</strong>: 寒い時期は暖機やエアコンの使用などで燃費が悪くなりやすいといわれます</li>"
      "<li><strong>エアコンの使用</strong>: 使用中はエンジンの負担が増える傾向があります</li></ul>"
      "<p>運転は安全と交通ルールが最優先です。燃費のために無理な運転をしないでください。</p>")

    p("pitfalls.html", "燃費・ガソリン代計算で間違いやすい点",
      "カタログ燃費と実燃費の違い、満タン法の誤差、往復の数え忘れ、燃料以外の費用など、よくある間違いをまとめました。",
      "<h1>間違いやすい点</h1>"
      "<h2>1. カタログの燃費をそのまま使う</h2><p>カタログの値は決められた条件での測定値です。実際の燃費とは差が出るため、ガソリン代の見積もりには自分の実燃費を使うと現実に近づきます。</p>"
      "<h2>2. 満タンの基準が毎回違う</h2><p>給油のたびに入れ方が違うと、1回の燃費は大きくぶれます。複数回の合計(総距離 ÷ 総給油量)で見ると安定します。</p>"
      "<h2>3. 往復を数え忘れる</h2><p>片道の距離で計算して、帰りぶんを入れ忘れる間違いがあります。<a href='trip.html'>移動コストの計算</a>は往復の切り替えができます。</p>"
      "<h2>4. 燃料代だけを移動コストとみなす</h2><p>高速料金や駐車場代に加え、車を持つ費用(保険、税金、整備、減価など)は別にかかります。</p>"
      "<h2>5. 単価の古い数字を使う</h2><p>燃料価格は変動します。計算の前に、最新の価格を公式の情報などで確認してください。</p>"
      "<h2>6. km/Lと L/100km の混同</h2><p>数字の大小の意味が逆です。単位を必ず確認してください。</p>")

    terms = [("燃費", "一定量の燃料で走れる距離。日本ではkm/Lで表すことが多い"),
             ("満タン法", "満タンから満タンまでの走行距離と給油量から燃費を出す方法"),
             ("L/100km", "100km走るのに使う燃料のリットル数。km/Lの逆数にあたる"),
             ("カタログ燃費", "決められた条件で測定された燃費。実際の燃費とは差が出る"),
             ("実燃費", "実際に走って測った燃費"), ("単価", "燃料1リットルあたりの価格(円/L)"),
             ("アイドリング", "車が止まった状態でエンジンが回っていること"), ("維持費", "燃料代のほか、保険・税金・整備など車を持つ費用")]
    trs = "".join(f"<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>" for a, b in terms)
    p("terms.html", "燃費・ガソリン代の用語集|満タン法・L/100km",
      "燃費、満タン法、L/100km、カタログ燃費、実燃費などの用語を短く説明します。",
      f"<h1>燃費・ガソリン代の用語集</h1><table><tr><th>用語</th><th>意味</th></tr>{trs}</table><p><a href='formulas.html'>式の解説</a></p>")

    p("faq.html", "燃費・ガソリン代のよくある質問",
      "実燃費の測り方、往復の計算、割り勘の考え方、燃料代以外の費用など、よくある疑問に答えます。",
      "<h1>よくある質問</h1>"
      "<h2>実燃費はどう測りますか?</h2><p>満タンにして走行距離計をリセットし、次に満タンにしたときの給油量で割ります。<a href='economy.html'>燃費の計算</a>が使えます。</p>"
      "<h2>ガソリン代の目安を出すには?</h2><p>距離 ÷ 燃費 × 単価です。<a href='cost.html'>ガソリン代の計算</a>をご利用ください。</p>"
      "<h2>割り勘はどう考えればよいですか?</h2><p>このサイトでは、合計を人数で割る単純な方法を示しています。実際の負担の決め方は、同乗者どうしで話し合ってください。</p>"
      "<h2>この金額で必ず足りますか?</h2><p>概算の目安です。渋滞や寄り道、価格の変動で増減します。余裕をもって見積もってください。</p>"
      "<h2>入力した数字は送信されますか?</h2><p>いいえ。計算はブラウザの中だけで行われます。</p>")
