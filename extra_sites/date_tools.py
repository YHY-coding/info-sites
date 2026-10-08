"""日付・年齢・和暦西暦変換・日数計算ツール集。規約: META と build(page, write) を持つ。出力は docs/date-tools/ 配下。"""
import datetime
import html

META = dict(slug="date-tools", name="日付・年齢・和暦ツール集", desc="年齢、日数、日付の加減算、曜日、和暦と西暦の変換を、ブラウザだけで計算できる無料ツール")
SITE = dict(name=META["name"], home="index.html")
NAV = [("年齢", "age.html"), ("日数", "days.html"), ("日付の加減算", "add.html"), ("曜日", "weekday.html"), ("和暦↔西暦", "wareki.html"), ("解説", "eras.html")]
DISC = ("本サイトの計算結果は目安です。契約・手続き・法律上の日数や年齢の数え方は、書類の記載や官公庁などの公式情報で確認してください。"
        "入力した日付は、ブラウザの中だけで計算され、送信されません。")

ERAS = [("令和", 2019, 5, 1), ("平成", 1989, 1, 8), ("昭和", 1926, 12, 25), ("大正", 1912, 7, 30), ("明治", 1868, 10, 23)]
ETO = "子丑寅卯辰巳午未申酉戌亥"
WD = "日月火水木金土"


def esc(s):
    return html.escape(s, quote=True)


# ---- Python側の基準実装(ブラウザ側JSと一致することを確認する) ----
def is_leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def dim(y, m):
    return [31, 29 if is_leap(y) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]


def to_day(y, m, d):
    return (datetime.date(y, m, d) - datetime.date(1970, 1, 1)).days


def weekday(y, m, d):
    """0=日曜"""
    return (datetime.date(y, m, d).weekday() + 1) % 7


def add_months(y, m, d, k):
    t = y * 12 + m - 1 + k
    ny, nm = t // 12, t % 12 + 1
    return ny, nm, min(d, dim(ny, nm))


def add_days(y, m, d, n):
    r = datetime.date(y, m, d) + datetime.timedelta(days=n)
    return r.year, r.month, r.day


def age(b, t):
    months = (t[0] - b[0]) * 12 + (t[1] - b[1])
    if t[2] < b[2]:
        months -= 1
    a = add_months(b[0], b[1], b[2], months)
    return months // 12, months % 12, to_day(*t) - to_day(*a)


def wareki(y, m, d):
    for name, sy, sm, sd in ERAS:
        if (y, m, d) >= (sy, sm, sd):
            return name, y - sy + 1
    return None


def from_wareki(name, n):
    for i, (nm, sy, sm, sd) in enumerate(ERAS):
        if nm == name:
            return sy + n - 1
    return None


def eto(y):
    return ETO[(y - 4) % 12]


# ---- ブラウザ側JS ----
CORE_JS = """
function leap(y){return y%4===0&&(y%100!==0||y%400===0)}
function dim(y,m){return [31,leap(y)?29:28,31,30,31,30,31,31,30,31,30,31][m-1]}
function toDay(y,m,d){var t=new Date(0);t.setUTCFullYear(y,m-1,d);return Math.round(t.getTime()/86400000)}
function fromDay(n){var t=new Date(n*86400000);return [t.getUTCFullYear(),t.getUTCMonth()+1,t.getUTCDate()]}
function weekday(y,m,d){return (((toDay(y,m,d)+4)%7)+7)%7}
function addMonths(y,m,d,k){var t=y*12+m-1+k,ny=Math.floor(t/12),nm=((t%12)+12)%12+1;return [ny,nm,Math.min(d,dim(ny,nm))]}
function addDays(y,m,d,n){return fromDay(toDay(y,m,d)+n)}
function age(b,t){var months=(t[0]-b[0])*12+(t[1]-b[1]);if(t[2]<b[2])months--;var a=addMonths(b[0],b[1],b[2],months);return [Math.floor(months/12),months%12,toDay(t[0],t[1],t[2])-toDay(a[0],a[1],a[2])]}
var ERAS=[['令和',2019,5,1],['平成',1989,1,8],['昭和',1926,12,25],['大正',1912,7,30],['明治',1868,10,23]];
function wareki(y,m,d){for(var i=0;i<ERAS.length;i++){var e=ERAS[i];if(y>e[1]||(y===e[1]&&(m>e[2]||(m===e[2]&&d>=e[3]))))return [e[0],y-e[1]+1]}return null}
function fromWareki(name,n){for(var i=0;i<ERAS.length;i++){if(ERAS[i][0]===name)return ERAS[i][1]+n-1}return null}
function eto(y){return '子丑寅卯辰巳午未申酉戌亥'.charAt((((y-4)%12)+12)%12)}
var WD='日月火水木金土';
function pd(id){var v=document.getElementById(id).value;if(!/^\\d{4}-\\d{2}-\\d{2}$/.test(v))return null;var a=v.split('-');return [parseInt(a[0],10),parseInt(a[1],10),parseInt(a[2],10)]}
function fd(a){return a[0]+'年'+a[1]+'月'+a[2]+'日('+WD.charAt(weekday(a[0],a[1],a[2]))+')'}
function bad(){document.getElementById('out').textContent='日付を確認してください'}
"""

