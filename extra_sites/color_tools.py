"""色コード変換(HEX・RGB・HSL)と配色の基本。規約: META と build(page, write) を持つ。出力は docs/color-tools/ 配下。"""
import html
import math

META = dict(slug="color-tools", name="色コード変換ツール集", desc="HEX・RGB・HSLの色コード変換、文字色のコントラスト比、色の混ぜ合わせ、配色パターンをブラウザだけで試せる無料ツール")
SITE = dict(name=META["name"], home="index.html")
NAV = [("変換", "converter.html"), ("コントラスト", "contrast.html"), ("混色", "mix.html"), ("配色", "palette.html"), ("色の表し方", "color-models.html"), ("基本色", "basic-colors.html")]
DISC = ("本サイトの結果は概算・目安です(画面や環境によって実際の見え方は変わります)。デザインの最終判断や、アクセシビリティの基準への適合確認は、公式の基準で確認してください。"
        "入力した値は、ブラウザの中だけで計算され、送信されません。")


def esc(s):
    return html.escape(s, quote=True)


# ---- Python側の基準実装(ブラウザ側JSと一致することを node で確認する) ----
def rnd(x):
    return math.floor(x + 0.5)


def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return [int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)]


def rgb_to_hex(r, g, b):
    return "#" + "".join("%02x" % v for v in (r, g, b))


def rgb_to_hsl(r, g, b):
    r, g, b = r / 255, g / 255, b / 255
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    d = mx - mn
    if d == 0:
        return [0, 0, rnd(l * 100)]
    s = d / (1 - abs(2 * l - 1))
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return [rnd(h * 60) % 360, rnd(s * 100), rnd(l * 100)]


def hsl_to_rgb(h, s, l):
    s, l = s / 100, l / 100
    c = (1 - abs(2 * l - 1)) * s
    hp = (h % 360) / 60
    x = c * (1 - abs(hp % 2 - 1))
    k = int(math.floor(hp))
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][k]
    m = l - c / 2
    return [rnd((r + m) * 255), rnd((g + m) * 255), rnd((b + m) * 255)]


def lin(v):
    v = v / 255
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def luminance(r, g, b):
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(c1, c2):
    a, b = luminance(*c1), luminance(*c2)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def mix(c1, c2, t):
    return [rnd(c1[i] * (1 - t) + c2[i] * t) for i in range(3)]


def palette(h, s, l):
    """基準色のHSLから、補色・類似色・3色配色の色相を返す(色相のみ回転)"""
    return {"comp": [(h + 180) % 360], "analog": [(h + 330) % 360, (h + 30) % 360], "triad": [(h + 120) % 360, (h + 240) % 360]}


# ---- ブラウザ側JS ----
CORE_JS = """
function rnd(x){return Math.floor(x+0.5)}
function hexToRgb(h){h=h.trim().replace(/^#/,'');if(h.length===3)h=h.split('').map(function(c){return c+c}).join('');return [parseInt(h.substr(0,2),16),parseInt(h.substr(2,2),16),parseInt(h.substr(4,2),16)]}
function rgbToHex(r,g,b){return '#'+[r,g,b].map(function(v){var s=v.toString(16);return s.length<2?'0'+s:s}).join('')}
function rgbToHsl(r,g,b){r/=255;g/=255;b/=255;var mx=Math.max(r,g,b),mn=Math.min(r,g,b),l=(mx+mn)/2,d=mx-mn;if(d===0)return [0,0,rnd(l*100)];
var s=d/(1-Math.abs(2*l-1)),h;if(mx===r){h=(g-b)/d%6;if(h<0)h+=6}else if(mx===g)h=(b-r)/d+2;else h=(r-g)/d+4;return [rnd(h*60)%360,rnd(s*100),rnd(l*100)]}
function hslToRgb(h,s,l){s/=100;l/=100;var c=(1-Math.abs(2*l-1))*s,hp=(((h%360)+360)%360)/60,x=c*(1-Math.abs(hp%2-1)),k=Math.floor(hp);
var t=[[c,x,0],[x,c,0],[0,c,x],[0,x,c],[x,0,c],[c,0,x]][k],m=l-c/2;return [rnd((t[0]+m)*255),rnd((t[1]+m)*255),rnd((t[2]+m)*255)]}
function lin(v){v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)}
function luminance(r,g,b){return 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b)}
function contrast(a,b){var x=luminance(a[0],a[1],a[2]),y=luminance(b[0],b[1],b[2]),hi=Math.max(x,y),lo=Math.min(x,y);return (hi+0.05)/(lo+0.05)}
function mix(a,b,t){return [0,1,2].map(function(i){return rnd(a[i]*(1-t)+b[i]*t)})}
function palette(h){return {comp:[(h+180)%360],analog:[(h+330)%360,(h+30)%360],triad:[(h+120)%360,(h+240)%360]}}
function $(id){return document.getElementById(id)}
function validHex(h){return /^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(h.trim())}
function sw(hex){return '<span class="sw" style="background:'+hex+'"></span>'}
"""

