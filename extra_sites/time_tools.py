"""時間の足し算・引き算、時間差、タイムゾーン(UTCオフセット)変換ツール集。規約: META と build(page, write) を持つ。出力は docs/time-tools/ 配下。"""
import html

META = dict(slug="time-tools", name="時間計算ツール集", desc="時間の足し算・引き算、2つの時刻の差、UTCオフセットによる時差変換、小数時間の換算をブラウザだけで試せる無料ツールと解説")
SITE = dict(name=META["name"], home="index.html")
NAV = [("足し引き", "add-subtract.html"), ("時間差", "duration.html"), ("時差変換", "timezone.html"), ("小数時間", "decimal.html"),
       ("時刻の表記", "notation.html"), ("UTC", "utc-and-offsets.html"), ("夏時間", "dst.html"), ("手計算", "manual.html"), ("オフセット表", "offset-table.html"), ("用語", "glossary.html")]
DISC = ("本サイトの結果は目安です。勤怠・契約・航空券などで使う前には、公式の時刻表や各組織の規定など公式の情報で確認してください。"
        "入力した値は、ブラウザの中だけで計算され、送信されません。")


def esc(s):
    return html.escape(s, quote=True)


# ---- Python側の基準実装(ブラウザ側JSと一致することを node で確認する) ----
def parse_hms(s):
    """'h', 'h:m', 'h:m:s' を秒に。不正ならNone。"""
    parts = s.strip().split(":")
    if not 1 <= len(parts) <= 3 or any((not p.isdigit()) for p in parts):
        return None
    v = [int(p) for p in parts] + [0] * (3 - len(parts))
    if v[1] > 59 or v[2] > 59:
        return None
    return v[0] * 3600 + v[1] * 60 + v[2]


def fmt_hms(sec):
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def addsub(base, delta, sign):
    """時刻baseにdeltaを足す(sign=1)/引く(sign=-1)。(日数のずれ, その日の秒)を返す。"""
    t = base + sign * delta
    return t // 86400, t % 86400


def duration(start, end):
    """開始から終了までの秒。終了が早ければ翌日とみなす。"""
    d = end - start
    return d + 86400 if d < 0 else d


def tzconv(minutes_of_day, off_from, off_to):
    """現地時刻(分)をオフセット(分)から別のオフセットへ。(日数のずれ, その日の分)。"""
    t = minutes_of_day - off_from + off_to
    return t // 1440, t % 1440


def parse_dec(s):
    """小数時間の文字列を百分の一時間(整数)に。小数第3位以下は切り捨て。"""
    s = s.strip()
    if not s or s.count(".") > 1:
        return None
    a, _, b = s.partition(".")
    if (a and not a.isdigit()) or (b and not b.isdigit()) or (not a and not b):
        return None
    return int(a or "0") * 100 + int((b + "00")[:2])


def dec_to_min(h100):
    return (h100 * 60 + 50) // 100


def min_to_dec(m):
    return (m * 200 + 60) // 120


LIB = """
function parseHMS(s){var p=s.trim().split(':');if(p.length<1||p.length>3)return null;for(var i=0;i<p.length;i++)if(!/^[0-9]+$/.test(p[i]))return null;
var h=parseInt(p[0],10),m=p.length>1?parseInt(p[1],10):0,x=p.length>2?parseInt(p[2],10):0;if(m>59||x>59)return null;return h*3600+m*60+x}
function pad(n){return (n<10?'0':'')+n}
function fmtHMS(t){return Math.floor(t/3600)+':'+pad(Math.floor(t%3600/60))+':'+pad(t%60)}
function addsub(b,d,s){var t=b+s*d;return [Math.floor(t/86400),((t%86400)+86400)%86400]}
function duration(a,b){var d=b-a;return d<0?d+86400:d}
function tzconv(m,f,t){var x=m-f+t;return [Math.floor(x/1440),((x%1440)+1440)%1440]}
function parseDec(s){s=s.trim();if(!s)return null;var p=s.split('.');if(p.length>2)return null;var a=p[0],b=p.length>1?p[1]:'';
if((a&&!/^[0-9]+$/.test(a))||(b&&!/^[0-9]+$/.test(b))||(!a&&!b))return null;return parseInt(a||'0',10)*100+parseInt((b+'00').slice(0,2),10)}
function decToMin(h){return Math.floor((h*60+50)/100)}
function minToDec(m){return Math.floor((m*200+60)/120)}
function fmtDec(h){return Math.floor(h/100)+'.'+pad(h%100)}
function $(id){return document.getElementById(id)}
"""

