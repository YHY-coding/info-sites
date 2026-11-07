"""消費電力と電気代の計算ツール集(式の解説つき)。
規約: META と build(page, write) を持つ。出力は docs/electric-calc/ 配下。"""
import html
import json

META = dict(slug="electric-calc", name="電気代・消費電力の計算ツール集",
            desc="消費電力(W)と使用時間から電気代を計算。家電の買い替え比較、W・kWh・A・Vの換算、ブレーカー容量の目安を、ブラウザだけで計算できる無料ツール")
SITE = dict(name=META["name"], home="index.html")
NAV = [("電気代", "cost.html"), ("家電別", "appliances.html"), ("買い替え比較", "compare.html"), ("単位換算", "units.html"),
       ("アンペア", "breaker.html"), ("式の解説", "formulas.html"), ("節電のコツ", "tips.html"), ("用語", "terms.html"), ("FAQ", "faq.html")]
DISC = ("本サイトの計算結果は概算・目安です。電気料金の単価・基本料金・燃料費調整などは契約や時期で変わります。"
        "実際の金額は、検針票・契約中の電力会社の公式情報で確認してください。"
        "家電の消費電力は機種・使い方で変わるため、本体の表示や取扱説明書で確認してください。"
        "入力した数値は、ブラウザの中だけで計算され、送信されません。")

DEFAULT_PRICE = 30.0   # 円/kWh。入力欄の初期値(仮の値。請求書の単価で置き換えて使う)

# 家電の例: (キー, 表示名, 消費電力W(使用時の目安), 1日の使用時間h(目安), 備考)
APPLIANCES = [
    ("led", "LED電球(1個)", 8, 5, "明るさ相当の白熱電球より小さい"),
    ("tv", "液晶テレビ", 100, 5, "画面サイズで変わる"),
    ("pc", "ノートパソコン", 40, 6, "負荷が高いと増える"),
    ("fridge", "冷蔵庫(平均)", 40, 24, "実際は断続運転。年間の消費電力量表示から平均を出す方法もある"),
    ("ac", "エアコン(冷暖房の平均的な運転時)", 500, 8, "設定温度・外気温・部屋の広さで大きく変わる"),
    ("heater", "電気ストーブ", 800, 4, "発熱が主目的の機器は消費電力が大きい"),
    ("dryer", "ヘアドライヤー", 1200, 0.2, "強風時の定格に近い"),
    ("micro", "電子レンジ", 1000, 0.3, "加熱出力ではなく消費電力で見る"),
    ("kettle", "電気ケトル", 1200, 0.3, "沸騰させる時間は短い"),
    ("rice", "炊飯器(炊飯時)", 700, 1, "保温時は消費電力が小さい"),
    ("washer", "洗濯機", 300, 1, "乾燥機能つきは別に大きくなる"),
    ("router", "Wi-Fiルーター", 10, 24, "常時通電する機器の例"),
]


def esc(s):
    return html.escape(s, quote=True)


# ---- Python側の基準実装(ブラウザ側JSと一致することを node で確認する) ----
def kwh_per_month(watts, hours_per_day, days):
    """消費電力量(kWh) = W × 時間/日 × 日数 ÷ 1000"""
    return watts * hours_per_day * days / 1000


def cost_yen(kwh, price_per_kwh):
    return kwh * price_per_kwh


def annual_cost(watts, hours_per_day, price_per_kwh):
    return kwh_per_month(watts, hours_per_day, 365) * price_per_kwh


def payback_years(extra_price, saving_per_year):
    """買い替えで増える購入額 ÷ 年間の電気代の減り。減らない場合は None。"""
    if saving_per_year <= 0:
        return None
    return extra_price / saving_per_year


def watts_from_va(volts, amps):
    return volts * amps


def amps_from_w(watts, volts):
    return watts / volts


def wh_to_kwh(wh):
    return wh / 1000


def kwh_to_mj(kwh):
    return kwh * 3.6


