"""料理の分量換算ツール集(大さじ・小さじ・カップ・グラム・合・オーブン温度・人数換算)。
規約: META と build(page, write) を持つ。出力は docs/cooking-converter/ 配下。"""
import html
import json

META = dict(slug="cooking-converter", name="料理の分量換算ツール集",
            desc="大さじ・小さじ・カップ・ml・グラム、米の合数、オーブン温度、人数分の換算を、ブラウザだけで計算できる無料ツール")
SITE = dict(name=META["name"], home="index.html")
NAV = [("体積", "volume.html"), ("グラム", "weight.html"), ("お米", "rice.html"), ("人数", "servings.html"),
       ("温度", "oven.html"), ("早見表", "tables.html"), ("コツ", "measuring-tips.html"), ("用語", "terms.html"), ("FAQ", "faq.html")]
DISC = ("本サイトの換算結果は概算・目安です。食材の種類・銘柄・詰め方で重さは変わります。"
        "計量スプーンやカップの容量、調理器具の設定は、商品の取扱説明書や公式の情報で確認してください。"
        "入力した数値は、ブラウザの中だけで計算され、送信されません。")


def esc(s):
    return html.escape(s, quote=True)


# ---- データ ----
# 体積単位: (キー, 表示名, mlあたりの大きさ)
VOL_UNITS = [
    ("ml", "ミリリットル(ml・cc)", 1.0),
    ("L", "リットル(L)", 1000.0),
    ("tsp", "小さじ(日本・5ml)", 5.0),
    ("tbsp", "大さじ(日本・15ml)", 15.0),
    ("cup", "計量カップ(日本・200ml)", 200.0),
    ("go", "1合(180ml)", 180.0),
    ("ustsp", "米国ティースプーン(約4.93ml)", 4.92892159375),
    ("ustbsp", "米国テーブルスプーン(約14.79ml)", 14.78676478125),
    ("uscup", "米国カップ(約237ml)", 236.5882365),
    ("usfloz", "米国液量オンス(約29.57ml)", 29.5735295625),
]

# 食材: (キー, 表示名, 小さじ1杯のg, 大さじ1杯のg, 1カップ(200ml)のg)  ※一般的な目安値
INGREDIENTS = [
    ("water", "水・酒・酢", 5, 15, 200),
    ("milk", "牛乳", 5, 15, 210),
    ("oil", "サラダ油", 4, 12, 180),
    ("shoyu", "しょうゆ", 6, 18, 230),
    ("miso", "みそ", 6, 18, 230),
    ("mirin", "みりん", 6, 18, 230),
    ("salt", "食塩(精製塩)", 6, 18, 240),
    ("sugar", "上白糖", 3, 9, 130),
    ("gran", "グラニュー糖", 4, 12, 180),
    ("flour", "小麦粉(薄力粉)", 3, 9, 110),
    ("starch", "片栗粉", 3, 9, 130),
    ("panko", "パン粉(乾燥)", 1, 3, 40),
    ("butter", "バター", 4, 12, 180),
    ("mayo", "マヨネーズ", 4, 12, 190),
    ("ketchup", "トマトケチャップ", 5, 15, 230),
    ("honey", "はちみつ", 7, 21, 280),
]
SPOON_UNITS = [("tsp", "小さじ", 2), ("tbsp", "大さじ", 3), ("cup", "カップ(200ml)", 4)]

GO_ML = 180          # 1合の体積(ml)
GO_RICE_G = 150      # 1合の生米の重さの目安(g)
COOKED_RATIO = 2.2   # 炊きあがりの重さ ÷ 生米の重さ の目安
WATER_RATIO = 1.2    # 白米の水加減(米の体積に対する倍率)の目安


# ---- Python側の基準実装(ブラウザ側JSと一致することを node で確認する) ----
def convert_volume(v, frm, to):
    ml = {k: s for k, _, s in VOL_UNITS}
    return v * ml[frm] / ml[to]


def spoon_to_grams(n, ing, unit):
    row = {r[0]: r for r in INGREDIENTS}[ing]
    idx = {"tsp": 2, "tbsp": 3, "cup": 4}[unit]
    return n * row[idx]


def grams_to_spoon(g, ing, unit):
    row = {r[0]: r for r in INGREDIENTS}[ing]
    idx = {"tsp": 2, "tbsp": 3, "cup": 4}[unit]
    return g / row[idx]


