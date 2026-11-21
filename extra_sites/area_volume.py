"""面積・体積・図形の計算ツール集。
規約: META と build(page, write) を持つ。出力は docs/area-volume/ 配下。"""
import html
import math

META = dict(slug="area-volume", name="面積・体積・図形の計算ツール集",
            desc="長方形・三角形・円などの面積、直方体・円柱・球などの体積、平方メートルと坪・畳の換算、立方センチとリットルの換算を、ブラウザだけで計算できる無料ツール")
SITE = dict(name=META["name"], home="index.html")
NAV = [("面積", "area.html"), ("体積", "volume.html"), ("面積の単位換算", "area-units.html"), ("体積と容量", "capacity.html"),
       ("式の一覧", "formulas.html"), ("間違いやすい点", "pitfalls.html"), ("用語", "terms.html"), ("FAQ", "faq.html")]
DISC = ("本サイトの計算結果は概算・目安です。建築・工事・販売などで使う面積や体積は、測り方や定義が決まっている場合があります。"
        "重要な用途では、公式の基準や専門家に確認してください。"
        "入力した数値は、ブラウザの中だけで計算され、送信されません。")

TSUBO_M2 = 400 / 121   # 1坪 = 400/121 平方メートル(約3.3058)


def esc(s):
    return html.escape(s, quote=True)


# ---- Python側の基準実装(ブラウザ側JSと一致することを node で確認する) ----
def area_rect(a, b):
    return a * b


def area_triangle(base, h):
    return base * h / 2


def area_circle(r):
    return math.pi * r * r


def area_trapezoid(a, b, h):
    return (a + b) * h / 2


def area_parallelogram(base, h):
    return base * h


def area_ring(r_out, r_in):
    return math.pi * (r_out * r_out - r_in * r_in)


def circumference(r):
    return 2 * math.pi * r


def vol_box(a, b, c):
    return a * b * c


def vol_cylinder(r, h):
    return math.pi * r * r * h


def vol_sphere(r):
    return 4 / 3 * math.pi * r ** 3


def vol_cone(r, h):
    return math.pi * r * r * h / 3


def vol_pyramid(base_area, h):
    return base_area * h / 3


def surface_box(a, b, c):
    return 2 * (a * b + b * c + c * a)


def surface_sphere(r):
    return 4 * math.pi * r * r


def m2_to_tsubo(m2):
    return m2 / TSUBO_M2


def tsubo_to_m2(t):
    return t * TSUBO_M2


def m2_to_ha(m2):
    return m2 / 10000


def cm3_to_liter(cm3):
    return cm3 / 1000


def m3_to_liter(m3):
    return m3 * 1000


# ---- ブラウザ側JS ----
CORE_JS = """
var TSUBO=400/121;
function areaRect(a,b){return a*b}
function areaTriangle(b,h){return b*h/2}
function areaCircle(r){return Math.PI*r*r}
function areaTrapezoid(a,b,h){return (a+b)*h/2}
function areaParallelogram(b,h){return b*h}
function areaRing(ro,ri){return Math.PI*(ro*ro-ri*ri)}
function circumference(r){return 2*Math.PI*r}
function volBox(a,b,c){return a*b*c}
function volCylinder(r,h){return Math.PI*r*r*h}
function volSphere(r){return 4/3*Math.PI*Math.pow(r,3)}
function volCone(r,h){return Math.PI*r*r*h/3}
function volPyramid(s,h){return s*h/3}
function surfaceBox(a,b,c){return 2*(a*b+b*c+c*a)}
function surfaceSphere(r){return 4*Math.PI*r*r}
function m2ToTsubo(m){return m/TSUBO}
function tsuboToM2(t){return t*TSUBO}
function m2ToHa(m){return m/10000}
function cm3ToLiter(c){return c/1000}
function m3ToLiter(m){return m*1000}
function fmt(x){if(!isFinite(x))return '-';var a=Math.abs(x);if(a!==0&&(a<0.001||a>=1e9))return x.toExponential(3);return (Math.round(x*1000)/1000).toLocaleString('ja-JP',{maximumFractionDigits:3})}
function $(id){return document.getElementById(id)}
function num(id){return parseFloat($(id).value)}
if(typeof module!=='undefined')module.exports={areaRect:areaRect,areaTriangle:areaTriangle,areaCircle:areaCircle,areaTrapezoid:areaTrapezoid,areaParallelogram:areaParallelogram,areaRing:areaRing,circumference:circumference,volBox:volBox,volCylinder:volCylinder,volSphere:volSphere,volCone:volCone,volPyramid:volPyramid,surfaceBox:surfaceBox,surfaceSphere:surfaceSphere,m2ToTsubo:m2ToTsubo,tsuboToM2:tsuboToM2,m2ToHa:m2ToHa,cm3ToLiter:cm3ToLiter,m3ToLiter:m3ToLiter};
"""