ADD_JS = """
function run(){var b=parseHMS($('base').value),d=parseHMS($('delta').value),s=parseInt($('sign').value,10);
if(b===null||d===null){$('out').textContent='時刻の形式を確認してください(例: 9:30 や 13:45:10。分と秒は0〜59)';return}
var r=addsub(b,d,s),dd=r[0],txt=dd===0?'同じ日':(dd>0?'+'+dd+'日後':dd+'日(前の日)');
$('out').innerHTML='<p class="big">'+fmtHMS(r[1])+'</p><p>'+txt+'</p>'}
$('btn').onclick=run;run();
"""

DUR_JS = """
function run(){var a=parseHMS($('st').value),b=parseHMS($('en').value),br=parseHMS($('br').value);
if(a===null||b===null||br===null||a>=86400||b>=86400){$('out').textContent='時刻の形式を確認してください(開始・終了は 0:00〜23:59:59、休憩は 0:00 以上)';return}
var d=duration(a,b),net=d-br;
var o='<table><tr><th>開始から終了まで</th><td>'+fmtHMS(d)+'</td></tr>';
if(net<0){o+='<tr><th>休憩を引いた時間</th><td>休憩が長すぎます</td></tr>'}else{o+='<tr><th>休憩を引いた時間</th><td>'+fmtHMS(net)+'</td></tr><tr><th>小数の時間(休憩後・小数第2位まで切り捨て)</th><td>'+fmtDec(Math.floor(net/36))+' 時間</td></tr>'}
$('out').innerHTML=o+'</table>'}
$('btn').onclick=run;run();
"""

TZ_JS = """
function run(){var p=$('t').value.trim().split(':');
if(p.length!==2||!/^[0-9]+$/.test(p[0])||!/^[0-9]+$/.test(p[1])||parseInt(p[0],10)>23||parseInt(p[1],10)>59){$('out').textContent='時刻は 時:分 の形式で入力してください(例: 9:30)';return}
var m=parseInt(p[0],10)*60+parseInt(p[1],10),r=tzconv(m,parseInt($('f').value,10),parseInt($('to').value,10)),dd=r[0];
var txt=dd===0?'同じ日':(dd>0?'翌日':'前日');
$('out').innerHTML='<p class="big">'+pad(Math.floor(r[1]/60))+':'+pad(r[1]%60)+'</p><p>'+txt+'</p>'}
$('btn').onclick=run;run();
"""

DEC_JS = """
function run(){var h=parseDec($('dec').value),m=parseHMS($('hm').value),o='';
if(h===null){o+='<p>小数の時間の入力を確認してください(例: 7.75)</p>'}else{var t=decToMin(h);o+='<p>'+fmtDec(h)+' 時間 = <strong>'+Math.floor(t/60)+'時間'+pad(t%60)+'分</strong></p>'}
if(m===null||m>=86400*100){o+='<p>時:分 の入力を確認してください(例: 7:45)</p>'}else{var tm=Math.floor(m/60);o+='<p>'+Math.floor(tm/60)+':'+pad(tm%60)+' = <strong>'+fmtDec(minToDec(tm))+' 時間</strong>(小数第3位を四捨五入)</p>'}
$('out').innerHTML=o}
$('btn').onclick=run;run();
"""