def rice(go):
    return dict(ml=go * GO_ML, raw_g=go * GO_RICE_G, cooked_g=go * GO_RICE_G * COOKED_RATIO, water_ml=go * GO_ML * WATER_RATIO)


def rice_from_grams(g):
    return g / GO_RICE_G


def scale(amount, frm, to):
    return amount * to / frm


def c_to_f(c):
    return c * 9 / 5 + 32


def f_to_c(f):
    return (f - 32) * 5 / 9


# ---- ブラウザ側JS(DOM部分は document がある場合のみ動く) ----
CORE_JS = """
var DATA=__DATA__;
function convertVolume(v,a,b){return v*DATA.vol[a]/DATA.vol[b]}
function spoonToGrams(n,ing,u){return n*DATA.ing[ing][u]}
function gramsToSpoon(g,ing,u){return g/DATA.ing[ing][u]}
function rice(go){return {ml:go*DATA.go.ml,raw_g:go*DATA.go.raw,cooked_g:go*DATA.go.raw*DATA.go.cooked,water_ml:go*DATA.go.ml*DATA.go.water}}
function riceFromGrams(g){return g/DATA.go.raw}
function scale(a,f,t){return a*t/f}
function cToF(c){return c*9/5+32}
function fToC(f){return (f-32)*5/9}
function fmt(x){if(!isFinite(x))return '-';var a=Math.abs(x);if(a!==0&&(a<0.001||a>=1e9))return x.toExponential(3);return (Math.round(x*10000)/10000).toLocaleString('ja-JP',{maximumFractionDigits:4})}
function $(id){return document.getElementById(id)}
if(typeof module!=='undefined')module.exports={convertVolume:convertVolume,spoonToGrams:spoonToGrams,gramsToSpoon:gramsToSpoon,rice:rice,riceFromGrams:riceFromGrams,scale:scale,cToF:cToF,fToC:fToC};
"""

VOLUME_JS = """
if(typeof document!=='undefined'){
function run(){var v=parseFloat($('v').value),a=$('a').value,b=$('b').value;
if(!isFinite(v)||v<0){$('out').textContent='0以上の数値を入力してください';return}
var h='<p class="big">'+fmt(convertVolume(v,a,b))+' '+DATA.vn[b]+'</p><table><tr><th>単位</th><th>値</th></tr>';
for(var k in DATA.vol){h+='<tr><td>'+DATA.vn[k]+'</td><td>'+fmt(convertVolume(v,a,k))+'</td></tr>'}
$('out').innerHTML=h+'</table>'}
$('btn').onclick=run;run()}
"""

WEIGHT_JS = """
if(typeof document!=='undefined'){
function run(){var n=parseFloat($('n').value),ing=$('ing').value,u=$('u').value,g=parseFloat($('g').value);
if(!isFinite(n)||n<0||!isFinite(g)||g<0){$('out').textContent='0以上の数値を入力してください';return}
$('out').innerHTML='<table><tr><th>'+DATA.un[u]+' '+fmt(n)+' 杯分の重さ</th><td>約 '+fmt(spoonToGrams(n,ing,u))+' g</td></tr>'
+'<tr><th>'+fmt(g)+' g は</th><td>約 '+fmt(gramsToSpoon(g,ing,u))+' '+DATA.un[u]+'</td></tr></table>'}
$('btn').onclick=run;run()}
"""

RICE_JS = """
if(typeof document!=='undefined'){
function run(){var go=parseFloat($('go').value),g=parseFloat($('g').value);
if(!isFinite(go)||go<0||!isFinite(g)||g<0){$('out').textContent='0以上の数値を入力してください';return}
var r=rice(go);
$('out').innerHTML='<table><tr><th>'+fmt(go)+'合の米の体積</th><td>'+fmt(r.ml)+' ml</td></tr><tr><th>生米の重さ(目安)</th><td>約 '+fmt(r.raw_g)+' g</td></tr>'
+'<tr><th>水の量(米の1.2倍の目安)</th><td>約 '+fmt(r.water_ml)+' ml</td></tr><tr><th>炊きあがりの重さ(約2.2倍の目安)</th><td>約 '+fmt(r.cooked_g)+' g</td></tr>'
+'<tr><th>生米 '+fmt(g)+' g は</th><td>約 '+fmt(riceFromGrams(g))+' 合</td></tr></table>'}
$('btn').onclick=run;run()}
"""

