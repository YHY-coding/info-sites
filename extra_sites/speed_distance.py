"""速度・距離・時間の計算ツール集。
規約: META と build(page, write) を持つ。出力は docs/speed-distance/ 配下。"""
import html
import json

META = dict(slug="speed-distance", name="速度・距離・時間の計算ツール集",
            desc="速度・距離・時間のどれか1つを求める計算、km/hとm/sなどの換算、ランニングのペース計算、平均速度、出会い・追いつきの時間を、ブラウザだけで計算できる無料ツール")
SITE = dict(name=META["name"], home="index.html")
NAV = [("速度距離時間", "calc.html"), ("単位換算", "units.html"), ("ペース", "pace.html"), ("平均速度", "average.html"),
       ("出会い・追いつき", "meeting.html"), ("式の解説", "formulas.html"), ("間違いやすい点", "pitfalls.html"), ("用語", "terms.html"), ("FAQ", "faq.html")]
DISC = ("本サイトの計算結果は概算・目安です。実際の移動時間は、信号、渋滞、休憩、天候、経路などで変わります。"
        "交通機関の所要時間や運行は、各事業者の公式情報で確認してください。"
        "入力した数値は、ブラウザの中だけで計算され、送信されません。")

KMH_PER_KNOT = 1.852   # 1ノット=1海里/時、1海里=1852m(定義)
M_PER_MILE = 1609.344  # 1マイル=1609.344m(定義)


def esc(s):
    return html.escape(s, quote=True)


# ---- Python側の基準実装(ブラウザ側JSと一致することを node で確認する) ----
def speed(d, t):
    return d / t


def distance(v, t):
    return v * t


def time_needed(d, v):
    return d / v


def kmh_to_ms(k):
    return k * 1000 / 3600


def ms_to_kmh(m):
    return m * 3600 / 1000


def kmh_to_knot(k):
    return k / KMH_PER_KNOT


def kmh_to_mph(k):
    return k * 1000 / M_PER_MILE


def pace_sec_per_km(kmh):
    return 3600 / kmh


def kmh_from_pace(sec_per_km):
    return 3600 / sec_per_km


def finish_seconds(pace_sec, km):
    return pace_sec * km


def avg_speed(legs):
    """legs: [(距離, 速度)]。全体の距離 ÷ 全体の時間(調和平均)。"""
    td = sum(d for d, _ in legs)
    tt = sum(d / v for d, v in legs)
    return td / tt


def meet_time(gap, v1, v2):
    """向かい合って進む。出会うまでの時間。"""
    return gap / (v1 + v2)


def catch_time(gap, v_fast, v_slow):
    """同じ向き。追いつくまでの時間。追いつけない場合は None。"""
    if v_fast <= v_slow:
        return None
    return gap / (v_fast - v_slow)


# ---- ブラウザ側JS ----
CORE_JS = """
function speed(d,t){return d/t}
function distance(v,t){return v*t}
function timeNeeded(d,v){return d/v}
function kmhToMs(k){return k*1000/3600}
function msToKmh(m){return m*3600/1000}
function kmhToKnot(k){return k/1.852}
function kmhToMph(k){return k*1000/1609.344}
function paceSecPerKm(k){return 3600/k}
function kmhFromPace(s){return 3600/s}
function finishSeconds(p,km){return p*km}
function avgSpeed(legs){var td=0,tt=0;for(var i=0;i<legs.length;i++){td+=legs[i][0];tt+=legs[i][0]/legs[i][1]}return td/tt}
function meetTime(g,a,b){return g/(a+b)}
function catchTime(g,f,s){return f<=s?null:g/(f-s)}
function fmt(x){if(!isFinite(x))return '-';var a=Math.abs(x);if(a!==0&&(a<0.001||a>=1e9))return x.toExponential(3);return (Math.round(x*100)/100).toLocaleString('ja-JP',{maximumFractionDigits:2})}
function hms(sec){sec=Math.round(sec);var h=Math.floor(sec/3600),m=Math.floor(sec%3600/60),s=sec%60;return (h>0?h+'時間':'')+(h>0||m>0?m+'分':'')+s+'秒'}
function $(id){return document.getElementById(id)}
if(typeof module!=='undefined')module.exports={speed:speed,distance:distance,timeNeeded:timeNeeded,kmhToMs:kmhToMs,msToKmh:msToKmh,kmhToKnot:kmhToKnot,kmhToMph:kmhToMph,paceSecPerKm:paceSecPerKm,kmhFromPace:kmhFromPace,finishSeconds:finishSeconds,avgSpeed:avgSpeed,meetTime:meetTime,catchTime:catchTime};
"""

