"""進数変換ツール(2進・8進・10進・16進)と解説。規約: META と build(page, write) を持つ。出力は docs/radix-tools/ 配下。"""
import html

META = dict(slug="radix-tools", name="進数変換ツール集", desc="2進・8進・10進・16進の変換、2の補数、ビット演算をブラウザだけで試せる無料ツールと、進数の基本解説")
SITE = dict(name=META["name"], home="index.html")
NAV = [("変換", "converter.html"), ("2の補数", "twos-complement.html"), ("ビット演算", "bitops.html"), ("2進数", "binary-basics.html"),
       ("16進数", "hex-basics.html"), ("8進数", "octal.html"), ("手計算", "manual-conversion.html"), ("早見表", "table.html"), ("用途", "uses.html"), ("用語", "glossary.html")]
DISC = ("本サイトの結果は目安です。試験・業務・プログラムで使う前には、教科書・言語の公式ドキュメントなど公式の情報で確認してください。"
        "入力した値は、ブラウザの中だけで計算され、送信されません。")


def esc(s):
    return html.escape(s, quote=True)


# ---- Python側の基準実装(ブラウザ側JSと一致することを node で確認する) ----
def parse_big(s, b):
    s = "".join(ch for ch in s.strip().lower() if not ch.isspace() and ch != "_")
    neg = False
    if s.startswith("-"):
        neg, s = True, s[1:]
    if not s:
        return None
    v = 0
    for ch in s:
        if ch.isdigit():
            d = int(ch)
        elif "a" <= ch <= "z":
            d = ord(ch) - 87
        else:
            return None
        if d >= b:
            return None
        v = v * b + d
    return -v if neg else v


def to_base(v, b):
    neg = v < 0
    v = abs(v)
    if v == 0:
        return "0"
    digs = "0123456789abcdefghijklmnopqrstuvwxyz"
    s = ""
    while v > 0:
        s = digs[v % b] + s
        v //= b
    return "-" + s if neg else s


def twos(v, w):
    lo, hi = -(1 << (w - 1)), (1 << (w - 1)) - 1
    if v < lo or v > hi:
        return None
    u = v + (1 << w) if v < 0 else v
    return to_base(u, 2).rjust(w, "0")


def untwos(s, w):
    if not s or len(s) > w or any(c not in "01" for c in s):
        return None
    u = int(s, 2)
    return u - (1 << w) if u >= (1 << (w - 1)) else u


def bitop(a, b, op, w):
    m = (1 << w) - 1
    a &= m
    b &= m
    if op == "and":
        r = a & b
    elif op == "or":
        r = a | b
    elif op == "xor":
        r = a ^ b
    elif op == "not":
        r = ~a
    elif op == "shl":
        r = a << b
    else:
        r = a >> b
    return r & m


LIB = """
function parseBig(s,b){s=s.trim().toLowerCase().replace(/[\\s_]/g,'');var neg=false;if(s.charAt(0)==='-'){neg=true;s=s.slice(1)}if(!s.length)return null;var v=0n,B=BigInt(b);for(var i=0;i<s.length;i++){var d=parseInt(s.charAt(i),36);if(isNaN(d)||d>=b)return null;v=v*B+BigInt(d)}return neg?-v:v}
function toBase(v,b){var neg=v<0n;if(neg)v=-v;if(v===0n)return '0';var B=BigInt(b),s='';while(v>0n){s=Number(v%B).toString(36)+s;v=v/B}return neg?'-'+s:s}
function twos(v,w){var lo=-(1n<<BigInt(w-1)),hi=(1n<<BigInt(w-1))-1n;if(v<lo||v>hi)return null;var u=v<0n?v+(1n<<BigInt(w)):v;return toBase(u,2).padStart(w,'0')}
function untwos(s,w){if(!s.length||s.length>w||/[^01]/.test(s))return null;var u=parseBig(s,2);if(u>=(1n<<BigInt(w-1)))u-=(1n<<BigInt(w));return u}
function bitop(a,b,op,w){var m=(1n<<BigInt(w))-1n;a=a&m;b=b&m;var r;if(op==='and')r=a&b;else if(op==='or')r=a|b;else if(op==='xor')r=a^b;else if(op==='not')r=~a;else if(op==='shl')r=a<<b;else r=a>>b;return r&m}
function $(id){return document.getElementById(id)}
"""

