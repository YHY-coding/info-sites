"""お金の計算ツール集(住宅ローン・残業代・割引と消費税)。追加サイトのひな型を兼ねる。
規約: META と build(page, write) を持つ。出力パスは docs/<slug>/ 配下。nav は各サイトのルートからの相対パス。"""
import html

META = dict(slug="money-tools", name="お金の計算ツール集", desc="住宅ローン返済額・残業代・割引と消費税を、ブラウザだけで計算できる無料ツール")
SITE = dict(name=META["name"], home="index.html")
NAV = [("住宅ローン", "loan/index.html"), ("残業代", "overtime.html"), ("割引・消費税", "discount.html")]
DISC = ("本サイトの計算結果は目安です。実際の金額は、金融機関・勤務先の就業規則・契約内容で変わります。"
        "重要な判断の前には、必ず契約書や専門家の説明で確認してください。")


def esc(s):
    return html.escape(s, quote=True)


def monthly_payment(principal, annual_rate_pct, years):
    """元利均等返済の月々の返済額(円)。"""
    n = int(round(years * 12))
    r = annual_rate_pct / 100 / 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** (-n))


def yen(x):
    return f"{int(round(x)):,}円"


LOAN_JS = """
function pay(P,rate,years){var n=Math.round(years*12),r=rate/100/12;if(r===0)return P/n;return P*r/(1-Math.pow(1+r,-n))}
function f(x){return Math.round(x).toLocaleString('ja-JP')+'円'}
function run(){var P=parseFloat(document.getElementById('p').value)*10000,rate=parseFloat(document.getElementById('r').value),y=parseFloat(document.getElementById('y').value);
if(!(P>0)||!(y>0)||!(rate>=0)){document.getElementById('out').textContent='入力を確認してください';return}
var m=pay(P,rate,y),n=Math.round(y*12),total=m*n;
document.getElementById('out').innerHTML='<p class="big">毎月 '+f(m)+'</p><table><tr><th>総返済額</th><td>'+f(total)+'</td></tr><tr><th>うち利息</th><td>'+f(total-P)+'</td></tr><tr><th>返済回数</th><td>'+n+'回</td></tr></table>'}
document.getElementById('btn').onclick=run;run();
"""

OT_JS = """
function f(x){return Math.round(x).toLocaleString('ja-JP')+'円'}
function run(){var w=parseFloat(document.getElementById('w').value)*10000,h=parseFloat(document.getElementById('h').value);
var o=parseFloat(document.getElementById('o').value)||0,ho=parseFloat(document.getElementById('ho').value)||0,nt=parseFloat(document.getElementById('nt').value)||0;
if(!(w>0)||!(h>0)){document.getElementById('out').textContent='入力を確認してください';return}
var hr=w/h,o1=Math.min(o,60),o2=Math.max(o-60,0);
var a=hr*1.25*o1,b=hr*1.5*o2,c=hr*1.35*ho,d=hr*0.25*nt,t=a+b+c+d;
document.getElementById('out').innerHTML='<p class="big">割増賃金の合計 '+f(t)+'</p><table><tr><th>1時間あたりの基礎賃金</th><td>'+f(hr)+'</td></tr><tr><th>時間外(60時間以内・25%増)</th><td>'+f(a)+'</td></tr><tr><th>時間外(60時間超・50%増)</th><td>'+f(b)+'</td></tr><tr><th>法定休日(35%増)</th><td>'+f(c)+'</td></tr><tr><th>深夜(25%加算)</th><td>'+f(d)+'</td></tr></table>'}
document.getElementById('btn').onclick=run;run();
"""