CALC_JS = """
if(typeof document!=='undefined'){
function run(){var m=$('mode').value,d=parseFloat($('d').value),v=parseFloat($('v').value),h=parseFloat($('h').value)||0,mi=parseFloat($('mi').value)||0,t=h+mi/60,o='';
if(m==='v'){if(!(d>=0)||!(t>0)){$('out').textContent='距離と、0より大きい時間を入力してください';return}o='速度は <span class="big">'+fmt(speed(d,t))+' km/h</span>(秒速 '+fmt(kmhToMs(speed(d,t)))+' m/s)'}
else if(m==='d'){if(!(v>=0)||!(t>=0)){$('out').textContent='速度と時間を入力してください';return}o='距離は <span class="big">'+fmt(distance(v,t))+' km</span>'}
else{if(!(d>=0)||!(v>0)){$('out').textContent='距離と、0より大きい速度を入力してください';return}var x=timeNeeded(d,v);o='時間は <span class="big">'+hms(x*3600)+'</span>('+fmt(x)+' 時間)'}
$('out').innerHTML=o}
$('mode').onchange=run;$('btn').onclick=run;run()}
"""

UNITS_JS = """
if(typeof document!=='undefined'){
function run(){var k=parseFloat($('k').value);if(!(k>=0)){$('out').textContent='0以上の数を入力してください';return}
$('out').innerHTML='<table><tr><th>'+fmt(k)+' km/h は</th><td>'+fmt(kmhToMs(k))+' m/s</td></tr><tr><th>ノット</th><td>'+fmt(kmhToKnot(k))+' kn</td></tr><tr><th>マイル毎時</th><td>'+fmt(kmhToMph(k))+' mph</td></tr><tr><th>1kmにかかる時間(ペース)</th><td>'+(k>0?hms(paceSecPerKm(k)):'-')+'</td></tr></table>'}
$('btn').onclick=run;run()}
"""

PACE_JS = """
if(typeof document!=='undefined'){
function run(){var pm=parseFloat($('pm').value)||0,ps=parseFloat($('ps').value)||0,km=parseFloat($('km').value),p=pm*60+ps;
if(!(p>0)||!(km>0)){$('out').textContent='ペースと距離を入力してください';return}
$('out').innerHTML='<table><tr><th>時速</th><td>'+fmt(kmhFromPace(p))+' km/h</td></tr><tr><th>'+fmt(km)+' km を走り切る時間の目安</th><td>'+hms(finishSeconds(p,km))+'</td></tr></table>'}
$('btn').onclick=run;run()}
"""

AVG_JS = """
if(typeof document!=='undefined'){
function run(){var ls=$('lines').value.split('\\n'),legs=[],i,h='';
for(i=0;i<ls.length;i++){var s=ls[i].trim();if(!s)continue;var p=s.split(/[ ,、\\t]+/),d=parseFloat(p[0]),v=parseFloat(p[1]);
if(p.length<2||!(d>=0)||!(v>0)){$('out').textContent=(i+1)+'行目を確認してください(「距離 速度」の形で、速度は0より大きい数)';return}legs.push([d,v])}
if(!legs.length){$('out').textContent='1行以上入力してください';return}
var td=0,tt=0;for(i=0;i<legs.length;i++){td+=legs[i][0];tt+=legs[i][0]/legs[i][1]}
$('out').innerHTML='<table><tr><th>全体の距離</th><td>'+fmt(td)+'</td></tr><tr><th>全体の時間</th><td>'+fmt(tt)+'(距離と速度の単位に対応)</td></tr><tr><th>平均速度</th><td><span class="big">'+fmt(avgSpeed(legs))+'</span></td></tr></table>'}
$('btn').onclick=run;run()}
"""