AREA_JS = """
if(typeof document!=='undefined'){
var F={rect:['縦','横'],tri:['底辺','高さ'],circle:['半径'],trap:['上底','下底','高さ'],para:['底辺','高さ'],ring:['外側の半径','内側の半径']};
function draw(){var s=$('shape').value,h='',i;for(i=0;i<F[s].length;i++)h+='<label>'+F[s][i]+' <input class="f" type="number" value="'+(i+2)+'" min="0" step="any"></label><br>';$('fields').innerHTML=h;run()}
function run(){var s=$('shape').value,e=document.getElementsByClassName('f'),v=[],i;for(i=0;i<e.length;i++){v.push(parseFloat(e[i].value));if(!(v[i]>=0)){$('out').textContent='0以上の数を入力してください';return}}
var a,o='';
if(s==='rect')a=areaRect(v[0],v[1]);else if(s==='tri')a=areaTriangle(v[0],v[1]);else if(s==='circle')a=areaCircle(v[0]);else if(s==='trap')a=areaTrapezoid(v[0],v[1],v[2]);else if(s==='para')a=areaParallelogram(v[0],v[1]);else{if(v[1]>v[0]){$('out').textContent='内側の半径は外側以下にしてください';return}a=areaRing(v[0],v[1])}
o='面積は <span class="big">'+fmt(a)+'</span>(長さの単位を2乗した単位)';
if(s==='circle')o+='<br>円周は '+fmt(circumference(v[0]));
$('out').innerHTML=o}
$('shape').onchange=draw;$('btn').onclick=run;draw()}
"""

VOLUME_JS = """
if(typeof document!=='undefined'){
var F={box:['縦','横','高さ'],cyl:['底面の半径','高さ'],sphere:['半径'],cone:['底面の半径','高さ'],pyr:['底面積','高さ']};
function draw(){var s=$('shape').value,h='',i;for(i=0;i<F[s].length;i++)h+='<label>'+F[s][i]+' <input class="f" type="number" value="'+(i+2)+'" min="0" step="any"></label><br>';$('fields').innerHTML=h;run()}
function run(){var s=$('shape').value,e=document.getElementsByClassName('f'),v=[],i;for(i=0;i<e.length;i++){v.push(parseFloat(e[i].value));if(!(v[i]>=0)){$('out').textContent='0以上の数を入力してください';return}}
var a,sf=null;
if(s==='box'){a=volBox(v[0],v[1],v[2]);sf=surfaceBox(v[0],v[1],v[2])}else if(s==='cyl')a=volCylinder(v[0],v[1]);else if(s==='sphere'){a=volSphere(v[0]);sf=surfaceSphere(v[0])}else if(s==='cone')a=volCone(v[0],v[1]);else a=volPyramid(v[0],v[1]);
var o='体積は <span class="big">'+fmt(a)+'</span>(長さの単位を3乗した単位)';
if(sf!==null)o+='<br>表面積は '+fmt(sf);
$('out').innerHTML=o}
$('shape').onchange=draw;$('btn').onclick=run;draw()}
"""