SERV_JS = """
if(typeof document!=='undefined'){
function run(){var f=parseFloat($('f').value),t=parseFloat($('t').value),lines=$('lines').value.split('\\n'),h='';
if(!(f>0)||!(t>=0)){$('out').textContent='人数は正の数で入力してください';return}
for(var i=0;i<lines.length;i++){var s=lines[i].trim();if(!s)continue;
var m=s.match(/^(.*?)([0-9]+(?:\\.[0-9]+)?)(.*)$/);
if(m){h+='<tr><td>'+esc(m[1])+'<strong>'+fmt(scale(parseFloat(m[2]),f,t))+'</strong>'+esc(m[3])+'</td></tr>'}else{h+='<tr><td>'+esc(s)+'</td></tr>'}}
$('out').innerHTML=h?'<table>'+h+'</table>':'材料を1行に1つ入力してください'}
function esc(s){return s.replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
$('btn').onclick=run;run()}
"""

OVEN_JS = """
if(typeof document!=='undefined'){
function run(){var c=parseFloat($('c').value),f=parseFloat($('f').value);
if(!isFinite(c)||!isFinite(f)){$('out').textContent='数値を入力してください';return}
$('out').innerHTML='<table><tr><th>'+fmt(c)+' ℃ は</th><td>'+fmt(cToF(c))+' ℉</td></tr><tr><th>'+fmt(f)+' ℉ は</th><td>'+fmt(fToC(f))+' ℃</td></tr></table>'}
$('btn').onclick=run;run()}
"""


def data_js():
    d = dict(
        vol={k: s for k, _, s in VOL_UNITS},
        vn={k: n for k, n, _ in VOL_UNITS},
        ing={k: dict(tsp=a, tbsp=b, cup=c) for k, _, a, b, c in INGREDIENTS},
        un={k: n for k, n, _ in SPOON_UNITS},
        go=dict(ml=GO_ML, raw=GO_RICE_G, cooked=COOKED_RATIO, water=WATER_RATIO),
    )
    return CORE_JS.replace("__DATA__", json.dumps(d, ensure_ascii=False))


def script(extra):
    return f"<script>{data_js()}{extra}</script>"