MEET_JS = """
if(typeof document!=='undefined'){
function run(){var g=parseFloat($('g').value),a=parseFloat($('a').value),b=parseFloat($('b').value);
if(!(g>=0)||!(a>=0)||!(b>=0)){$('out').textContent='0以上の数を入力してください';return}
var o='<table>';
o+='<tr><th>向かい合って進む場合の出会うまでの時間</th><td>'+((a+b)>0?hms(meetTime(g,a,b)*3600):'進まないため出会いません')+'</td></tr>';
var f=Math.max(a,b),s=Math.min(a,b),c=catchTime(g,f,s);
o+='<tr><th>同じ向きに進み、速い側が追いつくまでの時間</th><td>'+(c===null?'速さが同じか遅いので追いつきません':hms(c*3600))+'</td></tr></table>';
$('out').innerHTML=o}
$('btn').onclick=run;run()}
"""


def script(extra):
    return f"<script>{CORE_JS}{extra}</script>"


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)

    p("index.html", "速度・距離・時間の計算ツール集|km/h・m/s・ペース",
      "速度・距離・時間のうち2つから残りを計算。km/hとm/sの換算、ランニングのペース、平均速度、出会い・追いつきの時間をブラウザだけで計算できます。",
      "<h1>速度・距離・時間の計算ツール集</h1><p>「はじき」の関係(速さ=距離÷時間)を使う計算を、ツールと解説で整理しました。入力した数字は、ブラウザの中だけで計算され、送信されません。</p>"
      "<div class='card'><a href='calc.html'><strong>速度・距離・時間の計算</strong></a><br>どれか1つを求める</div>"
      "<div class='card'><a href='units.html'><strong>速度の単位換算</strong></a><br>km/h・m/s・ノット・mph、1kmあたりの時間</div>"
      "<div class='card'><a href='pace.html'><strong>ランニングのペース計算</strong></a><br>1kmあたりのペースから時速と所要時間</div>"
      "<div class='card'><a href='average.html'><strong>平均速度の計算</strong></a><br>区間ごとに速度が違うときの全体の平均</div>"
      "<div class='card'><a href='meeting.html'><strong>出会い・追いつきの計算</strong></a><br>2つの移動物の間隔から時間を求める</div>"
      "<h2>解説</h2><ul class='links'><li><a href='formulas.html'>速度・距離・時間の式</a></li><li><a href='pitfalls.html'>間違いやすい点</a></li>"
      "<li><a href='terms.html'>用語集</a></li><li><a href='faq.html'>よくある質問</a></li></ul>")

    p("calc.html", "速度・距離・時間の計算|はじきの公式",
      "速度・距離・時間のうち2つを入力して、残り1つを計算します。速度はkm/h、距離はkm、時間は時間と分で入力します。",
      "<h1>速度・距離・時間の計算</h1><p>求めたいものを選び、残りを入力してください。速度は km/h、距離は km です。</p>"
      "<div class='card'><label>求めるもの <select id='mode'><option value='t'>時間</option><option value='v'>速度</option><option value='d'>距離</option></select></label><br>"
      "<label>距離(km) <input id='d' type='number' value='60' min='0' step='any'></label><br>"
      "<label>速度(km/h) <input id='v' type='number' value='40' min='0' step='any'></label><br>"
      "<label>時間 <input id='h' type='number' value='1' min='0' step='any'> 時間 <input id='mi' type='number' value='30' min='0' step='any'> 分</label><br><br>"
      "<button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<p class='note'>「求めるもの」で選んだ項目の入力欄は、計算には使われません。平均の速さとして扱うため、途中の停止や渋滞は含みません。</p>"
      "<p><a href='formulas.html'>式の解説</a> / <a href='pitfalls.html'>間違いやすい点</a></p>" + script(CALC_JS))

    p("units.html", "速度の単位換算|km/h・m/s・ノット・mph",
      "時速(km/h)を、秒速(m/s)、ノット、マイル毎時に換算します。1kmにかかる時間も同時に表示します。",
      "<h1>速度の単位換算</h1>"
      "<div class='card'><label>時速(km/h) <input id='k' type='number' value='60' min='0' step='any'></label><br><br><button id='btn'>換算する</button></div><div id='out' class='card'></div>"
      "<h2>換算の考え方</h2><ul><li>km/h → m/s は、1000を掛けて3600で割ります(36km/h = 10m/s)</li>"
      "<li>1ノットは1時間に1海里進む速さで、1海里は1852mと定められています(約1.852km/h)</li>"
      "<li>1マイルは1609.344mと定められています</li>"
      "<li>船舶・航空ではノット、道路標識の国によってはmphが使われます。使う場面のルールは公式情報で確認してください</li></ul>"
      + script(UNITS_JS))

    p("pace.html", "ランニングのペース計算|1kmあたりのペースから時速へ",
      "1kmあたりのペース(分・秒)から時速を計算し、指定した距離を走り切る時間の目安を出します。",
      "<h1>ランニングのペース計算</h1><p>ペースは「1kmを何分何秒で進むか」を表します。</p>"
      "<div class='card'><label>1kmのペース <input id='pm' type='number' value='6' min='0' step='1'> 分 <input id='ps' type='number' value='0' min='0' max='59' step='1'> 秒</label><br>"
      "<label>距離(km) <input id='km' type='number' value='10' min='0' step='any'></label><br><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>考え方</h2><ul><li>時速 = 3600 ÷ 1kmにかかる秒数。ペース6分0秒なら 3600 ÷ 360 = 10km/h</li>"
      "<li>所要時間 = ペース × 距離。ずっと同じペースで進めた場合の理想値です</li>"
      "<li>実際は、坂道、気温、体調、信号などでペースは変わります。無理のない計画は、自分の体調と専門家の指導を優先してください</li></ul>"
      + script(PACE_JS))

    p("average.html", "平均速度の計算|区間ごとに速度が違うとき",
      "区間ごとの距離と速度を入力して、全体の平均速度を計算します。速度の単純な平均にならない理由も解説。",
      "<h1>平均速度の計算</h1><p>1行に1区間、「距離 速度」の形で入力してください(例:行きと帰りで速度が違う場合)。</p>"
      "<div class='card'><label>区間(距離 速度)<br><textarea id='lines' rows='5' cols='30'>30 60\n30 30</textarea></label><br><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>なぜ単純に平均しないのか</h2><p>平均速度は「全体の距離 ÷ 全体の時間」です。速度が遅い区間では時間が長くかかるため、その影響が大きくなります。たとえば同じ30kmを時速60kmと時速30kmで進むと、時間は0.5時間と1時間で合計1.5時間、平均は 60 ÷ 1.5 = 40km/h です。60と30の単純な平均45km/hにはなりません。</p>"
      "<p>距離と速度の単位はそろえて入力してください(例:km と km/h)。</p>" + script(AVG_JS))

    p("meeting.html", "出会い・追いつきの計算|間隔と速度から時間を求める",
      "2つの移動物の間隔と速度から、向かい合って進むときに出会うまでの時間と、同じ向きに進むとき追いつくまでの時間を計算します。",
      "<h1>出会い・追いつきの計算</h1><p>2つの移動物(人・車・列車など)が一定の速さで進むと考えます。</p>"
      "<div class='card'><label>最初の間隔(km) <input id='g' type='number' value='12' min='0' step='any'></label><br>"
      "<label>Aの速度(km/h) <input id='a' type='number' value='4' min='0' step='any'></label><br>"
      "<label>Bの速度(km/h) <input id='b' type='number' value='8' min='0' step='any'></label><br><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>考え方</h2><ul><li><strong>向かい合って進む</strong>: 間隔は1時間に「2つの速度の和」ずつ縮まります。時間 = 間隔 ÷ (A + B)</li>"
      "<li><strong>同じ向きに進む</strong>: 間隔は1時間に「速度の差」ずつ縮まります。時間 = 間隔 ÷ (速い方 − 遅い方)。同じか遅ければ追いつけません</li>"
      "<li>後ろから追う側が速い場合の追いつきを想定した表示です。追われる側が速い場合は追いつきません</li></ul>" + script(MEET_JS))

    p("formulas.html", "速度・距離・時間の式|はじきの公式と単位のそろえ方",
      "速さ=距離÷時間の関係と、そこから距離・時間を求める式、単位をそろえるコツを整理しました。",
      "<h1>速度・距離・時間の式</h1>"
      "<h2>3つの基本式</h2><ol><li><strong>速さ = 距離 ÷ 時間</strong></li><li><strong>距離 = 速さ × 時間</strong></li><li><strong>時間 = 距離 ÷ 速さ</strong></li></ol>"
      "<p>3つは同じ関係を並べ替えたものです。覚えやすいように「は・じ・き」の図で整理する方法があります(は=速さ、き=距離、じ=時間)。</p>"
      "<h2>計算例(説明用の数字)</h2><p>時速40kmで90分(1.5時間)進むと、距離は 40 × 1.5 = 60km です。60kmを時速40kmで進む時間は 60 ÷ 40 = 1.5時間(1時間30分)です。</p>"
      "<h2>単位をそろえる</h2><ul><li>時速(km/h)なら、距離はkm、時間は「時間」</li><li>分で与えられた時間は60で割って「時間」にします(90分 = 1.5時間)</li>"
      "<li>秒速(m/s)なら、距離はm、時間は秒</li></ul>"
      "<p><a href='calc.html'>計算する</a> / <a href='units.html'>単位換算</a> / <a href='pitfalls.html'>間違いやすい点</a></p>")

    p("pitfalls.html", "速度計算で間違いやすい点|平均・単位・小数の時間",
      "平均速度を単純平均してしまう、分を小数にしてしまう、単位がそろっていないなど、速度・距離・時間の計算でよくある間違いをまとめました。",
      "<h1>速度計算で間違いやすい点</h1>"
      "<h2>1. 速度を単純に平均する</h2><p>区間の距離が同じでも、速度が違えば時間は違います。全体の距離 ÷ 全体の時間で求めます。<a href='average.html'>平均速度の計算</a>で確認できます。</p>"
      "<h2>2. 1時間30分を1.30時間とする</h2><p>1時間30分は1.5時間です。分は60で割ります。0.5時間は30分、0.25時間は15分です。</p>"
      "<h2>3. 単位がそろっていない</h2><p>km/hとmを混ぜる、分と時間を混ぜるなどは、桁の間違いのもとです。計算前に単位をそろえます。</p>"
      "<h2>4. 理想値を実際の所要時間とする</h2><p>計算結果は一定の速さで進めた場合の値です。信号、渋滞、休憩、乗り換えは含まれません。</p>"
      "<h2>5. 制限速度との関係</h2><p>道路の制限速度は法令と標識に従ってください。このサイトの計算は、速く走ることを勧めるものではありません。</p>")

    terms = [("速さ(速度)", "単位時間に進む距離。日常では同じ意味で使われることが多い"),
             ("平均速度", "全体の距離を全体の時間で割った値"),
             ("km/h(時速)", "1時間に進むキロメートル数"), ("m/s(秒速)", "1秒に進むメートル数。36km/h=10m/s"),
             ("ノット(kn)", "1時間に1海里進む速さ。1海里=1852m"), ("マイル毎時(mph)", "1時間に進むマイル数。1マイル=1609.344m"),
             ("ペース", "一定の距離(例:1km)を進むのにかかる時間"), ("相対速度", "一方から見たもう一方の速度。向かい合えば和、同じ向きなら差")]
    trs = "".join(f"<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>" for a, b in terms)
    p("terms.html", "速度・距離・時間の用語集|km/h・m/s・ノット・ペース",
      "速さ、平均速度、時速、秒速、ノット、ペース、相対速度などの用語を短く説明します。",
      f"<h1>速度・距離・時間の用語集</h1><table><tr><th>用語</th><th>意味</th></tr>{trs}</table><p><a href='formulas.html'>式の解説</a></p>")

    p("faq.html", "速度・距離・時間のよくある質問",
      "36km/hが10m/sになる理由、平均速度の求め方、ペースと時速の関係など、よくある疑問に答えます。",
      "<h1>よくある質問</h1>"
      "<h2>km/hとm/sの換算で、なぜ3.6を使うのですか?</h2><p>1km=1000m、1時間=3600秒なので、1km/h = 1000÷3600 m/s = 約0.2778m/s です。逆にm/sを3.6倍するとkm/hです。</p>"
      "<h2>行きと帰りで速度が違うとき、平均はどう求めますか?</h2><p>全体の距離を全体の時間で割ります。<a href='average.html'>平均速度の計算</a>を使ってください。</p>"
      "<h2>ペース5分30秒は時速何kmですか?</h2><p>330秒/kmなので 3600 ÷ 330 = 約10.9km/h です。<a href='pace.html'>ペース計算</a>で確認できます。</p>"
      "<h2>この所要時間で実際に着きますか?</h2><p>一定の速さで進める理想の値です。実際の所要時間は、交通機関の公式情報や地図サービスなどで確認してください。</p>"
      "<h2>入力した数字は送信されますか?</h2><p>いいえ。計算はブラウザの中だけで行われます。</p>")