# オフセットの選択肢(標準時の値。夏時間は考慮しない)。値は分。
ZONES = [
    ("UTC(協定世界時)", 0), ("日本標準時(UTC+9)", 540), ("韓国標準時(UTC+9)", 540), ("中国標準時(UTC+8)", 480), ("インド標準時(UTC+5:30)", 330),
    ("アラブ首長国連邦(UTC+4)", 240), ("中央ヨーロッパ標準時(UTC+1)", 60), ("英国標準時(UTC+0)", 0),
    ("米国東部標準時(UTC−5)", -300), ("米国中部標準時(UTC−6)", -360), ("米国山岳部標準時(UTC−7)", -420), ("米国太平洋標準時(UTC−8)", -480),
    ("オーストラリア東部標準時(UTC+10)", 600), ("ニュージーランド標準時(UTC+12)", 720),
]


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)
    zopts = lambda sel: "".join(f"<option value='{v}'{' selected' if n == sel else ''}>{esc(n)}</option>" for n, v in ZONES)

    p("index.html", "時間計算ツール集|足し引き・時間差・時差変換",
      "時間の足し算・引き算、2つの時刻の差、時差の変換、小数時間の換算をブラウザだけで試せる無料ツールと、時刻の基本解説をまとめたサイトです。",
      "<h1>時間計算ツール集</h1><p>入力した値は、ブラウザの中だけで計算されます。サーバーには送信されません。</p>"
      "<h2>ツール</h2>"
      "<div class='card'><a href='add-subtract.html'><strong>時間の足し算・引き算</strong></a><br>時刻に時間を足し引きして、日をまたぐ場合も表示</div>"
      "<div class='card'><a href='duration.html'><strong>時間差(経過時間)の計算</strong></a><br>開始と終了の時刻から経過時間を計算。休憩を引くことも可能</div>"
      "<div class='card'><a href='timezone.html'><strong>時差変換(UTCオフセット)</strong></a><br>標準時のオフセットで、ある地域の時刻を別の地域の時刻に</div>"
      "<div class='card'><a href='decimal.html'><strong>小数時間の換算</strong></a><br>7.75時間と7時間45分の相互変換</div>"
      "<h2>解説</h2><ul class='links'><li><a href='notation.html'>24時間表記と12時間表記</a></li><li><a href='utc-and-offsets.html'>UTCとオフセットの基本</a></li>"
      "<li><a href='dst.html'>夏時間(サマータイム)の注意点</a></li><li><a href='manual.html'>時間計算の手計算のやり方</a></li>"
      "<li><a href='offset-table.html'>主な地域の標準時オフセット表</a></li><li><a href='glossary.html'>用語集</a></li></ul>")

    p("add-subtract.html", "時間の足し算・引き算ツール|日またぎも対応",
      "時刻に「何時間何分」を足したり引いたりした結果を計算します。日をまたぐ場合は何日後・何日前かも表示します。",
      "<h1>時間の足し算・引き算</h1><p>基準の時刻に、時間を足すか引きます。時刻は 時:分 または 時:分:秒 の形式で入力します。</p>"
      "<div class='card'><label>基準の時刻 <input id='base' type='text' value='22:30'></label><br>"
      "<label>演算 <select id='sign'><option value='1'>足す(+)</option><option value='-1'>引く(−)</option></select></label><br>"
      "<label>足す・引く時間 <input id='delta' type='text' value='3:45'></label><br><br><button id='btn'>計算する</button></div>"
      "<div id='out' class='card'></div>"
      "<h2>使い方のヒント</h2><ul><li>足す・引く時間は、24時間を超えても入力できます(例: 30:00)</li><li>結果が日をまたぐときは「+1日後」のように表示されます</li>"
      "<li>時刻どうしの差を知りたいときは<a href='duration.html'>時間差の計算</a>を使います</li></ul>"
      "<p>手計算の考え方は<a href='manual.html'>時間計算の手計算</a>を参照してください。</p>"
      f"<script>{LIB}{ADD_JS}</script>")

    p("duration.html", "時間差の計算ツール|開始と終了から経過時間を求める",
      "開始時刻と終了時刻から経過時間を計算します。終了が開始より早い場合は翌日とみなし、休憩時間を引いた時間も表示します。",
      "<h1>時間差(経過時間)の計算</h1><p>開始と終了の時刻を入力します。終了が開始より小さいときは、翌日の時刻として計算します。</p>"
      "<div class='card'><label>開始 <input id='st' type='text' value='9:00'></label><br>"
      "<label>終了 <input id='en' type='text' value='18:30'></label><br>"
      "<label>休憩 <input id='br' type='text' value='1:00'></label><br><br><button id='btn'>計算する</button></div>"
      "<div id='out' class='card'></div>"
      "<h2>注意</h2><ul><li>1日(24時間)を超える時間差は、このツールでは扱いません</li><li>勤務時間の扱い(丸め方、休憩の取り方など)は、会社の規定や公式の資料で確認してください</li>"
      "<li>小数の時間は、小数第2位まで切り捨てて表示します。換算は<a href='decimal.html'>小数時間の換算</a>でも行えます</li></ul>"
      f"<script>{LIB}{DUR_JS}</script>")

    p("timezone.html", "時差変換ツール|標準時のオフセットで地域間の時刻を変換",
      "日本・米国・欧州など主な地域の標準時のオフセットを使って、ある地域の時刻を別の地域の時刻に変換します。夏時間は考慮しません。",
      "<h1>時差変換(標準時のオフセット)</h1><p>時刻と、元の地域・変換先の地域を選びます。<strong>標準時の値で計算し、夏時間は考慮しません</strong>(<a href='dst.html'>夏時間の注意点</a>)。</p>"
      "<div class='card'><label>時刻(時:分) <input id='t' type='text' value='9:00'></label><br>"
      f"<label>元の地域 <select id='f'>{zopts('日本標準時(UTC+9)')}</select></label><br>"
      f"<label>変換先 <select id='to'>{zopts('米国東部標準時(UTC−5)')}</select></label><br><br><button id='btn'>変換する</button></div>"
      "<div id='out' class='card'></div>"
      "<p>夏時間を実施する地域では、時期によって実際の差が1時間変わります。会議の設定や渡航の予定には、必ず公式の情報や信頼できる時計で確認してください。</p>"
      f"<script>{LIB}{TZ_JS}</script>")

    p("decimal.html", "小数時間の換算ツール|7.75時間は7時間45分",
      "「7.75時間」のような小数の時間と、「7時間45分」の相互変換を行います。",
      "<h1>小数時間の換算</h1><p>勤務時間などを、小数(例: 7.75)と時:分(例: 7:45)の間で換算します。</p>"
      "<div class='card'><label>小数の時間 <input id='dec' type='text' value='7.75'></label><br>"
      "<label>時:分 <input id='hm' type='text' value='7:45'></label><br><br><button id='btn'>換算する</button></div>"
      "<div id='out' class='card'></div>"
      "<h2>換算の考え方</h2><ul><li>小数の時間 × 60 = 分(7.75時間なら 465分 = 7時間45分)</li><li>分 ÷ 60 = 小数の時間(45分なら 0.75時間)</li></ul>"
      "<p>このツールは分未満・小数第3位以下を四捨五入します。給与計算での丸め方は規定が異なるため、公式の情報で確認してください。</p>"
      f"<script>{LIB}{DEC_JS}</script>")

    p("notation.html", "24時間表記と12時間表記|午前・午後の注意点",
      "24時間表記と12時間表記(AM/PM)の違い、0時と12時のあいまいさ、日をまたぐ表現(24:30など)を解説します。",
      "<h1>24時間表記と12時間表記</h1>"
      "<h2>24時間表記</h2><p>0時から23時59分までで1日を表します。午前・午後の区別が要らないため、計算や記録に向いています。</p>"
      "<h2>12時間表記</h2><p>午前(AM)と午後(PM)に分け、それぞれ12時間で表します。日常会話でよく使われますが、「午前12時」「午後12時」はどちらを指すか誤解されやすい表現です。</p>"
      "<table><tr><th>24時間表記</th><th>12時間表記の例</th></tr><tr><td>0:00</td><td>午前0時(夜中の0時)</td></tr><tr><td>6:00</td><td>午前6時</td></tr>"
      "<tr><td>12:00</td><td>正午(午後0時と書く流儀もある)</td></tr><tr><td>18:00</td><td>午後6時</td></tr><tr><td>23:59</td><td>午後11時59分</td></tr></table>"
      "<h2>「24:30」という書き方</h2><p>深夜の時間帯を前日の続きとして、24時や25時と書く慣習が、番組表や勤務表などで見られます。25:00は翌日の1:00と同じ時刻です。使うかどうかは、各組織のルールに従います。</p>"
      "<p>12時間表記が不安なときは、24時間表記で書くか「正午」「深夜0時」と書くと誤解を防げます。<a href='add-subtract.html'>足し引きツール</a>では24時間表記で入力します。</p>")

    p("utc-and-offsets.html", "UTCとオフセットの基本|協定世界時と地域の時刻",
      "協定世界時(UTC)と、各地域の標準時を「UTC+9」のようなオフセットで表す仕組みを解説します。",
      "<h1>UTCとオフセットの基本</h1>"
      "<h2>UTCとは</h2><p>UTC(協定世界時)は、世界の標準時刻の基準となる時刻です。各地域の標準時は、UTCからどれだけ進んでいるか、または遅れているかで表せます。</p>"
      "<h2>オフセットの読み方</h2><ul><li>UTC+9: UTCより9時間進んでいる(日本標準時)</li><li>UTC−5: UTCより5時間遅れている</li>"
      "<li>UTC+5:30: 30分単位のずれを持つ地域もある</li></ul>"
      "<h2>変換の手順</h2><ol><li>元の時刻から、元のオフセットを引いて、UTCにする</li><li>UTCに、変換先のオフセットを足す</li></ol>"
      "<p>例: 日本の9:00(UTC+9)→ UTCでは0:00 → UTC−5の地域では、前日の19:00。計算は<a href='timezone.html'>時差変換ツール</a>で確かめられます。</p>"
      "<p>地域ごとのオフセットは制度の変更があり得るため、最新の値は公式の情報で確認してください。主な値の例は<a href='offset-table.html'>オフセット表</a>にあります。</p>")

    p("dst.html", "夏時間(サマータイム)の注意点|時差がずれる理由",
      "夏時間を実施する地域で、時差が時期によって変わる理由と、時刻計算での注意点を解説します。",
      "<h1>夏時間(サマータイム)の注意点</h1>"
      "<p>夏時間は、夏の間だけ標準時より時計を1時間進める制度で、一部の国や地域で実施されています。日本では現在、実施されていません。</p>"
      "<h2>時差への影響</h2><p>日本と、夏時間を実施する地域との時差は、年に2回ほど1時間ずつ変わります。実施の有無・開始と終了の日付は、地域や年によって異なり、変更されることもあります。</p>"
      "<h2>計算するときの注意</h2><ul><li>将来の会議や渡航の時刻は、その日付に夏時間が適用されるかを確認する</li><li>切り替え日には、1日が23時間または25時間になる</li>"
      "<li>本サイトの<a href='timezone.html'>時差変換ツール</a>は標準時のみで計算するため、夏時間の期間は結果が1時間ずれることがある</li></ul>"
      "<p>具体的な日付やルールは、各地域の公式の情報で確認してください。基本の考え方は<a href='utc-and-offsets.html'>UTCとオフセット</a>のページにあります。</p>")

    p("manual.html", "時間計算の手計算のやり方|60進法の繰り上がり",
      "時間・分・秒の足し算、引き算、時間差を、60進法の繰り上がりと繰り下がりで手計算するやり方を例つきで解説します。",
      "<h1>時間計算の手計算のやり方</h1>"
      "<p>時間・分・秒は60進法です。10進数の筆算と同じ形で、60を超えたら繰り上げます。</p>"
      "<h2>足し算</h2><p>例: 22:30 に 3時間45分を足す</p><ol><li>分を足す: 30 + 45 = 75分 → 60を引いて15分、時に1繰り上げ</li><li>時を足す: 22 + 3 + 1 = 26時 → 24を引いて2時(翌日)</li></ol><p>答え: 翌日の2:15。</p>"
      "<h2>引き算</h2><p>例: 9:20 から 2時間45分を引く</p><ol><li>分が足りないので、1時間(60分)を借りる: 20 + 60 = 80分</li><li>分: 80 − 45 = 35分</li><li>時: 9 − 1 − 2 = 6時</li></ol><p>答え: 6:35。</p>"
      "<h2>すべて秒に直す方法</h2><p>1時間=3600秒、1分=60秒に直して足し引きし、最後に3600や60で割って戻すと、繰り上がりを意識せずに済みます。</p>"
      "<p>計算結果は<a href='add-subtract.html'>足し引きツール</a>で検算できます。</p>")

    rows = "".join(f"<tr><td>{esc(n)}</td><td>{('+' if v >= 0 else '−')}{abs(v) // 60}:{abs(v) % 60:02d}</td></tr>" for n, v in ZONES)
    p("offset-table.html", "主な地域の標準時オフセット表",
      "日本・米国・欧州・アジアなど主な地域の標準時のUTCオフセットを一覧にしました(夏時間は含みません)。",
      "<h1>主な地域の標準時オフセット表</h1><table><tr><th>地域</th><th>UTCとの差(標準時)</th></tr>" + rows + "</table>"
      "<p class='note'>夏時間は含みません。制度は変更されることがあるため、最新の値は公式の情報で確認してください。<a href='timezone.html'>時差変換ツール</a>でもこの値を使っています。</p>")

    terms = [("UTC", "協定世界時。世界の標準時刻の基準"), ("オフセット", "UTCとのずれ(UTC+9など)"), ("標準時", "地域ごとに定められた基本の時刻"),
             ("夏時間", "夏の間だけ時計を進める制度"), ("24時間表記", "0〜23時で1日を表す方法"), ("12時間表記", "午前・午後に分けて表す方法"),
             ("60進法", "60ごとに繰り上がる数え方。時間・分・秒で使う"), ("経過時間", "開始から終了までの時間の長さ"), ("小数時間", "時間を0.25のような小数で表した値"),
             ("日またぎ", "計算の結果が翌日や前日の時刻になること")]
    p("glossary.html", "時間計算の用語集",
      "UTC・オフセット・標準時・夏時間・経過時間など、時間計算に出てくる基本用語をまとめました。",
      "<h1>時間計算の用語集</h1><table><tr><th>用語</th><th>意味</th></tr>"
      + "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in terms) + "</table>"
      "<p><a href='utc-and-offsets.html'>UTCとオフセット</a> / <a href='notation.html'>時刻の表記</a></p>")