AGE_JS = """
function run(){var b=pd('b'),t=pd('t');if(!b||!t||toDay(t[0],t[1],t[2])<toDay(b[0],b[1],b[2])){bad();return}
var a=age(b,t),next=addMonths(b[0],b[1],b[2],(a[0]+1)*12),left=toDay(next[0],next[1],next[2])-toDay(t[0],t[1],t[2]);
document.getElementById('out').innerHTML='<p class="big">満'+a[0]+'歳</p><table><tr><th>年月日で表すと</th><td>'+a[0]+'年'+a[1]+'か月'+a[2]+'日</td></tr><tr><th>生まれてからの日数</th><td>'+(toDay(t[0],t[1],t[2])-toDay(b[0],b[1],b[2])).toLocaleString('ja-JP')+'日</td></tr><tr><th>次の誕生日まで</th><td>あと'+left+'日</td></tr></table>'}
document.getElementById('btn').onclick=run;
(function(){var n=new Date();document.getElementById('t').value=n.getFullYear()+'-'+('0'+(n.getMonth()+1)).slice(-2)+'-'+('0'+n.getDate()).slice(-2);run()})();
"""

DAYS_JS = """
function run(){var a=pd('a'),b=pd('b');if(!a||!b){bad();return}
var n=toDay(b[0],b[1],b[2])-toDay(a[0],a[1],a[2]),s=n<0?-1:1,x=Math.abs(n),w=Math.floor(x/7);
document.getElementById('out').innerHTML='<p class="big">'+x.toLocaleString('ja-JP')+'日間'+(n<0?'(終了日の方が前)':'')+'</p><table><tr><th>初日を含めて数えると</th><td>'+(x+1).toLocaleString('ja-JP')+'日</td></tr><tr><th>週に直すと</th><td>'+w+'週と'+(x%7)+'日</td></tr></table>'}
document.getElementById('btn').onclick=run;run();
"""

ADD_JS = """
function run(){var a=pd('a'),n=parseInt(document.getElementById('n').value,10),u=document.getElementById('u').value,s=document.getElementById('s').value==='before'?-1:1;
if(!a||isNaN(n)){bad();return}
var r=u==='d'?addDays(a[0],a[1],a[2],s*n):addMonths(a[0],a[1],a[2],s*n*(u==='y'?12:1));
document.getElementById('out').innerHTML='<p class="big">'+fd(r)+'</p><table><tr><th>起点</th><td>'+fd(a)+'</td></tr></table>'}
document.getElementById('btn').onclick=run;run();
"""