UNITS_JS = """
if(typeof document!=='undefined'){
function run(){var m=num('m2');if(!(m>=0)){$('out').textContent='0以上の数を入力してください';return}
$('out').innerHTML='<table><tr><th>'+fmt(m)+' ㎡ は</th><td>'+fmt(m2ToTsubo(m))+' 坪</td></tr><tr><th>ヘクタール</th><td>'+fmt(m2ToHa(m))+' ha</td></tr><tr><th>平方センチメートル</th><td>'+fmt(m*10000)+' cm²</td></tr></table>'}
function run2(){var t=num('tsubo');if(!(t>=0)){$('out2').textContent='0以上の数を入力してください';return}
$('out2').innerHTML=fmt(t)+' 坪 は <span class="big">'+fmt(tsuboToM2(t))+' ㎡</span>'}
$('btn').onclick=run;$('btn2').onclick=run2;run();run2()}
"""

CAP_JS = """
if(typeof document!=='undefined'){
function run(){var a=num('a'),b=num('b'),c=num('c');if(!(a>=0)||!(b>=0)||!(c>=0)){$('out').textContent='0以上の数を入力してください';return}
var cm3=volBox(a,b,c);
$('out').innerHTML='<table><tr><th>体積</th><td>'+fmt(cm3)+' cm³</td></tr><tr><th>容量</th><td><span class="big">'+fmt(cm3ToLiter(cm3))+' L</span></td></tr></table>'}
function run2(){var m=num('m3');if(!(m>=0)){$('out2').textContent='0以上の数を入力してください';return}
$('out2').innerHTML=fmt(m)+' ㎥ は <span class="big">'+fmt(m3ToLiter(m))+' L</span>'}
$('btn').onclick=run;$('btn2').onclick=run2;run();run2()}
"""