DISC_JS = """
function f(x){return Math.round(x).toLocaleString('ja-JP')+'円'}
function run(){var p=parseFloat(document.getElementById('p').value),t=parseFloat(document.getElementById('t').value),d=parseFloat(document.getElementById('d').value)||0;
if(!(p>=0)){document.getElementById('out').textContent='入力を確認してください';return}
var disc=p*(1-d/100),inc=Math.floor(p*(1+t/100)),exc=Math.ceil(p/(1+t/100));
document.getElementById('out').innerHTML='<table><tr><th>'+d+'%引き後の価格</th><td>'+f(disc)+'</td></tr><tr><th>税抜として税込にすると</th><td>'+f(inc)+'</td></tr><tr><th>税込として税抜にすると</th><td>'+f(exc)+'</td></tr></table>'}
document.getElementById('btn').onclick=run;run();
"""

AMOUNTS = list(range(1000, 8500, 500))   # 万円
RATES = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
YEARS = [20, 25, 30, 35]


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)

    # トップ
    p("index.html", "お金の計算ツール集|住宅ローン・残業代・割引",
      "住宅ローンの返済額、残業代(割増賃金)、割引後の価格と消費税を、ブラウザだけで計算できる無料ツール集です。",
      "<h1>お金の計算ツール集</h1><p>入力した数字は、ブラウザの中だけで計算されます。サーバーには送信されません。</p>"
      "<div class='card'><a href='loan/index.html'><strong>住宅ローン返済シミュレーター</strong></a><br>借入額・金利・返済期間から、毎月の返済額と総返済額を計算</div>"
      "<div class='card'><a href='overtime.html'><strong>残業代(割増賃金)の計算</strong></a><br>時間外・深夜・休日の割増を含めた目安を計算</div>"
      "<div class='card'><a href='discount.html'><strong>割引・消費税の計算</strong></a><br>割引後の価格と、税込・税抜の変換</div>")

    # 住宅ローン計算ツール
    p("loan/index.html", "住宅ローン返済シミュレーター|毎月の返済額と総返済額",
      "借入額・金利・返済期間を入力すると、元利均等返済での毎月の返済額、総返済額、利息の合計を計算します。",
      "<h1>住宅ローン返済シミュレーター</h1><p>元利均等返済(毎月の返済額が一定)の場合の目安を計算します。</p>"
      "<div class='card'><label>借入額(万円) <input id='p' type='number' value='3000' min='1' step='100'></label><br>"
      "<label>年利(%) <input id='r' type='number' value='1.5' min='0' step='0.1'></label><br>"
      "<label>返済期間(年) <input id='y' type='number' value='35' min='1' step='1'></label><br><br>"
      "<button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>計算の前提</h2><ul><li>金利は返済期間中、変わらないものとして計算(固定金利のイメージ)</li><li>ボーナス返済・繰り上げ返済・各種手数料・保険料は含まない</li>"
      "<li>実際の返済額は、金融機関の計算方法(端数処理など)で、数十円〜数百円の差が出ることがあります</li></ul>"
      "<h2>借入額別の返済額一覧</h2><ul class='links'>"
      + "".join(f"<li><a href='{a}.html'>借入額{a:,}万円の毎月の返済額</a></li>" for a in AMOUNTS) + "</ul>"
      f"<script>{LOAN_JS}</script>")
    for i, a in enumerate(AMOUNTS):
        head = "".join(f"<th>{y}年</th>" for y in YEARS)
        rows = ""
        for r in RATES:
            rows += f"<tr><th>金利{r}%</th>" + "".join(f"<td>{yen(monthly_payment(a * 10000, r, y))}</td>" for y in YEARS) + "</tr>"
        m35 = monthly_payment(a * 10000, 1.5, 35)
        total35 = m35 * 35 * 12
        near = [x for x in AMOUNTS if x != a][max(0, i - 2):max(0, i - 2) + 4]
        links = "".join(f"<li><a href='{x}.html'>借入額{x:,}万円</a></li>" for x in near)
        p(f"loan/{a}.html", f"借入額{a:,}万円の住宅ローン|毎月の返済額(金利・期間別)",
          f"借入額{a:,}万円の住宅ローンの毎月の返済額を、金利0.5〜3.0%・返済期間20〜35年の組み合わせで一覧にしました。",
          f"<h1>借入額{a:,}万円の毎月の返済額</h1>"
          f"<p>元利均等返済の目安です。たとえば金利1.5%・35年なら、毎月<strong>{yen(m35)}</strong>、総返済額は約{yen(total35)}(うち利息{yen(total35 - a * 10000)})です。</p>"
          f"<table><tr><th></th>{head}</tr>{rows}</table>"
          "<p class='note'>ボーナス返済・手数料・保険料は含みません。</p>"
          f"<h2>ほかの借入額を見る</h2><ul class='links'>{links}</ul>"
          "<p><a href='index.html'>自分の条件で計算する</a></p>")

    # 残業代
    p("overtime.html", "残業代(割増賃金)の計算|時間外・深夜・休日",
      "月給と月平均所定労働時間から、時間外・深夜・休日労働の割増賃金の目安を計算します。",
      "<h1>残業代(割増賃金)の計算</h1><p>月給から1時間あたりの基礎賃金を出し、割増率をかけた目安を計算します。</p>"
      "<div class='card'><label>月給(万円・手当を除く基本分) <input id='w' type='number' value='25' min='1' step='0.5'></label><br>"
      "<label>月平均所定労働時間 <input id='h' type='number' value='160' min='1' step='1'></label><br>"
      "<label>時間外労働(時間) <input id='o' type='number' value='30' min='0' step='1'></label><br>"
      "<label>法定休日の労働(時間) <input id='ho' type='number' value='0' min='0' step='1'></label><br>"
      "<label>深夜(22時〜5時)の労働(時間) <input id='nt' type='number' value='0' min='0' step='1'></label><br><br><button id='btn'>計算する</button></div>"
      "<div id='out' class='card'></div>"
      "<h2>割増率の基本</h2><table><tr><th>種類</th><th>割増率</th></tr><tr><td>時間外労働(月60時間以内)</td><td>25%以上</td></tr><tr><td>時間外労働(月60時間超)</td><td>50%以上</td></tr>"
      "<tr><td>法定休日の労働</td><td>35%以上</td></tr><tr><td>深夜労働(22時〜5時)</td><td>25%以上(他の割増に加算)</td></tr></table>"
      "<h2>注意点</h2><ul><li>1時間あたりの基礎賃金には、通勤手当・家族手当・住宅手当など、法律で除外できる手当が含まれません。どの手当を除くかは、就業規則や給与明細で確認してください</li>"
      "<li>この計算では、時間外と深夜が重なる場合の加算を、深夜の時間に対して25%加算で近似しています。実際の取り扱いは、勤務先の規則で確認してください</li>"
      "<li>割増率は法律上の最低ラインで、会社が上乗せしている場合があります。割増の制度は改正されることがあるため、最新の情報は厚生労働省などの公式情報で確認してください</li></ul>"
      f"<script>{OT_JS}</script>")

    # 割引・消費税
    p("discount.html", "割引・消費税の計算|税込・税抜の変換",
      "割引後の価格と、税込・税抜の変換を計算します。消費税率は10%と8%(軽減税率)に対応。",
      "<h1>割引・消費税の計算</h1>"
      "<div class='card'><label>価格(円) <input id='p' type='number' value='1000' min='0' step='1'></label><br>"
      "<label>消費税率 <select id='t'><option value='10'>10%(標準)</option><option value='8'>8%(軽減税率)</option></select></label><br>"
      "<label>割引率(%) <input id='d' type='number' value='20' min='0' max='100' step='1'></label><br><br><button id='btn'>計算する</button></div>"
      "<div id='out' class='card'></div>"
      "<h2>計算のしかた</h2><ul><li>割引後の価格 = 価格 × (1 − 割引率)</li><li>税込価格 = 税抜価格 × (1 + 税率)(端数は切り捨てで表示)</li><li>税抜価格 = 税込価格 ÷ (1 + 税率)(端数は切り上げで表示)</li></ul>"
      "<p class='note'>端数の処理(切り捨て・切り上げ・四捨五入)は、店舗や請求書の方針で異なります。</p>"
      f"<script>{DISC_JS}</script>")