CONV_JS = """
function show(rgb,from){var hex=rgbToHex(rgb[0],rgb[1],rgb[2]),hsl=rgbToHsl(rgb[0],rgb[1],rgb[2]);
if(from!=='hex')$('hex').value=hex;if(from!=='rgb')$('rgb').value=rgb.join(', ');if(from!=='hsl')$('hsl').value=hsl[0]+', '+hsl[1]+'%, '+hsl[2]+'%';
$('out').innerHTML=sw(hex)+' <strong>'+hex+'</strong><br>rgb('+rgb.join(', ')+')<br>hsl('+hsl[0]+', '+hsl[1]+'%, '+hsl[2]+'%)'}
function err(m){$('out').textContent=m}
$('hex').oninput=function(){if(!validHex(this.value))return err('HEXは3桁か6桁で入力してください(例: #1a2b3c)');show(hexToRgb(this.value),'hex')};
$('rgb').oninput=function(){var v=this.value.split(/[ ,]+/).filter(Boolean).map(Number);if(v.length!==3||v.some(function(x){return !(x>=0&&x<=255)||x%1!==0}))return err('RGBは0〜255の整数3つで入力してください');show(v,'rgb')};
$('hsl').oninput=function(){var v=this.value.replace(/%/g,'').split(/[ ,]+/).filter(Boolean).map(Number);if(v.length!==3||v.some(isNaN)||v[1]<0||v[1]>100||v[2]<0||v[2]>100)return err('HSLは色相(0〜360)、彩度・明度(0〜100)で入力してください');show(hslToRgb(v[0],v[1],v[2]),'hsl')};
$('pick').oninput=function(){show(hexToRgb(this.value),'pick');$('hex').value=this.value};
show(hexToRgb('#3366cc'),'');
"""

CONTRAST_JS = """
function run(){var a=$('fg').value,b=$('bg').value;if(!validHex(a)||!validHex(b)){$('out').textContent='HEXは3桁か6桁で入力してください';return}
var fa=hexToRgb(a),fb=hexToRgb(b),r=contrast(fa,fb),rr=Math.floor(r*100)/100;
function ok(x){return x?'<strong>基準を満たす</strong>':'満たさない'}
$('out').innerHTML='<div style="padding:16px;background:'+rgbToHex(fb[0],fb[1],fb[2])+';color:'+rgbToHex(fa[0],fa[1],fa[2])+'">サンプル文字 Sample Text</div><p class="big">'+rr.toFixed(2)+' : 1</p><table><tr><th>目安</th><th>結果</th></tr>'+
'<tr><td>通常の文字(4.5:1以上)</td><td>'+ok(r>=4.5)+'</td></tr><tr><td>大きい文字(3:1以上)</td><td>'+ok(r>=3)+'</td></tr></table>'}
['fg','bg'].forEach(function(i){$(i).oninput=run});run();
"""

MIX_JS = """
function run(){var a=$('c1').value,b=$('c2').value,n=parseInt($('n').value,10);if(!validHex(a)||!validHex(b)||!(n>=2&&n<=11)){$('out').textContent='HEXは3桁か6桁、段階数は2〜11で入力してください';return}
var A=hexToRgb(a),B=hexToRgb(b),h='<table><tr><th>色</th><th>割合</th><th>HEX</th></tr>';
for(var i=0;i<n;i++){var t=i/(n-1),m=mix(A,B,t),hx=rgbToHex(m[0],m[1],m[2]);h+='<tr><td>'+sw(hx)+'</td><td>'+Math.round(t*100)+'%</td><td>'+hx+'</td></tr>'}
$('out').innerHTML=h+'</table>'}
['c1','c2','n'].forEach(function(i){$(i).oninput=run});run();
"""