# ---- ブラウザ側JS ----
CORE_JS = """
var DATA=__DATA__;
function kwhPer(w,h,d){return w*h*d/1000}
function costYen(k,p){return k*p}
function annualCost(w,h,p){return kwhPer(w,h,365)*p}
function payback(extra,saving){return saving<=0?null:extra/saving}
function wattsFromVA(v,a){return v*a}
function ampsFromW(w,v){return w/v}
function whToKwh(wh){return wh/1000}
function kwhToMj(k){return k*3.6}
function fmt(x){if(!isFinite(x))return '-';var a=Math.abs(x);if(a!==0&&(a<0.001||a>=1e9))return x.toExponential(3);return (Math.round(x*100)/100).toLocaleString('ja-JP',{maximumFractionDigits:2})}
function yen(x){return Math.round(x).toLocaleString('ja-JP')+'円'}
function $(id){return document.getElementById(id)}
if(typeof module!=='undefined')module.exports={kwhPer:kwhPer,costYen:costYen,annualCost:annualCost,payback:payback,wattsFromVA:wattsFromVA,ampsFromW:ampsFromW,whToKwh:whToKwh,kwhToMj:kwhToMj};
"""

COST_JS = """
if(typeof document!=='undefined'){
function run(){var w=parseFloat($('w').value),h=parseFloat($('h').value),d=parseFloat($('d').value),p=parseFloat($('p').value),n=parseFloat($('n').value);
if(!(w>=0)||!(h>=0&&h<=24)||!(d>=0)||!(p>=0)||!(n>=1)){$('out').textContent='入力を確認してください(使用時間は0〜24時間)';return}
var k=kwhPer(w,h,d)*n;
$('out').innerHTML='<p class="big">'+yen(costYen(k,p))+'</p><table><tr><th>期間の消費電力量</th><td>'+fmt(k)+' kWh</td></tr>'
+'<tr><th>1日あたりの電気代</th><td>'+yen(costYen(kwhPer(w,h,1)*n,p))+'</td></tr>'
+'<tr><th>1年(365日同じ使い方)の電気代</th><td>'+yen(annualCost(w,h,p)*n)+'</td></tr></table>'}
$('btn').onclick=run;run()}
"""

APP_JS = """
if(typeof document!=='undefined'){
var A=__APPS__;
function run(){var p=parseFloat($('p').value),h=parseFloat($('h').value),w=parseFloat($('w').value),d=parseFloat($('d').value);
if(!(p>=0)||!(h>=0&&h<=24)||!(w>=0)||!(d>=0)){$('out').textContent='入力を確認してください';return}
var k=kwhPer(w,h,d);
$('out').innerHTML='<table><tr><th>期間の消費電力量</th><td>'+fmt(k)+' kWh</td></tr><tr><th>期間の電気代</th><td>'+yen(costYen(k,p))+'</td></tr><tr><th>1年(365日)の電気代</th><td>'+yen(annualCost(w,h,p))+'</td></tr></table>'}
$('sel').onchange=function(){var a=A[$('sel').value];$('w').value=a[0];$('h').value=a[1];run()};
$('btn').onclick=run;$('sel').onchange()}
"""

COMPARE_JS = """
if(typeof document!=='undefined'){
function run(){var ow=parseFloat($('ow').value),nw=parseFloat($('nw').value),h=parseFloat($('h').value),p=parseFloat($('p').value),x=parseFloat($('x').value);
if(!(ow>=0)||!(nw>=0)||!(h>=0&&h<=24)||!(p>=0)||!(x>=0)){$('out').textContent='入力を確認してください';return}
var o=annualCost(ow,h,p),n=annualCost(nw,h,p),s=o-n,pb=payback(x,s);
$('out').innerHTML='<table><tr><th>今の機器の年間電気代</th><td>'+yen(o)+'</td></tr><tr><th>新しい機器の年間電気代</th><td>'+yen(n)+'</td></tr><tr><th>年間の差</th><td>'+yen(s)+'</td></tr>'
+'<tr><th>購入額が回収できる年数の目安</th><td>'+(pb===null?'電気代は減らないため回収できません':fmt(pb)+' 年')+'</td></tr></table>'}
$('btn').onclick=run;run()}
"""