def script(extra):
    return f"<script>{CORE_JS}{extra}</script>"


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)

    p("index.html", "面積・体積・図形の計算ツール集|面積・体積・坪・リットル",
      "長方形・三角形・円などの面積、直方体・円柱・球などの体積、㎡と坪の換算、cm³とリットルの換算をブラウザだけで計算できます。",
      "<h1>面積・体積・図形の計算ツール集</h1><p>図形の面積・体積の計算と、面積・容量の単位換算を、ツールと解説で整理しました。入力した数字は、ブラウザの中だけで計算され、送信されません。</p>"
      "<div class='card'><a href='area.html'><strong>面積の計算</strong></a><br>長方形・三角形・円・台形・平行四辺形・円環</div>"
      "<div class='card'><a href='volume.html'><strong>体積の計算</strong></a><br>直方体・円柱・球・円錐・角錐</div>"
      "<div class='card'><a href='area-units.html'><strong>面積の単位換算</strong></a><br>㎡・坪・ヘクタール</div>"
      "<div class='card'><a href='capacity.html'><strong>体積と容量の換算</strong></a><br>cm³・㎥とリットル</div>"
      "<h2>解説</h2><ul class='links'><li><a href='formulas.html'>面積・体積の式の一覧</a></li><li><a href='pitfalls.html'>間違いやすい点</a></li>"
      "<li><a href='terms.html'>用語集</a></li><li><a href='faq.html'>よくある質問</a></li></ul>")

    p("area.html", "面積の計算|長方形・三角形・円・台形",
      "長方形、三角形、円、台形、平行四辺形、円環の面積を計算します。円は円周も表示します。",
      "<h1>面積の計算</h1><p>図形を選び、長さを入力してください。長さの単位をそろえれば、結果はその単位の2乗です(mなら㎡)。</p>"
      "<div class='card'><label>図形 <select id='shape'><option value='rect'>長方形</option><option value='tri'>三角形</option><option value='circle'>円</option>"
      "<option value='trap'>台形</option><option value='para'>平行四辺形</option><option value='ring'>円環(ドーナツ型)</option></select></label><br>"
      "<div id='fields'></div><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<p class='note'>円周率は、プログラム内の円周率(π)を使っています。表示は小数第3位までの四捨五入です。</p>"
      "<p><a href='formulas.html'>式の一覧</a> / <a href='pitfalls.html'>間違いやすい点</a></p>" + script(AREA_JS))

    p("volume.html", "体積の計算|直方体・円柱・球・円錐・角錐",
      "直方体、円柱、球、円錐、角錐の体積を計算します。直方体と球は表面積も表示します。",
      "<h1>体積の計算</h1><p>立体を選び、長さを入力してください。長さの単位をそろえれば、結果はその単位の3乗です(mなら㎥)。</p>"
      "<div class='card'><label>立体 <select id='shape'><option value='box'>直方体</option><option value='cyl'>円柱</option><option value='sphere'>球</option>"
      "<option value='cone'>円錐</option><option value='pyr'>角錐(底面積と高さ)</option></select></label><br>"
      "<div id='fields'></div><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<p class='note'>角錐は底面積を入力します。底面の形は問いません。</p>"
      "<p><a href='formulas.html'>式の一覧</a> / <a href='capacity.html'>体積と容量の換算</a></p>" + script(VOLUME_JS))

    p("area-units.html", "面積の単位換算|㎡・坪・ヘクタール",
      "平方メートルを坪・ヘクタール・平方センチメートルに、坪を平方メートルに換算します。",
      "<h1>面積の単位換算</h1>"
      "<h2>㎡から換算</h2><div class='card'><label>面積(㎡) <input id='m2' type='number' value='50' min='0' step='any'></label><br><br><button id='btn'>換算する</button></div><div id='out' class='card'></div>"
      "<h2>坪から㎡へ</h2><div class='card'><label>面積(坪) <input id='tsubo' type='number' value='20' min='0' step='any'></label><br><br><button id='btn2'>換算する</button></div><div id='out2' class='card'></div>"
      "<h2>換算の考え方</h2><ul><li>1坪は 400/121 ㎡(約3.3058㎡)です</li><li>1ヘクタールは10,000㎡です</li>"
      "<li>畳の大きさは地域や建物の種類によって異なるため、このツールでは換算しません。畳数の表示ルールは、不動産の公式な基準で確認してください</li>"
      "<li>土地の登記簿の面積など、公的な書類に使う面積は、各書類の定義に従ってください</li></ul>" + script(UNITS_JS))

    p("capacity.html", "体積と容量の換算|cm³・㎥とリットル",
      "直方体の寸法(cm)から体積と容量(リットル)を求め、㎥をリットルに換算します。水槽や容器の目安に使えます。",
      "<h1>体積と容量の換算</h1>"
      "<h2>直方体の容量(寸法はcm)</h2><div class='card'><label>縦(cm) <input id='a' type='number' value='60' min='0' step='any'></label><br>"
      "<label>横(cm) <input id='b' type='number' value='30' min='0' step='any'></label><br>"
      "<label>高さ(cm) <input id='c' type='number' value='36' min='0' step='any'></label><br><br><button id='btn'>計算する</button></div><div id='out' class='card'></div>"
      "<h2>㎥からリットルへ</h2><div class='card'><label>体積(㎥) <input id='m3' type='number' value='1.5' min='0' step='any'></label><br><br><button id='btn2'>換算する</button></div><div id='out2' class='card'></div>"
      "<h2>考え方</h2><ul><li>1リットル = 1000cm³ = 0.001㎥</li><li>外寸ではなく、実際に入れられる内側の寸法で計算してください</li>"
      "<li>実際に入る量は、容器の形、角の丸み、満たす高さで変わります。目安としてお使いください</li></ul>" + script(CAP_JS))

    p("formulas.html", "面積・体積の式の一覧|基本図形と立体",
      "長方形、三角形、円、台形、直方体、円柱、球、円錐、角錐の面積・体積・表面積の式を一覧にしました。",
      "<h1>面積・体積の式の一覧</h1>"
      "<h2>面積</h2><table><tr><th>図形</th><th>式</th></tr><tr><td>長方形</td><td>縦 × 横</td></tr><tr><td>三角形</td><td>底辺 × 高さ ÷ 2</td></tr>"
      "<tr><td>平行四辺形</td><td>底辺 × 高さ</td></tr><tr><td>台形</td><td>(上底 + 下底) × 高さ ÷ 2</td></tr>"
      "<tr><td>円</td><td>円周率 × 半径 × 半径</td></tr><tr><td>円環</td><td>円周率 × (外側の半径² − 内側の半径²)</td></tr></table>"
      "<h2>体積</h2><table><tr><th>立体</th><th>式</th></tr><tr><td>直方体</td><td>縦 × 横 × 高さ</td></tr><tr><td>円柱</td><td>円周率 × 半径² × 高さ</td></tr>"
      "<tr><td>球</td><td>4/3 × 円周率 × 半径³</td></tr><tr><td>円錐</td><td>円周率 × 半径² × 高さ ÷ 3</td></tr><tr><td>角錐</td><td>底面積 × 高さ ÷ 3</td></tr></table>"
      "<h2>表面積と円周</h2><ul><li>直方体の表面積 = 2 ×(縦×横 + 横×高さ + 高さ×縦)</li><li>球の表面積 = 4 × 円周率 × 半径²</li><li>円周 = 2 × 円周率 × 半径</li></ul>"
      "<p>円周率は約3.14159です。概算では3.14を使うことが多いですが、桁数が多い計算では差が出ます。</p>"
      "<p><a href='area.html'>面積の計算</a> / <a href='volume.html'>体積の計算</a></p>")

    p("pitfalls.html", "面積・体積計算で間違いやすい点|半径と直径・単位の2乗3乗",
      "半径と直径の取り違え、単位換算での2乗・3乗の見落とし、三角形の高さの取り方など、よくある間違いをまとめました。",
      "<h1>面積・体積計算で間違いやすい点</h1>"
      "<h2>1. 半径と直径の取り違え</h2><p>円や球の式に入れるのは半径です。直径が与えられたら2で割ります。半径を直径にしてしまうと、面積は4倍、球の体積は8倍になります。</p>"
      "<h2>2. 面積・体積の単位換算</h2><p>1m = 100cm でも、1㎡ = 10,000cm²、1㎥ = 1,000,000cm³ です。長さの換算率を2乗・3乗します。</p>"
      "<h2>3. 三角形の「高さ」</h2><p>高さは底辺に垂直な長さです。斜めの辺の長さではありません。</p>"
      "<h2>4. 単位がそろっていない</h2><p>縦をm、横をcmで入力すると、結果の桁が合いません。先にそろえます。</p>"
      "<h2>5. 外寸と内寸</h2><p>容器の容量は、壁の厚みを除いた内側の寸法で計算します。</p>"
      "<h2>6. 円周率の丸め</h2><p>3.14と3.14159では、半径が大きいほど差が広がります。用途に合わせて桁数を選びます。</p>")

    terms = [("面積", "平面の広がりの大きさ。単位は長さの2乗(㎡など)"), ("体積", "立体が占める空間の大きさ。単位は長さの3乗(㎥など)"),
             ("容量", "容器に入る量。リットルなどで表す"), ("底面積", "立体の底の面の面積"), ("表面積", "立体の外側すべての面の面積の合計"),
             ("円周率(π)", "円周と直径の比。約3.14159"), ("坪", "日本の面積の単位。1坪は約3.3058㎡"), ("ヘクタール(ha)", "10,000㎡")]
    trs = "".join(f"<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>" for a, b in terms)
    p("terms.html", "面積・体積の用語集|面積・体積・容量・坪",
      "面積、体積、容量、底面積、表面積、円周率、坪、ヘクタールなどの用語を短く説明します。",
      f"<h1>面積・体積の用語集</h1><table><tr><th>用語</th><th>意味</th></tr>{trs}</table><p><a href='formulas.html'>式の一覧</a></p>")

    p("faq.html", "面積・体積のよくある質問",
      "50㎡は何坪か、1リットルは何cm³か、円の面積は直径からどう求めるかなど、よくある疑問に答えます。",
      "<h1>よくある質問</h1>"
      "<h2>50㎡は何坪ですか?</h2><p>50 ÷ 3.3058 で約15.1坪です。<a href='area-units.html'>面積の単位換算</a>で確認できます。</p>"
      "<h2>1リットルは何cm³ですか?</h2><p>1000cm³です。<a href='capacity.html'>体積と容量の換算</a>で計算できます。</p>"
      "<h2>直径から円の面積を求めるには?</h2><p>直径を2で割って半径にし、円周率 × 半径² で求めます。</p>"
      "<h2>円錐や角錐の体積はなぜ3で割るのですか?</h2><p>同じ底面と高さの円柱・角柱の体積の3分の1になる、という確立した関係があるためです。</p>"
      "<h2>入力した数字は送信されますか?</h2><p>いいえ。計算はブラウザの中だけで行われます。</p>")