CONV_JS = """
function run(){var b=parseInt($('from').value,10),v=parseBig($('n').value,b);
if(v===null){$('out').textContent='入力を確認してください(使える文字は、選んだ進数の数字だけです)';return}
var c=parseInt($('cb').value,10);
$('out').innerHTML='<table><tr><th>2進数</th><td>'+toBase(v,2)+'</td></tr><tr><th>8進数</th><td>'+toBase(v,8)+'</td></tr><tr><th>10進数</th><td>'+toBase(v,10)+'</td></tr><tr><th>16進数</th><td>'+toBase(v,16)+'</td></tr><tr><th>'+c+'進数</th><td>'+toBase(v,c)+'</td></tr></table>'}
$('btn').onclick=run;run();
"""

TWOS_JS = """
function run(){var w=parseInt($('w').value,10),v=parseBig($('d').value,10),o='';
if(v===null){o='<p>10進数の入力を確認してください</p>'}else{var t=twos(v,w);o=t===null?'<p>'+w+'ビットで表せる範囲を超えています</p>':'<p class="big">'+t+'</p><p>16進数では '+toBase(BigInt('0b'+t),16).toUpperCase()+'</p>'}
var s=$('b').value.trim().replace(/\\s/g,''),u=untwos(s,w);
o+=(u===null)?'<p>2進数の入力を確認してください(0と1だけ、'+w+'桁以内)</p>':'<p>2進数 '+s+' を '+w+'ビットの符号付き整数とみなすと <strong>'+u.toString()+'</strong></p>';
$('out').innerHTML=o}
$('btn').onclick=run;run();
"""