UNITS_JS = """
if(typeof document!=='undefined'){
function run(){var w=parseFloat($('w').value),wh=parseFloat($('wh').value),v=parseFloat($('v').value),a=parseFloat($('a').value);
if(!(w>=0)||!(wh>=0)||!(v>0)||!(a>=0)){$('out').textContent='入力を確認してください';return}
$('out').innerHTML='<table><tr><th>'+fmt(w)+' W は</th><td>'+fmt(w/1000)+' kW</td></tr>'
+'<tr><th>'+fmt(wh)+' Wh は</th><td>'+fmt(whToKwh(wh))+' kWh(= '+fmt(kwhToMj(whToKwh(wh)))+' MJ)</td></tr>'
+'<tr><th>'+fmt(v)+' V × '+fmt(a)+' A は</th><td>'+fmt(wattsFromVA(v,a))+' W</td></tr>'
+'<tr><th>'+fmt(w)+' W を '+fmt(v)+' V で使うと</th><td>約 '+fmt(ampsFromW(w,v))+' A</td></tr></table>'}
$('btn').onclick=run;run()}
"""

BREAKER_JS = """
if(typeof document!=='undefined'){
function run(){var v=parseFloat($('v').value),c=parseFloat($('c').value),lines=$('lines').value.split('\\n'),tw=0,h='';
if(!(v>0)||!(c>0)){$('out').textContent='入力を確認してください';return}
for(var i=0;i<lines.length;i++){var s=lines[i].trim();if(!s)continue;var m=s.match(/([0-9]+(?:\\.[0-9]+)?)\\s*$/);
if(m){tw+=parseFloat(m[1]);h+='<tr><td>'+esc(s)+'</td></tr>'}}
var cap=wattsFromVA(v,c),a=ampsFromW(tw,v);
$('out').innerHTML='<table><tr><th>同時に使う機器の合計</th><td>'+fmt(tw)+' W(約 '+fmt(a)+' A)</td></tr><tr><th>契約アンペアの上限の目安</th><td>'+fmt(cap)+' W('+fmt(c)+' A)</td></tr>'
+'<tr><th>判定の目安</th><td>'+(a>c?'上限を超える見込み(ブレーカーが落ちる可能性が高い)':(a>c*0.8?'上限の8割を超える(余裕が少ない)':'上限内の見込み'))+'</td></tr></table>'+(h?'<table>'+h+'</table>':'')}
function esc(s){return s.replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
$('btn').onclick=run;run()}
"""


def script(extra, apps=False):
    js = CORE_JS.replace("__DATA__", json.dumps({}, ensure_ascii=False))
    if apps:
        extra = extra.replace("__APPS__", json.dumps({k: [w, h] for k, _, w, h, _ in APPLIANCES}))
    return f"<script>{js}{extra}</script>"