WD_JS = """
function run(){var a=pd('a');if(!a){bad();return}
var w=weekday(a[0],a[1],a[2]),doy=toDay(a[0],a[1],a[2])-toDay(a[0],1,1)+1;
document.getElementById('out').innerHTML='<p class="big">'+WD.charAt(w)+'曜日</p><table><tr><th>その年の何日目か</th><td>'+doy+'日目('+(leap(a[0])?366:365)+'日中)</td></tr><tr><th>うるう年か</th><td>'+(leap(a[0])?'うるう年':'平年')+'</td></tr><tr><th>干支(その年)</th><td>'+eto(a[0])+'年</td></tr></table>'}
document.getElementById('btn').onclick=run;run();
"""

WAREKI_JS = """
function run(){var out='';var d=pd('a');
if(d){var w=wareki(d[0],d[1],d[2]);out+=(w&&d[0]>=1873)?'<p class="big">'+w[0]+(w[1]===1?'元':w[1])+'年</p>':'<p>1873年(明治6年)より前は、旧暦のため対応していません</p>'}
document.getElementById('o1').innerHTML=out;
var name=document.getElementById('e').value,n=parseInt(document.getElementById('n').value,10),o2='';
if(!isNaN(n)&&n>=1){var y=fromWareki(name,n);var ei=0;for(var i=0;i<ERAS.length;i++)if(ERAS[i][0]===name)ei=i;
var endY=ei>0?ERAS[ei-1][1]:null;
if(endY!==null&&y>endY)o2='<p>'+name+n+'年は存在しません</p>';else o2='<p class="big">西暦'+y+'年</p>'+((endY!==null&&y===endY)?'<p class="note">この年は途中で改元があります。月日によって元号が変わります。</p>':'')}
else o2='<p>年を確認してください</p>';
document.getElementById('o2').innerHTML=o2}
document.getElementById('btn').onclick=run;run();
"""


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)
    lab = "<label>%s <input id='%s' type='date' value='%s'></label><br>"

    p("index.html", "日付・年齢・和暦ツール集|年齢・日数・曜日・和暦西暦変換",
      "満年齢、2つの日付の間の日数、日付の加減算、曜日、和暦と西暦の変換を、ブラウザだけで計算できる無料ツール集です。",
      "<h1>日付・年齢・和暦ツール集</h1><p>入力した日付は、ブラウザの中だけで計算されます。サーバーには送信されません。</p>"
      "<div class='card'><a href='age.html'><strong>年齢計算</strong></a><br>生年月日から満年齢と、次の誕生日までの日数</div>"
      "<div class='card'><a href='days.html'><strong>日数計算</strong></a><br>2つの日付の間の日数</div>"
      "<div class='card'><a href='add.html'><strong>日付の加減算</strong></a><br>○日後・○か月前・○年後の日付</div>"
      "<div class='card'><a href='weekday.html'><strong>曜日の計算</strong></a><br>日付から曜日・その年の何日目か</div>"
      "<div class='card'><a href='wareki.html'><strong>和暦⇔西暦の変換</strong></a><br>令和・平成・昭和・大正・明治</div>"
      "<h2>解説ページ</h2><ul class='links'><li><a href='eras.html'>元号と改元の日付</a></li><li><a href='wareki-table.html'>西暦・和暦・干支の対応表</a></li>"
      "<li><a href='leap-year.html'>うるう年のルール</a></li><li><a href='age-counting.html'>満年齢と数え年の違い</a></li></ul>")

    p("age.html", "年齢計算|生年月日から満年齢を計算",
      "生年月日と基準日から、満年齢、年月日での年齢、次の誕生日までの日数を計算します。",
      "<h1>年齢計算</h1><p>誕生日の当日に1歳加わる、一般的な数え方で計算します。</p><div class='card'>"
      + lab % ("生年月日", "b", "2000-01-01") + lab % ("基準日", "t", "2026-01-01")
      + "<br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>注意点</h2><ul><li>2月29日生まれの人は、平年は3月1日に加齢する計算にしています。法律上の扱いは、公式の情報で確認してください</li>"
      "<li>数え年は<a href='age-counting.html'>満年齢と数え年の違い</a>を参照してください</li></ul>"
      f"<script>{CORE_JS}{AGE_JS}</script>")

    p("days.html", "日数計算|2つの日付の間の日数",
      "開始日と終了日を入力すると、間の日数、初日を含めた日数、週数を計算します。",
      "<h1>日数計算</h1><div class='card'>" + lab % ("開始日", "a", "2026-01-01") + lab % ("終了日", "b", "2026-12-31")
      + "<br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>数え方の違い</h2><ul><li>開始日の翌日から終了日までを数えるか、開始日も1日目として数えるかで、結果が1日変わります。両方を表示しています</li>"
      "<li>契約書や手続きの期間の数え方(初日を算入するか)は、書類の定めや公式の情報で確認してください</li></ul>"
      f"<script>{CORE_JS}{DAYS_JS}</script>")

    p("add.html", "日付の加減算|○日後・○か月前の日付",
      "起点の日付から、○日後・○日前・○か月後・○年後などの日付を計算します。",
      "<h1>日付の加減算</h1><div class='card'>" + lab % ("起点の日付", "a", "2026-01-31")
      + "<label><input id='n' type='number' value='30' step='1'> <select id='u'><option value='d'>日</option><option value='m'>か月</option><option value='y'>年</option></select> "
      "<select id='s'><option value='after'>後</option><option value='before'>前</option></select></label><br><br>"
      "<button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>月末の扱い</h2><p>「か月後」「年後」で、行き先の月に同じ日がない場合は、その月の末日にします(例:1月31日の1か月後は2月の末日)。この扱いは目安で、契約上の期間計算は書類の定めや公式の情報で確認してください。</p>"
      f"<script>{CORE_JS}{ADD_JS}</script>")

    p("weekday.html", "曜日の計算|日付から曜日を調べる",
      "日付を入力すると、曜日、その年の何日目か、うるう年かどうか、干支を表示します。",
      "<h1>曜日の計算</h1><div class='card'>" + lab % ("日付", "a", "2026-01-01")
      + "<br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<p>グレゴリオ暦(現在使われている暦)に基づく計算です。日本で採用された1873年より前の日付は、当時の暦と一致しません。</p>"
      f"<script>{CORE_JS}{WD_JS}</script>")

    opts = "".join(f"<option>{e[0]}</option>" for e in ERAS)
    p("wareki.html", "和暦⇔西暦の変換|令和・平成・昭和・大正・明治",
      "西暦の日付から和暦(元号と年)を、和暦の年から西暦を計算します。改元の日付を考慮します。",
      "<h1>和暦⇔西暦の変換</h1><h2>西暦の日付から和暦へ</h2><div class='card'>" + lab % ("日付", "a", "2026-01-01")
      + "<div id='o1'></div></div><h2>和暦から西暦へ</h2><div class='card'><label>元号 <select id='e'>" + opts + "</select></label> "
      "<label><input id='n' type='number' value='1' min='1' step='1'>年</label><div id='o2'></div></div><button id='btn'>計算する</button>"
      "<p class='note'>改元の日付は<a href='eras.html'>元号と改元の日付</a>、年ごとの対応は<a href='wareki-table.html'>対応表</a>にあります。</p>"
      f"<script>{CORE_JS}{WAREKI_JS}</script>")

    rows = "".join(f"<tr><td>{n}</td><td>{sy}年{sm}月{sd}日</td></tr>" for n, sy, sm, sd in ERAS)
    p("eras.html", "元号と改元の日付|明治から令和まで",
      "明治から令和までの元号と、改元(元号が変わる)日付の一覧、和暦と西暦の換算の考え方を解説します。",
      "<h1>元号と改元の日付</h1><table><tr><th>元号</th><th>始まりの日(西暦)</th></tr>" + rows + "</table>"
      "<p class='note'>明治の始まりは、新暦に直した日付です。当時の暦は旧暦でした。</p>"
      "<h2>換算の考え方</h2><ul><li>元号の元年は、その元号が始まった年です。西暦 = 元号の始まりの年 + 和暦の年 − 1</li>"
      "<li>改元があった年は、同じ西暦の年に2つの元号が存在します(例:1989年は昭和64年と平成元年)。月日で判断します</li>"
      "<li>元年は「1年」ではなく「元年」と書くのが一般的です</li></ul>"
      "<p><a href='wareki.html'>変換ツールを使う</a> / <a href='wareki-table.html'>対応表を見る</a></p>")

    trs = ""
    for y in range(1950, 2051):
        w = wareki(y, 12, 31)
        trs += f"<tr><td>{y}</td><td>{w[0]}{w[1]}</td><td>{eto(y)}</td></tr>"
    p("wareki-table.html", "西暦・和暦・干支の対応表|1950〜2050年",
      "1950年から2050年までの、西暦、和暦、干支(十二支)の対応表です。",
      "<h1>西暦・和暦・干支の対応表</h1><p>和暦はその年の年末時点の元号です。改元のあった年(1989年・2019年)は、前の元号の期間もあります。"
      "2050年までは参考値で、将来の元号は未定のため、令和が続くものとして表示しています。</p>"
      "<table><tr><th>西暦</th><th>和暦</th><th>干支</th></tr>" + trs + "</table>"
      "<p class='note'>干支は十二支のみ。年は1月1日で切り替えています(立春で切り替える数え方もあります)。</p>")

    p("leap-year.html", "うるう年のルール|2月29日がある年",
      "うるう年(2月が29日ある年)の決まりと、なぜ必要か、日数計算での注意点を解説します。",
      "<h1>うるう年のルール</h1><p>地球が太陽を1周する時間は約365.24日です。1年を365日にすると少しずつずれるため、約4年に一度、2月29日を加えます。</p>"
      "<h2>判定のルール(グレゴリオ暦)</h2><ol><li>西暦が4で割り切れる年はうるう年</li><li>ただし、100で割り切れる年は平年</li><li>ただし、400で割り切れる年はうるう年</li></ol>"
      "<table><tr><th>年</th><th>判定</th><th>理由</th></tr><tr><td>2024</td><td>うるう年</td><td>4で割り切れ、100では割り切れない</td></tr>"
      "<tr><td>2100</td><td>平年</td><td>100で割り切れ、400では割り切れない</td></tr><tr><td>2000</td><td>うるう年</td><td>400で割り切れる</td></tr>"
      "<tr><td>2026</td><td>平年</td><td>4で割り切れない</td></tr></table>"
      "<h2>日数計算での注意</h2><ul><li>うるう年は1年が366日になります</li><li>2月29日生まれの年齢の数え方は<a href='age-counting.html'>満年齢と数え年の違い</a>を参照</li></ul>"
      "<p><a href='weekday.html'>曜日の計算</a>でも、うるう年かどうかを表示します。</p>")

    p("age-counting.html", "満年齢と数え年の違い|年齢の数え方",
      "満年齢と数え年の数え方の違いと、計算の考え方、使われる場面を解説します。",
      "<h1>満年齢と数え年の違い</h1>"
      "<h2>満年齢</h2><p>生まれた日を0歳とし、誕生日を迎えるたびに1歳ずつ増える数え方です。現在、日常生活や公的な手続きで一般的に使われます。</p>"
      "<h2>数え年</h2><p>生まれた年を1歳とし、元日(1月1日)を迎えるたびに1歳増える数え方です。厄年や祝い事など、伝統的な行事で使われることがあります。</p>"
      "<h2>計算の目安</h2><ul><li>数え年 = 現在の西暦 − 生まれた西暦 + 1</li><li>満年齢は、誕生日を迎える前は「数え年 − 2」、迎えた後は「数え年 − 1」</li></ul>"
      "<table><tr><th>生まれ</th><th>2026年の誕生日前</th><th>2026年の誕生日後</th></tr>"
      "<tr><td>2000年</td><td>満25歳(数え27歳)</td><td>満26歳(数え27歳)</td></tr>"
      "<tr><td>2010年</td><td>満15歳(数え17歳)</td><td>満16歳(数え17歳)</td></tr></table>"
      "<p class='note'>2月29日生まれの人が、平年にいつ加齢するかなど、法律上の細かな扱いは公式の情報で確認してください。</p>"
      "<p><a href='age.html'>年齢計算ツール</a></p>")