PAL_JS = """
function run(){var a=$('base').value;if(!validHex(a)){$('out').textContent='HEXは3桁か6桁で入力してください';return}
var rgb=hexToRgb(a),hsl=rgbToHsl(rgb[0],rgb[1],rgb[2]),p=palette(hsl[0]),h='<table><tr><th>配色</th><th>色</th></tr>',names={comp:'補色',analog:'類似色',triad:'3色配色(トライアド)'};
function cell(hh){var c=hslToRgb(hh,hsl[1],hsl[2]),hx=rgbToHex(c[0],c[1],c[2]);return sw(hx)+' '+hx+'(色相'+hh+')'}
h+='<tr><td>基準色</td><td>'+sw(rgbToHex(rgb[0],rgb[1],rgb[2]))+' '+rgbToHex(rgb[0],rgb[1],rgb[2])+'(色相'+hsl[0]+')</td></tr>';
['comp','analog','triad'].forEach(function(k){h+='<tr><td>'+names[k]+'</td><td>'+p[k].map(cell).join('<br>')+'</td></tr>'});
$('out').innerHTML=h+'</table>'}
$('base').oninput=run;run();
"""

STYLE = "<style>.sw{display:inline-block;width:2em;height:1.2em;border:1px solid #888;vertical-align:middle}</style>"


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)

    p("index.html", "色コード変換ツール集|HEX・RGB・HSLと配色の基本",
      "HEX・RGB・HSLの色コード変換、文字色のコントラスト比、色の混ぜ合わせ、配色パターンを試せる無料ツール集と、色の基礎解説です。",
      "<h1>色コード変換ツール集</h1><p>入力した値は、ブラウザの中だけで計算されます。サーバーには送信されません。</p>"
      "<div class='card'><a href='converter.html'><strong>色コード変換</strong></a><br>HEX・RGB・HSLを相互に変換</div>"
      "<div class='card'><a href='contrast.html'><strong>コントラスト比チェッカー</strong></a><br>文字色と背景色の読みやすさの目安</div>"
      "<div class='card'><a href='mix.html'><strong>2色の混色・グラデーション</strong></a><br>2色の間の色を段階的に求める</div>"
      "<div class='card'><a href='palette.html'><strong>配色パターン</strong></a><br>補色・類似色・3色配色を求める</div>"
      "<h2>解説ページ</h2><ul class='links'><li><a href='color-models.html'>RGB・HEX・HSLの考え方</a></li><li><a href='hex-basics.html'>16進数のカラーコードの読み方</a></li>"
      "<li><a href='color-harmony.html'>配色の基本(色相環と配色パターン)</a></li><li><a href='contrast-guide.html'>文字の読みやすさとコントラスト</a></li>"
      "<li><a href='basic-colors.html'>基本16色の名前とコード</a></li></ul>")

    p("converter.html", "色コード変換|HEX・RGB・HSL",
      "HEX、RGB、HSLの色コードを相互に変換します。カラーピッカーで色を選ぶこともできます。",
      STYLE + "<h1>色コード変換(HEX・RGB・HSL)</h1><div class='card'>"
      "<label>HEX <input id='hex' value='#3366cc'></label><br><label>RGB(0〜255) <input id='rgb' value='51, 102, 204'></label><br>"
      "<label>HSL(色相, 彩度%, 明度%) <input id='hsl' value='220, 60%, 50%'></label><br><label>色を選ぶ <input id='pick' type='color' value='#3366cc'></label></div>"
      "<div id='out' class='card'></div><p class='note'>HSLは整数に丸めて表示するため、変換を往復すると1程度ずれることがあります。考え方は<a href='color-models.html'>RGB・HEX・HSLの考え方</a>を参照してください。</p>"
      f"<script>{CORE_JS}{CONV_JS}</script>")

    p("contrast.html", "コントラスト比チェッカー|文字色と背景色",
      "文字色と背景色のコントラスト比を計算し、読みやすさの目安(4.5:1、3:1)を満たすか確認します。",
      STYLE + "<h1>コントラスト比チェッカー</h1><div class='card'><label>文字色 <input id='fg' value='#333333'></label><br><label>背景色 <input id='bg' value='#ffffff'></label></div>"
      "<div id='out' class='card'></div><p class='note'>この数値は目安です。基準の詳細や適合の確認は、公式の基準で確認してください。読み方は<a href='contrast-guide.html'>文字の読みやすさとコントラスト</a>を参照してください。</p>"
      f"<script>{CORE_JS}{CONTRAST_JS}</script>")

    p("mix.html", "2色の混色・グラデーション|中間色を求める",
      "2つの色の間の色を、指定した段階数で計算します。グラデーションの途中の色を決めるときの目安になります。",
      STYLE + "<h1>2色の混色・グラデーション</h1><div class='card'><label>色1 <input id='c1' value='#ff0000'></label><br><label>色2 <input id='c2' value='#0000ff'></label><br>"
      "<label>段階数(2〜11) <input id='n' type='number' value='5' min='2' max='11'></label></div><div id='out' class='card'></div>"
      "<p class='note'>RGBの各値を割合で直線的に混ぜています。絵の具の混色とは結果が異なります。</p>"
      f"<script>{CORE_JS}{MIX_JS}</script>")

    p("palette.html", "配色パターン|補色・類似色・トライアド",
      "基準色から、補色、類似色、3色配色の色を色相の回転で求めます。",
      STYLE + "<h1>配色パターン</h1><div class='card'><label>基準色(HEX) <input id='base' value='#3366cc'></label></div><div id='out' class='card'></div>"
      "<p class='note'>色相だけを回転し、彩度と明度は基準色のままにしています。出てきた色の組み合わせが見やすいとは限りません。考え方は<a href='color-harmony.html'>配色の基本</a>を参照してください。</p>"
      f"<script>{CORE_JS}{PAL_JS}</script>")

    p("color-models.html", "RGB・HEX・HSLの考え方",
      "画面の色を表すRGB、HEX、HSLの違いと、それぞれの値の意味を解説します。",
      "<h1>RGB・HEX・HSLの考え方</h1>"
      "<h2>RGB</h2><p>赤(Red)・緑(Green)・青(Blue)の光の強さを、それぞれ0〜255の数で表す方法です。3つとも0なら黒、3つとも255なら白になります。光を足して色を作るため、「加法混色」と呼ばれます。</p>"
      "<h2>HEX(16進数表記)</h2><p>RGBの3つの値を16進数の2桁ずつにして並べ、先頭に#を付けた書き方です。Webの制作でよく使われます。詳しくは<a href='hex-basics.html'>16進数のカラーコードの読み方</a>を参照してください。</p>"
      "<h2>HSL</h2><p>色相(Hue)、彩度(Saturation)、明度(Lightness)で表す方法です。</p>"
      "<table><tr><th>要素</th><th>範囲</th><th>意味</th></tr><tr><td>色相</td><td>0〜360度</td><td>色の種類。0度が赤、120度が緑、240度が青の付近</td></tr>"
      "<tr><td>彩度</td><td>0〜100%</td><td>色の鮮やかさ。0%でグレー</td></tr><tr><td>明度</td><td>0〜100%</td><td>明るさ。0%で黒、100%で白</td></tr></table>"
      "<p>HSLは「少し明るくする」「少し落ち着かせる」といった調整が数字で考えやすいのが利点です。</p>"
      "<p class='note'>実際の見え方は、ディスプレイの設定や周囲の明るさで変わります。印刷用のCMYKとは別の仕組みです。</p>"
      "<p><a href='converter.html'>色コード変換ツール</a>で試せます。</p>")

    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in [
        ("#000000", "0, 0, 0", "黒"), ("#ffffff", "255, 255, 255", "白"), ("#ff0000", "255, 0, 0", "赤"), ("#00ff00", "0, 255, 0", "緑(最も明るい)"),
        ("#0000ff", "0, 0, 255", "青"), ("#808080", "128, 128, 128", "中間のグレー"), ("#ffff00", "255, 255, 0", "黄(赤+緑)")])
    p("hex-basics.html", "16進数のカラーコードの読み方",
      "#ff8800のようなカラーコードの読み方と、3桁表記の意味、16進数の基本を解説します。",
      "<h1>16進数のカラーコードの読み方</h1><p>カラーコード「#rrggbb」は、赤・緑・青の強さを16進数2桁ずつで並べたものです。16進数は0〜9とa〜f(10〜15)を使い、2桁で0〜255を表せます。</p>"
      "<h2>読み方の例</h2><p>「#ff8800」は、赤=ff(255)、緑=88(136)、青=00(0)です。16進数の2桁は「上の桁×16+下の桁」で数に直せます(88なら8×16+8=136)。</p>"
      "<table><tr><th>HEX</th><th>RGB</th><th>色</th></tr>" + rows + "</table>"
      "<h2>3桁表記</h2><p>各色の2桁が同じ数字の組(例: #ff8800)は、3桁に短縮して#f80と書けます。たとえば#fffは#ffffff(白)と同じです。</p>"
      "<h2>大文字と小文字</h2><p>a〜fの大文字と小文字は同じ意味です。</p>"
      "<p><a href='converter.html'>色コード変換ツール</a> / <a href='color-models.html'>RGB・HEX・HSLの考え方</a></p>")

    p("color-harmony.html", "配色の基本|色相環と配色パターン",
      "色相環の考え方と、補色・類似色・トライアドなどの配色パターン、配色の割合の目安を解説します。",
      "<h1>配色の基本(色相環と配色パターン)</h1><p>色相環は、色の種類(色相)を円に並べたものです。HSLの色相の角度(0〜360度)は、この円の位置にあたります。</p>"
      "<table><tr><th>パターン</th><th>色相の関係</th><th>印象の傾向</th></tr>"
      "<tr><td>補色</td><td>正反対(180度離れる)</td><td>はっきりと目立つ</td></tr><tr><td>類似色</td><td>隣り合う(30度ほど)</td><td>まとまりがあり穏やか</td></tr>"
      "<tr><td>トライアド</td><td>120度ずつ(3色)</td><td>にぎやかでバランスが取りやすい</td></tr></table>"
      "<h2>よく言われる割合の目安</h2><ul><li>ベースの色: 全体の大半(背景など)</li><li>メインの色: 全体の中くらい</li><li>アクセントの色: ごく一部(目立たせたい部分)</li></ul>"
      "<p>厳密な決まりではなく、考え方のひとつです。色の数を増やしすぎないほうが整って見えやすいとされています。</p>"
      "<p class='note'>印象は文化や個人、使う場面で異なります。参考のひとつとして使ってください。</p>"
      "<p><a href='palette.html'>配色パターンのツール</a> / <a href='contrast-guide.html'>文字の読みやすさとコントラスト</a></p>")

    p("contrast-guide.html", "文字の読みやすさとコントラスト",
      "文字色と背景色のコントラスト比とは何か、Webアクセシビリティの指針で示される目安と、見やすい配色のコツを解説します。",
      "<h1>文字の読みやすさとコントラスト</h1><p>コントラスト比は、文字色と背景色の明るさの差を1:1〜21:1の数で表したものです。白と黒の組み合わせが最大の21:1、同じ色どうしは1:1です。</p>"
      "<h2>よく知られる目安</h2><p>Webアクセシビリティの指針(WCAG)では、通常の文字で4.5:1以上、大きい文字で3:1以上が基本の目安として示されています。大きい文字の定義など細かい条件は、公式の文書で確認してください。</p>"
      "<h2>見やすくするコツ</h2><ul><li>明るさの差をしっかり付ける(色相の違いだけに頼らない)</li><li>薄いグレーの文字を、白い背景に使いすぎない</li>"
      "<li>色だけで意味を伝えない(例: 赤と緑だけで状態を区別しない。文字や形も併用する)</li><li>画像の上に文字を重ねるときは、背景を暗くするなどして差を確保する</li></ul>"
      "<h2>計算の概要</h2><p>各色のR・G・Bを、画面の明るさに近い値(相対輝度)に直し、明るい側と暗い側の比を、(明るい側+0.05)÷(暗い側+0.05)で求めます。</p>"
      "<p class='note'>数値を満たしていても、読みやすさは文字の太さや大きさ、画面の環境にも左右されます。</p>"
      "<p><a href='contrast.html'>コントラスト比チェッカー</a></p>")

    rows = "".join(f"<tr><td><span class='sw' style='background:{c}'></span></td><td>{n}</td><td>{c}</td></tr>" for n, c in [
        ("black(黒)", "#000000"), ("silver(銀)", "#c0c0c0"), ("gray(灰)", "#808080"), ("white(白)", "#ffffff"), ("maroon(栗色)", "#800000"), ("red(赤)", "#ff0000"),
        ("purple(紫)", "#800080"), ("fuchsia(赤紫)", "#ff00ff"), ("green(緑)", "#008000"), ("lime(黄緑)", "#00ff00"), ("olive(オリーブ)", "#808000"), ("yellow(黄)", "#ffff00"),
        ("navy(濃紺)", "#000080"), ("blue(青)", "#0000ff"), ("teal(青緑)", "#008080"), ("aqua(水色)", "#00ffff")])
    p("basic-colors.html", "基本16色の名前とコード",
      "HTMLとCSSで古くから使える基本16色の名前と、HEXコードの一覧です。",
      STYLE + "<h1>基本16色の名前とコード</h1><p>HTMLやCSSでは、色を名前で指定できます。ここでは古くから使える基本の16色を示します。日本語の名前はこのサイトでの便宜的な呼び方です。</p>"
      "<table><tr><th>見本</th><th>名前</th><th>HEX</th></tr>" + rows + "</table>"
      "<p class='note'>CSSにはこのほかにも多数の色名があります。一覧は公式の仕様で確認してください。</p>"
      "<p><a href='converter.html'>色コード変換ツール</a>でRGBやHSLに変換できます。</p>")