def n(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)
    PRICE_NOTE = ("<p class='note'>初期値の電力量単価は、計算例のための仮の値です。実際の単価は、検針票や契約中の電力会社の公式サイトで確認して入力してください。</p>")

    p("index.html", "電気代・消費電力の計算ツール集|W・kWh・電気代",
      "消費電力(W)と使用時間から電気代を計算。家電別の目安、買い替え比較、W・kWh・A・Vの換算、ブレーカー容量の目安をブラウザだけで計算できます。",
      "<h1>電気代・消費電力の計算ツール集</h1><p>消費電力と使う時間から電気代を出す基本式を、ツールと解説で整理しました。入力した数字は、ブラウザの中だけで計算され、送信されません。</p>"
      "<div class='card'><a href='cost.html'><strong>電気代の計算</strong></a><br>消費電力(W)・使用時間・単価から、電力量(kWh)と電気代を計算</div>"
      "<div class='card'><a href='appliances.html'><strong>家電別の電気代の目安</strong></a><br>家電の例を選んで、消費電力と使用時間をあらかじめ入力</div>"
      "<div class='card'><a href='compare.html'><strong>買い替え比較</strong></a><br>今の機器と新しい機器の年間電気代の差と、購入額の回収年数の目安</div>"
      "<div class='card'><a href='units.html'><strong>単位換算(W・kWh・V・A)</strong></a><br>W・kW、Wh・kWh・MJ、電圧と電流から電力への換算</div>"
      "<div class='card'><a href='breaker.html'><strong>契約アンペアと同時使用の目安</strong></a><br>同時に使う機器の合計が、契約アンペアの上限に収まるかを確認</div>"
      "<h2>解説</h2><ul class='links'><li><a href='formulas.html'>電気代の式と考え方</a></li><li><a href='tips.html'>節電のコツ(一般的な考え方)</a></li>"
      "<li><a href='terms.html'>電気の用語集</a></li><li><a href='faq.html'>よくある質問</a></li></ul>")

    p("cost.html", "電気代の計算|消費電力(W)と使用時間から",
      "消費電力(W)、1日の使用時間、日数、電力量単価を入力すると、消費電力量(kWh)と電気代の目安を計算します。",
      "<h1>電気代の計算</h1><p>電気代の目安 = 消費電力(W) × 使用時間(h) ÷ 1000 × 電力量単価(円/kWh)</p>"
      "<div class='card'><label>消費電力(W) <input id='w' type='number' value='100' min='0' step='any'></label><br>"
      "<label>1日の使用時間(時間) <input id='h' type='number' value='5' min='0' max='24' step='any'></label><br>"
      "<label>使用日数 <input id='d' type='number' value='30' min='0' step='1'></label><br>"
      "<label>台数 <input id='n' type='number' value='1' min='1' step='1'></label><br>"
      f"<label>電力量単価(円/kWh) <input id='p' type='number' value='{DEFAULT_PRICE:g}' min='0' step='any'></label><br><br><button id='btn'>計算する</button></div>"
      "<div id='out' class='card'></div>" + PRICE_NOTE +
      "<h2>この計算に含まれないもの</h2><ul><li>基本料金・最低料金など、使った量によらない料金</li><li>燃料費調整額・再エネ賦課金など、時期で変わる項目</li>"
      "<li>機器の消費電力は運転状態で変わります。表示されたW数は最大(定格)の場合があり、実際の平均はそれより小さいことが多いです</li></ul>"
      "<p><a href='formulas.html'>式の考え方</a> / <a href='appliances.html'>家電別の目安</a></p>" + script(COST_JS))

    iopts = "".join(f"<option value='{k}'>{esc(nm)}</option>" for k, nm, *_ in APPLIANCES)
    rows = "".join(f"<tr><th>{esc(nm)}</th><td>{w}W</td><td>{n(h)}時間</td><td>{n(kwh_per_month(w, h, 30))}kWh</td><td>{esc(note)}</td></tr>" for _, nm, w, h, note in APPLIANCES)
    p("appliances.html", "家電別の電気代の目安|消費電力と使用時間の例",
      "テレビ・エアコン・冷蔵庫など家電の消費電力と使用時間の例を選んで、電気代の目安を計算します。数値は一般的な目安です。",
      "<h1>家電別の電気代の目安</h1><p>家電の例を選ぶと、消費電力と使用時間の例が入ります。実際の機器に合わせて数字を書き換えてください。</p>"
      f"<div class='card'><label>家電の例 <select id='sel'>{iopts}</select></label><br>"
      "<label>消費電力(W) <input id='w' type='number' value='100' min='0' step='any'></label><br>"
      "<label>1日の使用時間(時間) <input id='h' type='number' value='5' min='0' max='24' step='any'></label><br>"
      "<label>使用日数 <input id='d' type='number' value='30' min='0' step='1'></label><br>"
      f"<label>電力量単価(円/kWh) <input id='p' type='number' value='{DEFAULT_PRICE:g}' min='0' step='any'></label><br><br><button id='btn'>計算する</button></div>"
      "<div id='out' class='card'></div>" + PRICE_NOTE +
      "<h2>家電の例と、30日あたりの消費電力量</h2>"
      f"<table><tr><th>家電</th><th>消費電力の例</th><th>使用時間の例</th><th>30日の電力量</th><th>メモ</th></tr>{rows}</table>"
      "<p class='note'>表の数字は計算のための例であり、実際の機器の値ではありません。機種ごとの値は、本体のラベルや取扱説明書で確認してください。</p>"
      + script(APP_JS, apps=True))

    p("compare.html", "家電の買い替え比較|電気代の差と回収年数の目安",
      "今の機器と新しい機器の消費電力から、年間の電気代の差と、購入額の差額が電気代の節約で回収できる年数の目安を計算します。",
      "<h1>買い替え比較</h1><p>同じ使い方をした場合の年間電気代を比べ、購入額の差が何年で回収できるかの目安を出します。</p>"
      "<div class='card'><label>今の機器の消費電力(W) <input id='ow' type='number' value='150' min='0' step='any'></label><br>"
      "<label>新しい機器の消費電力(W) <input id='nw' type='number' value='80' min='0' step='any'></label><br>"
      "<label>1日の使用時間(時間) <input id='h' type='number' value='8' min='0' max='24' step='any'></label><br>"
      f"<label>電力量単価(円/kWh) <input id='p' type='number' value='{DEFAULT_PRICE:g}' min='0' step='any'></label><br>"
      "<label>新しい機器の購入額(円・下取り等を差し引いた実質) <input id='x' type='number' value='50000' min='0' step='any'></label><br><br><button id='btn'>比較する</button></div>"
      "<div id='out' class='card'></div>" + PRICE_NOTE +
      "<h2>見落としやすい点</h2><ul><li>電気代以外の理由(故障の恐れ、性能、安全性、使い勝手)も、買い替えの判断材料になります</li>"
      "<li>消費電力の表示は測定条件が決まっています。実際の使い方で同じ差が出るとは限りません</li>"
      "<li>電力量単価は将来変わる可能性があり、回収年数は目安です</li>"
      "<li>古い機器の処分費用や、新しい機器の設置費用は、購入額に含めて入力してください</li></ul>"
      + script(COMPARE_JS))

    p("units.html", "電気の単位換算|W・kW・Wh・kWh・V・A",
      "ワットとキロワット、ワット時とキロワット時、電圧と電流から電力、電力から電流への換算を計算します。",
      "<h1>電気の単位換算</h1>"
      "<div class='card'><label>電力(W) <input id='w' type='number' value='1500' min='0' step='any'></label><br>"
      "<label>電力量(Wh) <input id='wh' type='number' value='2500' min='0' step='any'></label><br>"
      "<label>電圧(V) <input id='v' type='number' value='100' min='0.1' step='any'></label><br>"
      "<label>電流(A) <input id='a' type='number' value='10' min='0' step='any'></label><br><br><button id='btn'>換算する</button></div><div id='out' class='card'></div>"
      "<h2>換算の前提</h2><ul><li>W = V × A は、電圧と電流が同じ向きで変化する単純な場合(抵抗負荷)の式です。モーターや電子機器では力率が関係し、実際の消費電力はこれより小さくなることがあります</li>"
      "<li>1kWh = 3.6MJ(メガジュール)です</li>"
      "<li>家庭用コンセントの電圧は、日本では一般に100Vですが、機器・設備により異なる場合があります</li></ul>"
      "<p><a href='terms.html'>用語集</a> / <a href='formulas.html'>式の解説</a></p>" + script(UNITS_JS))

    p("breaker.html", "契約アンペアと同時使用の目安|ブレーカーが落ちる条件",
      "同時に使う機器の消費電力の合計から必要な電流を計算し、契約アンペアの上限と比べます。ブレーカーが落ちる仕組みの解説つき。",
      "<h1>契約アンペアと同時使用の目安</h1><p>同時に使う機器を1行に1つ、最後に消費電力(W)の数字を付けて入力してください。</p>"
      "<div class='card'><label>電圧(V) <input id='v' type='number' value='100' min='1' step='any'></label><br>"
      "<label>契約アンペア(A) <input id='c' type='number' value='30' min='1' step='any'></label><br>"
      "<label>同時に使う機器(1行に1つ・末尾にW数)<br><textarea id='lines' rows='6' cols='36'>エアコン 600\nドライヤー 1200\n電子レンジ 1000\n冷蔵庫 60</textarea></label><br><br><button id='btn'>確認する</button></div><div id='out' class='card'></div>"
      "<h2>ブレーカーが落ちる仕組み</h2><ul><li>電気を同時にたくさん使って、契約している電流の上限を超えると、アンペアブレーカーが落ちて電気が止まります</li>"
      "<li>落ちたときは、使っている機器を減らしてから、ブレーカーを戻します</li>"
      "<li>契約アンペアの種類や、そもそもアンペア制の契約かどうかは、地域・契約によって異なります。契約内容は検針票や電力会社の公式情報で確認してください</li>"
      "<li>ブレーカーや分電盤の工事・交換は、資格のある電気工事の専門家に依頼してください。自分で分解しないでください</li></ul>"
      "<p class='note'>この判定は単純な足し算の目安です。モーターを使う機器の起動時は、定格より大きな電流が一時的に流れることがあります。</p>"
      + script(BREAKER_JS))

    p("formulas.html", "電気代の式と考え方|W・kWh・単価の関係",
      "消費電力(W)、電力量(kWh)、電力量単価から電気代が決まる仕組みと、よくある計算の間違いを整理しました。",
      "<h1>電気代の式と考え方</h1>"
      "<h2>基本の3つの式</h2><ol><li><strong>電力量(kWh)= 消費電力(kW)× 使用時間(h)</strong>。W表示の場合は1000で割ってkWにします</li>"
      "<li><strong>電気代(円)= 電力量(kWh)× 電力量単価(円/kWh)</strong></li>"
      "<li><strong>電力(W)= 電圧(V)× 電流(A)</strong>(抵抗負荷の場合)</li></ol>"
      "<h2>計算例(数字は説明用の仮の値)</h2><p>消費電力100Wの機器を1日5時間、30日使うと、100 × 5 × 30 ÷ 1000 = 15kWhです。電力量単価が仮に30円/kWhなら、15 × 30 = 450円になります。</p>"
      "<h2>よくある間違い</h2><ul><li><strong>WとWhを混同する</strong>: Wは「ある瞬間の大きさ」、Whは「使った量」です。時間をかけて初めて電力量になります</li>"
      "<li><strong>kWを忘れる</strong>: 100Wは0.1kWです。1000で割るのを忘れると、1000倍の金額になります</li>"
      "<li><strong>最大値で計算し続ける</strong>: エアコンや冷蔵庫は、一定の消費電力で動き続けません。定格のW数で計算すると、実際より大きくなりがちです</li>"
      "<li><strong>基本料金を足し忘れる</strong>: 請求額には、使った量によらない項目や調整項目が含まれます</li></ul>"
      "<h2>実際の消費電力を調べるには</h2><ul><li>本体のラベルや取扱説明書の「消費電力」「定格」「年間消費電力量」の表示を見る</li>"
      "<li>コンセントに挟んで使うワットチェッカー(電力量計)で実測する</li></ul>"
      "<p><a href='cost.html'>電気代を計算する</a> / <a href='units.html'>単位を換算する</a></p>")

    p("tips.html", "節電のコツ|一般的な考え方",
      "電気代を減らすときの一般的な考え方を整理しました。効果の大きい順に確認する、待機電力、季節家電などの観点です。",
      "<h1>節電のコツ(一般的な考え方)</h1>"
      "<h2>1. 使用量の大きいものから見る</h2><p>電気代は「消費電力 × 使う時間」で決まります。効果が出やすいのは、消費電力が大きく、長く使う機器です。まず<a href='appliances.html'>家電別の目安</a>で、自分の家の大きいものを確認します。</p>"
      "<h2>2. 発熱・冷却は電力を使いやすい</h2><p>暖房、冷房、湯沸かし、乾燥など、熱を扱う機器は消費電力が大きくなりがちです。断熱、日よけ、フィルター掃除、使い方の見直しで運転の負担を減らせることがあります。</p>"
      "<h2>3. 常時通電する機器</h2><p>冷蔵庫、ルーター、待機状態の機器は、1日24時間通電します。消費電力は小さくても、時間が長いため、積み重なります。<a href='compare.html'>買い替え比較</a>で長期の差を見る方法もあります。</p>"
      "<h2>4. 待機電力</h2><p>電源を切っても、リモコン受信や時計表示などで微小な電力が流れる機器があります。長期間使わない機器は、プラグを抜く、スイッチつきタップを使うなどの方法があります。ただし、録画予約や設定保持が必要な機器もあるため、取扱説明書で確認してください。</p>"
      "<h2>5. 契約や単価の見直し</h2><p>電気の契約プランや時間帯別の単価は、電力会社・地域で異なります。契約内容の変更は、検針票と各社の公式情報を比べて検討してください。</p>"
      "<p class='note'>無理な我慢は健康に影響することがあります。特に猛暑・厳寒の時期の冷暖房は、体調を最優先にしてください。</p>")

    terms = [
        ("W(ワット)", "電力の単位。ある瞬間にどれくらいの電気を使っているかを表す"),
        ("kW(キロワット)", "1kW=1000W"),
        ("Wh(ワット時)", "電力量の単位。1Wの電力を1時間使った量"),
        ("kWh(キロワット時)", "電力量の単位。1kWh=1000Wh。電気料金の計算でよく使う"),
        ("V(ボルト)", "電圧の単位。電気を流そうとする力の大きさ"),
        ("A(アンペア)", "電流の単位。流れる電気の量"),
        ("定格消費電力", "機器が決められた条件で運転するときの消費電力。実際の平均とは異なることがある"),
        ("待機電力", "電源を切った状態や待機状態で流れる微小な電力"),
        ("力率", "交流で、供給された電力のうち有効に使われる割合を表す数値。1に近いほど効率がよい"),
        ("基本料金", "使った量によらず契約に応じてかかる料金。有無や決め方は契約で異なる"),
        ("電力量料金", "使った電力量(kWh)に応じてかかる料金"),
        ("契約アンペア", "同時に使える電流の上限として契約する値。アンペア制ではない契約もある"),
    ]
    trs = "".join(f"<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>" for a, b in terms)
    p("terms.html", "電気の用語集|W・kWh・V・A・力率",
      "電気代の計算に出てくるW・kWh・V・A・待機電力・契約アンペアなどの用語を、短い言葉で説明します。",
      f"<h1>電気の用語集</h1><table><tr><th>用語</th><th>意味</th></tr>{trs}</table>"
      "<p><a href='formulas.html'>式の解説</a> / <a href='units.html'>単位換算</a></p>")

    p("faq.html", "電気代・消費電力のよくある質問",
      "WとkWhの違い、電気代の計算が合わない理由、ブレーカーが落ちる条件、待機電力の考え方などによくある疑問に答えます。",
      "<h1>よくある質問</h1>"
      "<h2>WとkWhは何が違いますか?</h2><p>Wは瞬間の大きさ、kWhは使った量です。電気代はkWhに単価をかけて決まります。詳しくは<a href='formulas.html'>式の解説</a>へ。</p>"
      "<h2>計算した電気代が請求額と合いません</h2><p>請求額には基本料金や調整額が含まれる場合があります。また、機器の消費電力は運転状態で変わるため、定格での計算とは差が出ます。</p>"
      "<h2>電力量単価はどこで確認しますか?</h2><p>検針票、または契約中の電力会社の公式サイト・マイページで確認できます。このサイトの初期値は仮の値です。</p>"
      "<h2>エアコンの電気代はどう計算しますか?</h2><p>消費電力は部屋の条件で大きく変わります。取扱説明書の期間消費電力量や、実測値を使うほうが現実に近くなります。<a href='cost.html'>電気代の計算</a>で試算できます。</p>"
      "<h2>ブレーカーが頻繁に落ちます</h2><p>同時使用の見直しや契約の確認が必要です。配線や分電盤に不安がある場合は、電力会社や電気工事の専門家に相談してください。<a href='breaker.html'>目安の確認</a>も参照。</p>"
      "<h2>この計算は正確ですか?</h2><p>概算・目安です。重要な判断は、公式の情報と実測で確認してください。</p>")