def n(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return s


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)
    vopts = "".join(f"<option value='{k}'>{esc(nm)}</option>" for k, nm, _ in VOL_UNITS)
    iopts = "".join(f"<option value='{k}'>{esc(nm)}</option>" for k, nm, *_ in INGREDIENTS)
    uopts = "".join(f"<option value='{k}'>{esc(nm)}</option>" for k, nm, _ in SPOON_UNITS)

    p("index.html", "料理の分量換算ツール集|大さじ・小さじ・カップ・グラム",
      "大さじ・小さじ・カップ・ml・グラムの換算、米の合数、オーブン温度、人数分の換算をブラウザだけで計算できる無料ツール集です。",
      "<h1>料理の分量換算ツール集</h1><p>レシピの分量を、手元の計量道具に合わせて換算します。入力した数字は、ブラウザの中だけで計算され、送信されません。</p>"
      "<div class='card'><a href='volume.html'><strong>体積の換算(大さじ・小さじ・カップ・ml)</strong></a><br>日本と米国の計量単位をまとめて換算</div>"
      "<div class='card'><a href='weight.html'><strong>食材ごとのグラム換算</strong></a><br>しょうゆ・砂糖・小麦粉などを、大さじ・小さじ・カップとグラムで相互に換算</div>"
      "<div class='card'><a href='rice.html'><strong>お米の合数・グラム・水の量</strong></a><br>1合の体積と重さ、水加減、炊きあがりの目安</div>"
      "<div class='card'><a href='servings.html'><strong>人数分の換算(レシピの分量を増減)</strong></a><br>材料の数字を、指定した人数分に自動で書き換え</div>"
      "<div class='card'><a href='oven.html'><strong>温度の換算(℃と℉)</strong></a><br>海外レシピのオーブン温度を日本の設定に</div>"
      "<h2>解説・早見表</h2><ul class='links'><li><a href='tables.html'>大さじ・小さじ・カップの早見表</a></li>"
      "<li><a href='measuring-tips.html'>計量のコツと失敗しやすい点</a></li><li><a href='terms.html'>「少々」「ひとつまみ」「適量」の目安</a></li>"
      "<li><a href='faq.html'>よくある質問(日米のカップの違いなど)</a></li></ul>")

    p("volume.html", "体積の換算|大さじ・小さじ・カップ・mlの変換ツール",
      "大さじ・小さじ・計量カップ・ml・合・米国カップなどの体積を相互に換算します。日本と米国の単位の違いも確認できます。",
      "<h1>体積の換算</h1><p>量と単位を選ぶと、ほかのすべての単位に換算した値を一覧で表示します。</p>"
      "<div class='card'><label>量 <input id='v' type='number' value='2' min='0' step='any'></label><br>"
      f"<label>換算元 <select id='a'>{vopts}</select></label><br>"
      f"<label>換算先 <select id='b'>{vopts}</select></label><br><br><button id='btn'>換算する</button></div><div id='out' class='card'></div>"
      "<h2>換算の前提</h2><ul><li>日本の小さじ=5ml、大さじ=15ml、計量カップ=200mlとして計算しています</li><li>1合=180mlは、お米を量る単位としての値です</li>"
      "<li>米国の単位は、米国で一般に使われる定義に基づく概算です(表示用に別の値を使う場合があります)</li>"
      "<li>体積の換算であり、重さ(グラム)ではありません。重さは<a href='weight.html'>食材ごとのグラム換算</a>で確認してください</li></ul>"
      + script(VOLUME_JS))
    p("weight.html", "食材ごとのグラム換算|大さじ・小さじ・カップとグラム",
      "しょうゆ・砂糖・小麦粉・バターなどの食材ごとに、大さじ・小さじ・カップとグラムを相互に換算します。",
      "<h1>食材ごとのグラム換算</h1><p>同じ大さじ1杯でも、食材によって重さが違います。よく使う食材の目安値で換算します。</p>"
      f"<div class='card'><label>食材 <select id='ing'>{iopts}</select></label><br>"
      f"<label>計量道具 <select id='u'>{uopts}</select></label><br>"
      "<label>杯数 <input id='n' type='number' value='2' min='0' step='any'></label><br>"
      "<label>グラム数 <input id='g' type='number' value='100' min='0' step='any'></label><br><br><button id='btn'>換算する</button></div><div id='out' class='card'></div>"
      "<h2>この換算について</h2><ul><li>値は一般的な目安で、銘柄・水分量・詰め方で数%〜1割以上ずれることがあります</li>"
      "<li>粉類は、ふるったか、押し込んだかで重さが変わります</li><li>正確さが必要な菓子づくりなどは、キッチンスケールで量るのが確実です</li>"
      "<li>スプーンはすりきり1杯を前提としています。山盛りや半分の量は、<a href='measuring-tips.html'>計量のコツ</a>を参照</li></ul>"
      + script(WEIGHT_JS))

    p("rice.html", "お米の合数・グラム・水の量の換算|1合は何グラム?",
      "お米の合数から、体積・生米の重さ・水の量・炊きあがりの重さの目安を計算します。1合=180mlの意味も解説。",
      "<h1>お米の合数・グラム・水の量</h1>"
      "<div class='card'><label>お米の量(合) <input id='go' type='number' value='2' min='0' step='any'></label><br>"
      "<label>生米の重さ(g) <input id='g' type='number' value='300' min='0' step='any'></label><br><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>目安の考え方</h2><ul><li>1合は180mlです。これは炊飯器に付属する計量カップの大きさで、一般の計量カップ(200ml)とは違います</li>"
      "<li>白米1合は、生米でおよそ150gが目安です(米の品種や乾燥状態で多少変わります)</li>"
      "<li>水加減は、白米なら米の体積の1.2倍前後が一般的な目安です。炊飯器の内釜の目盛りがある場合は、そちらを優先してください</li>"
      "<li>炊きあがりの重さは、生米の約2.2倍が目安です</li>"
      "<li>玄米・雑穀米・炊き込みごはんは、水加減が異なります。商品の表示や炊飯器の説明書で確認してください</li></ul>"
      + script(RICE_JS))

    p("servings.html", "人数分の換算|レシピの材料を増減する計算ツール",
      "レシピの材料の数字を、何人分から何人分へ、自動で倍率計算します。1行に1材料で入力するだけ。",
      "<h1>人数分の換算</h1><p>材料を1行に1つずつ入力し、元の人数と作りたい人数を入れると、各行の数字を倍率計算します。</p>"
      "<div class='card'><label>元のレシピの人数 <input id='f' type='number' value='2' min='0.5' step='any'></label><br>"
      "<label>作りたい人数 <input id='t' type='number' value='5' min='0' step='any'></label><br>"
      "<label>材料(1行に1つ)<br><textarea id='lines' rows='6' cols='36'>鶏もも肉 300g\n玉ねぎ 1個\n水 200ml\nしょうゆ 大さじ2\n砂糖 小さじ1.5</textarea></label><br><br><button id='btn'>換算する</button></div>"
      "<div id='out' class='card'></div>"
      "<h2>倍率計算の注意</h2><ul><li>行の最初に出てくる数字だけを倍率計算します。「1/2個」のような分数は、小数(0.5)に直して入力してください</li>"
      "<li>調味料や香辛料は、量を単純に倍にすると濃すぎることがあります。人数を大きく変えるときは、味を見ながら調整してください</li>"
      "<li>加熱時間・鍋の大きさ・オーブンの温度は、量に比例して変わらないことがあります</li></ul>"
      + script(SERV_JS))

    p("oven.html", "温度の換算|オーブン温度 ℃と℉の変換ツール",
      "摂氏(℃)と華氏(℉)を相互に換算します。海外レシピのオーブン温度を、日本の設定にするときに便利です。",
      "<h1>温度の換算(℃と℉)</h1>"
      "<div class='card'><label>摂氏 ℃ <input id='c' type='number' value='180' step='any'></label><br>"
      "<label>華氏 ℉ <input id='f' type='number' value='350' step='any'></label><br><br><button id='btn'>換算する</button></div><div id='out' class='card'></div>"
      "<h2>式</h2><ul><li>華氏 = 摂氏 × 9 ÷ 5 + 32</li><li>摂氏 = (華氏 − 32) × 5 ÷ 9</li></ul>"
      "<h2>オーブン温度の注意</h2><ul><li>換算した値は数学的な変換です。実際には、オーブンの機種により庫内温度や熱の回り方が異なります</li>"
      "<li>海外レシピでは、「ファンあり(コンベクション)」の設定を前提としている場合があります。機器の説明書で確認してください</li>"
      "<li>換算後は、予熱時間や焼き色を見ながら、焼き時間を調整してください</li></ul>"
      + script(OVEN_JS))

    # 早見表
    spoon_ml = [("小さじ1/2", 2.5), ("小さじ1", 5), ("小さじ2", 10), ("大さじ1/2", 7.5), ("大さじ1", 15), ("大さじ2", 30), ("大さじ3", 45), ("大さじ4", 60),
                ("計量カップ1/4", 50), ("計量カップ1/2", 100), ("計量カップ1", 200), ("1合", 180)]
    t1 = "".join(f"<tr><td>{a}</td><td>{n(b)}ml</td><td>{n(b / 5)}</td><td>{n(b / 15)}</td></tr>" for a, b in spoon_ml)
    t2 = "".join(f"<tr><th>{esc(nm)}</th><td>{a}g</td><td>{b}g</td><td>{c}g</td></tr>" for _, nm, a, b, c in INGREDIENTS)
    p("tables.html", "大さじ・小さじ・カップの早見表|ml・グラム換算",
      "大さじ・小さじ・計量カップのmlと、食材ごとのグラム数の目安を一覧にした早見表です。",
      "<h1>大さじ・小さじ・カップの早見表</h1><h2>容量(ml)の早見表</h2>"
      f"<table><tr><th>計量</th><th>容量</th><th>小さじ換算</th><th>大さじ換算</th></tr>{t1}</table>"
      "<h2>食材ごとの重さの目安(すりきり)</h2>"
      f"<table><tr><th>食材</th><th>小さじ1</th><th>大さじ1</th><th>カップ1(200ml)</th></tr>{t2}</table>"
      "<p class='note'>重さは一般的な目安です。銘柄・詰め方で変わるため、正確さが必要な場合はスケールで量ってください。</p>"
      "<p><a href='weight.html'>食材を選んで換算する</a> / <a href='volume.html'>体積を換算する</a></p>")

    p("measuring-tips.html", "計量のコツ|スプーンとカップで失敗しないために",
      "計量スプーン・計量カップ・キッチンスケールの使い方と、計量でありがちな失敗の防ぎ方を整理しました。",
      "<h1>計量のコツと失敗しやすい点</h1>"
      "<h2>計量スプーン</h2><ul><li><strong>すりきり</strong>: 粉類は、山盛りにしてからヘラなどで平らにならす</li>"
      "<li><strong>半分</strong>: すりきり1杯から、ヘラで中央を境に半分をかき出す</li>"
      "<li><strong>液体</strong>: 表面張力で少し盛り上がるくらいまで入れる。こぼれる直前が1杯の目安</li>"
      "<li>粉類はふるうと軽くなり、同じ1杯でも重さが変わる</li></ul>"
      "<h2>計量カップ</h2><ul><li>平らな場所に置き、真横から目盛りを読む</li><li>粉類を量るときは、押し込まずにふんわり入れ、すりきりにする</li>"
      "<li>お米用の1合カップ(180ml)と、計量カップ(200ml)は別物</li></ul>"
      "<h2>キッチンスケール</h2><ul><li>容器を載せてから、ゼロに合わせる(風袋引き)</li><li>少量(数g)は、0.1g単位のスケールが向く</li><li>粉類・バター・砂糖はグラムで量ると再現性が高い</li></ul>"
      "<h2>失敗しやすい点</h2><ul><li>mlとgは別。水以外の液体は、同じ体積でも重さが違う</li><li>レシピが日本式か米国式かを確認する(<a href='faq.html'>カップの違い</a>)</li>"
      "<li>換算した端数は、無理に合わせず、切りのよい量に丸めてよい場合が多い</li></ul>"
      "<p><a href='tables.html'>早見表を見る</a></p>")

    p("terms.html", "「少々」「ひとつまみ」「適量」の目安|レシピ用語",
      "レシピによく出てくる「少々」「ひとつまみ」「適量」「適宜」などの分量表現の一般的な意味を解説します。",
      "<h1>「少々」「ひとつまみ」「適量」の目安</h1><p>レシピの分量表現は、厳密な定義がないものもあります。ここでは一般的に使われる意味を紹介します(目安です)。</p>"
      "<table><tr><th>表現</th><th>一般的な意味</th></tr>"
      "<tr><td>少々</td><td>親指と人差し指の2本でつまんだ程度の少量。小さじ1/8未満とされることが多い</td></tr>"
      "<tr><td>ひとつまみ</td><td>親指・人差し指・中指の3本でつまんだ量。少々より多め</td></tr>"
      "<tr><td>適量</td><td>好みや状況に合わせて、ちょうどよい量を使う</td></tr>"
      "<tr><td>適宜</td><td>必要に応じて入れる。入れなくてもよい</td></tr>"
      "<tr><td>お好みで</td><td>好みで量を決める、または入れなくてもよい</td></tr>"
      "<tr><td>ひたひた</td><td>材料の頭が少し見える程度の水分の量</td></tr>"
      "<tr><td>かぶるくらい</td><td>材料が水分にすっかり浸かる量</td></tr></table>"
      "<p class='note'>指の大きさや食材の粒の細かさで、実際の量は変わります。迷うときは、少なめから入れて味を見るのが無難です。</p>"
      "<p><a href='measuring-tips.html'>計量のコツ</a> / <a href='tables.html'>早見表</a></p>")

    p("faq.html", "料理の分量換算のよくある質問|カップの違い・ml・g",
      "日本と米国のカップの違い、1合と1カップの違い、mlとグラムの違いなど、分量換算のよくある疑問に答えます。",
      "<h1>よくある質問</h1>"
      "<h2>日本のカップと米国のカップは同じですか?</h2><p>違います。日本の計量カップは200ml、米国のカップは約237ml(表示用に240mlを使う場合もある)です。海外レシピは<a href='volume.html'>体積の換算</a>で確認してください。</p>"
      "<h2>1合と1カップは同じですか?</h2><p>違います。1合は180ml、日本の計量カップは200mlです。お米を計量カップで量ると、1合より多くなります。<a href='rice.html'>お米の換算</a>も参照してください。</p>"
      "<h2>1mlは1gですか?</h2><p>水はほぼ1ml=1gですが、油・しょうゆ・はちみつなどは重さが違います。<a href='weight.html'>食材ごとのグラム換算</a>を使ってください。</p>"
      "<h2>大さじ1杯は何mlですか?</h2><p>日本では15mlが一般的です。小さじは5mlです。国や地域・商品により異なる場合があるため、スプーンの表示を確認してください。</p>"
      "<h2>オーブン温度の換算は必要ですか?</h2><p>海外レシピは華氏(℉)で書かれていることがあります。<a href='oven.html'>温度の換算</a>で摂氏に直せますが、機種により焼き上がりは変わります。</p>"
      "<h2>この換算は正確ですか?</h2><p>概算・目安です。正確さが必要な場合は、スケールで量る、公式の情報を確認するなどしてください。</p>")