BIT_JS = """
function run(){var w=parseInt($('w').value,10),op=$('op').value,a=parseBig($('a').value,10),b=parseBig($('b').value,10);
if(a===null||(op!=='not'&&b===null)||a<0n||(b!==null&&b<0n)){$('out').textContent='0以上の整数を入力してください';return}
if(b===null)b=0n;var r=bitop(a,b,op,w);
$('out').innerHTML='<table><tr><th>結果(10進)</th><td>'+r.toString()+'</td></tr><tr><th>結果(2進・'+w+'桁)</th><td>'+toBase(r,2).padStart(w,'0')+'</td></tr><tr><th>結果(16進)</th><td>'+toBase(r,16).toUpperCase()+'</td></tr></table>'}
$('btn').onclick=run;run();
"""


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)
    bases = "".join(f"<option value='{b}'{' selected' if b == 36 else ''}>{b}進数</option>" for b in (2, 3, 4, 5, 6, 7, 8, 9, 12, 16, 20, 32, 36))
    from_opts = "".join(f"<option value='{b}'{' selected' if b == 10 else ''}>{n}</option>" for b, n in ((2, "2進数"), (8, "8進数"), (10, "10進数"), (16, "16進数"), (36, "36進数")))
    width_opts = "".join(f"<option value='{w}'{' selected' if w == 8 else ''}>{w}ビット</option>" for w in (4, 8, 16, 32))

    p("index.html", "進数変換ツール集|2進・8進・10進・16進の変換と解説",
      "2進・8進・10進・16進の変換、2の補数、ビット演算をブラウザだけで試せる無料ツールと、進数の基本をまとめた解説サイトです。",
      "<h1>進数変換ツール集</h1><p>入力した数字は、ブラウザの中だけで計算されます。サーバーには送信されません。</p>"
      "<h2>ツール</h2>"
      "<div class='card'><a href='converter.html'><strong>進数変換</strong></a><br>2進・8進・10進・16進と、好きな進数(2〜36)に一度に変換</div>"
      "<div class='card'><a href='twos-complement.html'><strong>2の補数(負の数のビット表現)</strong></a><br>4〜32ビットで、負の数を2進数に、2進数を符号付き整数に</div>"
      "<div class='card'><a href='bitops.html'><strong>ビット演算</strong></a><br>AND・OR・XOR・NOT・シフトの結果を2進数で確認</div>"
      "<h2>解説</h2><ul class='links'><li><a href='binary-basics.html'>2進数の基本</a></li><li><a href='hex-basics.html'>16進数の基本</a></li>"
      "<li><a href='octal.html'>8進数の基本</a></li><li><a href='manual-conversion.html'>進数変換の手計算のやり方</a></li>"
      "<li><a href='table.html'>0〜31の早見表</a></li><li><a href='uses.html'>進数が使われる場面</a></li><li><a href='glossary.html'>用語集</a></li></ul>")

    p("converter.html", "進数変換ツール|2進・8進・10進・16進を一度に変換",
      "整数を2進・8進・10進・16進と、2〜36進の好きな進数に変換します。大きな数にも対応。",
      "<h1>進数変換ツール</h1><p>整数を入力して、入力の進数を選びます。負の数は先頭に - を付けてください。</p>"
      "<div class='card'><label>数値 <input id='n' type='text' value='255'></label><br>"
      f"<label>入力の進数 <select id='from'>{from_opts}</select></label><br>"
      f"<label>もう1つ表示する進数 <select id='cb'>{bases}</select></label><br><br><button id='btn'>変換する</button></div>"
      "<div id='out' class='card'></div>"
      "<h2>使い方のヒント</h2><ul><li>16進数の英字(a〜f)は大文字でも小文字でも入力できます</li><li>桁が多いときは空白や _ で区切って入力できます</li>"
      "<li>小数や分数は扱いません。整数のみです</li><li>36進数は、0〜9とa〜zの36種類の文字を使います</li></ul>"
      "<p><a href='manual-conversion.html'>手計算のやり方</a>も参照してください。</p>"
      f"<script>{LIB}{CONV_JS}</script>")

    p("twos-complement.html", "2の補数の計算|負の数を2進数で表す",
      "負の数をnビットの2進数(2の補数)で表したり、2進数を符号付き整数に戻したりします。4・8・16・32ビット対応。",
      "<h1>2の補数の計算</h1><p>コンピュータで負の数を扱うときの代表的な表し方である「2の補数」を計算します。</p>"
      "<div class='card'>"
      f"<label>ビット数 <select id='w'>{width_opts}</select></label><br>"
      "<label>10進数 <input id='d' type='text' value='-5'></label><br>"
      "<label>2進数 <input id='b' type='text' value='11111011'></label><br><br><button id='btn'>計算する</button></div>"
      "<div id='out' class='card'></div>"
      "<h2>2の補数とは</h2><p>nビットで負の数を表すとき、元の数を2のn乗に足した値(または、ビットを反転して1を足した値)を使う方法です。"
      "最上位ビットが1なら負の数として扱います。nビットで表せる範囲は、−2のn−1乗 から 2のn−1乗−1 までです(8ビットなら −128〜127)。</p>"
      "<h2>求め方の例(8ビットで −5)</h2><ol><li>5を2進数にする: 00000101</li><li>全ビットを反転する: 11111010</li><li>1を足す: 11111011</li></ol>"
      "<p>言語や機器によって整数の扱いは異なるため、実際のプログラムでは公式ドキュメントで確認してください。</p>"
      f"<script>{LIB}{TWOS_JS}</script>")

    p("bitops.html", "ビット演算ツール|AND・OR・XOR・NOT・シフト",
      "2つの整数に対するAND・OR・XOR・NOT・左右シフトの結果を、2進数と16進数で表示します。",
      "<h1>ビット演算ツール</h1><p>0以上の整数を入力して、演算とビット数を選びます。結果はビット数の範囲に収めて表示します。</p>"
      "<div class='card'>"
      "<label>演算 <select id='op'><option value='and'>AND(両方1なら1)</option><option value='or'>OR(どちらか1なら1)</option><option value='xor'>XOR(異なれば1)</option>"
      "<option value='not'>NOT(ビット反転・左の数のみ)</option><option value='shl'>左シフト(右の数だけ)</option><option value='shr'>右シフト(右の数だけ)</option></select></label><br>"
      f"<label>ビット数 <select id='w'>{width_opts}</select></label><br>"
      "<label>左の数(10進) <input id='a' type='text' value='12'></label><br>"
      "<label>右の数(10進) <input id='b' type='text' value='10'></label><br><br><button id='btn'>計算する</button></div>"
      "<div id='out' class='card'></div>"
      "<h2>演算の意味</h2><table><tr><th>演算</th><th>働き</th></tr><tr><td>AND</td><td>特定のビットだけを取り出す(マスク)</td></tr><tr><td>OR</td><td>特定のビットを1にする</td></tr>"
      "<tr><td>XOR</td><td>特定のビットを反転する</td></tr><tr><td>NOT</td><td>全ビットを反転する</td></tr><tr><td>左シフト</td><td>2倍ずつ大きくする働き(上位は切り捨て)</td></tr><tr><td>右シフト</td><td>2で割る働き(小数点以下は切り捨て)</td></tr></table>"
      f"<script>{LIB}{BIT_JS}</script>")

    p("binary-basics.html", "2進数の基本|0と1で数を表す仕組み",
      "2進数の考え方、桁の重み、よく使う2のべき乗、ビットとバイトの関係を、初心者向けに解説します。",
      "<h1>2進数の基本</h1><p>2進数は、0と1の2種類の数字だけで数を表す方法です。コンピュータは、内部の電気的な状態(オンとオフ)を0と1に対応させて情報を扱います。</p>"
      "<h2>桁の重み</h2><p>10進数では、右から1の位・10の位・100の位…と、10倍ずつ重みが増えます。2進数では、右から1・2・4・8・16…と2倍ずつ増えます。</p>"
      "<table><tr><th>桁(右から)</th><td>8桁目</td><td>7</td><td>6</td><td>5</td><td>4</td><td>3</td><td>2</td><td>1桁目</td></tr><tr><th>重み</th><td>128</td><td>64</td><td>32</td><td>16</td><td>8</td><td>4</td><td>2</td><td>1</td></tr>"
      "<tr><th>例: 1101 0110</th><td>1</td><td>1</td><td>0</td><td>1</td><td>0</td><td>1</td><td>1</td><td>0</td></tr></table>"
      "<p>上の例は 128+64+16+4+2 = 214 です。</p>"
      "<h2>ビットとバイト</h2><ul><li>1ビット: 0か1の1桁</li><li>1バイト: 8ビット。0〜255の256通りを表せる</li><li>nビットで表せる値の種類は、2のn乗通り</li></ul>"
      "<h2>よく出る2のべき乗</h2><table><tr><th>べき乗</th><th>値</th></tr><tr><td>2の4乗</td><td>16</td></tr><tr><td>2の8乗</td><td>256</td></tr><tr><td>2の10乗</td><td>1,024</td></tr><tr><td>2の16乗</td><td>65,536</td></tr></table>"
      "<p><a href='converter.html'>変換ツール</a>で、いろいろな数を試してみましょう。負の数の表し方は<a href='twos-complement.html'>2の補数</a>のページへ。</p>")

    p("hex-basics.html", "16進数の基本|0〜9とA〜Fで数を表す",
      "16進数の考え方と、2進数との対応(4ビット=16進1桁)、見かける場面を解説します。",
      "<h1>16進数の基本</h1><p>16進数は、1桁で16種類を表す方法です。0〜9に加えて、10〜15をA〜F(a〜f)で表します。</p>"
      "<table><tr><th>10進</th><td>10</td><td>11</td><td>12</td><td>13</td><td>14</td><td>15</td></tr><tr><th>16進</th><td>A</td><td>B</td><td>C</td><td>D</td><td>E</td><td>F</td></tr></table>"
      "<h2>2進数との相性が良い理由</h2><p>2進数の4桁(4ビット)は、ちょうど16通りです。そのため、2進数を右から4桁ずつ区切ると、16進数の1桁に対応します。</p>"
      "<p>例: 1101 0110 → D(1101) と 6(0110) で、16進数の D6 になります。10進数では 214 です。</p>"
      "<h2>書き方の慣習</h2><ul><li>プログラミング言語では、0x を先頭に付けて 0xD6 と書くことが多い</li><li>HTMLの色指定では、# を付けて #ff8800 のように書く</li></ul>"
      "<p>書き方は言語やツールによって異なるため、使う環境の公式ドキュメントで確認してください。</p>"
      "<p><a href='converter.html'>変換ツール</a> / <a href='uses.html'>進数が使われる場面</a></p>")

    p("octal.html", "8進数の基本|3ビットごとの区切り",
      "8進数の考え方、2進数との対応(3ビット=8進1桁)、使われる場面の例を解説します。",
      "<h1>8進数の基本</h1><p>8進数は、0〜7の8種類の数字で数を表す方法です。桁が上がるごとに8倍になります。</p>"
      "<h2>2進数との対応</h2><p>2進数を右から3桁ずつ区切ると、8進数の1桁に対応します。</p>"
      "<table><tr><th>2進</th><td>000</td><td>001</td><td>010</td><td>011</td><td>100</td><td>101</td><td>110</td><td>111</td></tr><tr><th>8進</th><td>0</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td></tr></table>"
      "<p>例: 2進数 110 101 → 6 と 5 で、8進数の65。10進数では 53 です。</p>"
      "<h2>使われる場面の例</h2><p>UNIX系OSのファイル権限は、読み・書き・実行の3種類を3ビットで表し、所有者・グループ・その他の3組を8進数3桁(例: 755)で書く慣習があります。"
      "個々の意味や設定のしかたは、使っているOSの公式ドキュメントで確認してください。</p>"
      "<p><a href='converter.html'>変換ツール</a> / <a href='manual-conversion.html'>手計算のやり方</a></p>")

    p("manual-conversion.html", "進数変換の手計算のやり方|割り算と重みの足し算",
      "10進数から2進数・16進数へ、2進数から10進数へ、2進数と16進数の相互変換を、例つきで解説します。",
      "<h1>進数変換の手計算のやり方</h1>"
      "<h2>10進数 → n進数(割り算の方法)</h2><p>変換したい数をnで割り、余りを記録します。商が0になるまで繰り返し、余りを下から上へ並べると答えです。</p>"
      "<p>例: 10進数の45を2進数に</p><table><tr><th>割り算</th><th>商</th><th>余り</th></tr><tr><td>45 ÷ 2</td><td>22</td><td>1</td></tr><tr><td>22 ÷ 2</td><td>11</td><td>0</td></tr>"
      "<tr><td>11 ÷ 2</td><td>5</td><td>1</td></tr><tr><td>5 ÷ 2</td><td>2</td><td>1</td></tr><tr><td>2 ÷ 2</td><td>1</td><td>0</td></tr><tr><td>1 ÷ 2</td><td>0</td><td>1</td></tr></table>"
      "<p>余りを下から読むと 101101。つまり 45 = 101101(2進数)です。</p>"
      "<h2>n進数 → 10進数(重みの足し算)</h2><p>各桁の数に、その桁の重み(nのべき乗)をかけて足します。</p>"
      "<p>例: 2進数 101101 = 32+0+8+4+0+1 = 45。16進数 2D = 2×16 + 13 = 45。</p>"
      "<h2>2進数 ⇔ 16進数</h2><p>2進数を右から4桁ずつ区切って、それぞれを16進1桁にします。101101 は 0010 1101 なので、2 と D で 2D です。逆は、16進1桁を4桁の2進数に戻します。</p>"
      "<h2>検算のコツ</h2><ul><li>変換結果を逆方向に変換して、元の数に戻るか確認する</li><li><a href='converter.html'>変換ツール</a>の結果と見比べる</li></ul>")

    # 早見表(0〜31)
    rows = "".join(f"<tr><td>{n}</td><td>{to_base(n, 2).rjust(5, '0')}</td><td>{to_base(n, 8)}</td><td>{to_base(n, 16).upper()}</td></tr>" for n in range(32))
    p("table.html", "進数の早見表|0〜31の2進・8進・16進",
      "0から31までの数を、10進・2進・8進・16進で並べた早見表です。",
      "<h1>進数の早見表(0〜31)</h1><table><tr><th>10進</th><th>2進(5桁)</th><th>8進</th><th>16進</th></tr>" + rows + "</table>"
      "<p class='note'>範囲外の数は<a href='converter.html'>変換ツール</a>で計算できます。</p>")

    p("uses.html", "進数が使われる場面|色・メモリ・権限・文字コード",
      "16進数や2進数が実際に使われる場面(色コード、メモリ、ファイル権限、文字コードなど)を紹介します。",
      "<h1>進数が使われる場面</h1>"
      "<h2>色コード</h2><p>Webの色指定 #RRGGBB は、赤・緑・青をそれぞれ00〜ffの16進2桁(0〜255)で表したものです。</p>"
      "<h2>メモリアドレス・バイト列</h2><p>データの中身(バイト列)やメモリの位置は、1バイトを16進2桁で表すと読みやすいため、16進数で示されることが多いです。</p>"
      "<h2>ファイルの権限</h2><p>UNIX系OSでは、権限を8進数で書く慣習があります(<a href='octal.html'>8進数の基本</a>)。</p>"
      "<h2>文字コード</h2><p>文字には番号が割り当てられており、その番号は16進数で書かれることが一般的です(例: Unicodeのコードポイント)。割り当ての詳細は公式の規格で確認してください。</p>"
      "<h2>ネットワーク</h2><p>機器の識別に使うMACアドレスは、16進数で表記されます。IPv6アドレスも16進数で書きます。</p>"
      "<h2>ビット演算</h2><p>フラグの管理やマスク処理では、2進数・16進数で考えると分かりやすくなります(<a href='bitops.html'>ビット演算ツール</a>)。</p>")

    terms = [("ビット", "0か1を表す最小の単位"), ("バイト", "通常は8ビットのまとまり"), ("基数", "何進数かを決める数(2進数なら2)"),
             ("桁の重み", "各桁に対応する、基数のべき乗"), ("MSB", "最上位ビット。符号付き整数では符号を表す"), ("LSB", "最下位ビット。いちばん右のビット"),
             ("2の補数", "負の数を表すための代表的な方法"), ("マスク", "AND演算で特定のビットだけを取り出すこと"), ("シフト", "ビットを左右にずらす演算"),
             ("ニブル", "4ビットのまとまり。16進数1桁に対応")]
    p("glossary.html", "進数・ビットの用語集",
      "ビット・バイト・基数・2の補数・マスクなど、進数とビット演算に出てくる基本用語をまとめました。",
      "<h1>進数・ビットの用語集</h1><table><tr><th>用語</th><th>意味</th></tr>"
      + "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in terms) + "</table>"
      "<p><a href='binary-basics.html'>2進数の基本</a> / <a href='hex-basics.html'>16進数の基本</a></p>")
