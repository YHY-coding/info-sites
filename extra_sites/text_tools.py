"""文字数カウント・全角半角変換・テキスト整形ツール集。規約: META と build(page, write) を持つ。出力は docs/text-tools/ 配下。"""
import html
import json
import math
import unicodedata

META = dict(slug="text-tools", name="テキスト整形ツール集", desc="文字数カウント、全角半角変換、ひらがなカタカナ変換、行の整理を、ブラウザだけで行える無料ツール")
SITE = dict(name=META["name"], home="index.html")
NAV = [("文字数", "count.html"), ("全角半角", "width.html"), ("かな変換", "kana.html"), ("行の整理", "lines.html"), ("解説", "chars-bytes.html")]
DISC = ("本サイトの結果は目安です。文字数の制限や数え方は、投稿先・提出先・応募要項などの公式の案内で確認してください。"
        "入力した文章は、ブラウザの中だけで処理され、送信されません。")

WS = " \t\n\r　"


def esc(s):
    return html.escape(s, quote=True)


# ---- 変換表(PythonとJSで同じデータを使う) ----
def _kana_tables():
    h2f, f2h = {}, {}
    for cp in range(0xFF61, 0xFF9F + 1):
        h = chr(cp)
        if cp in (0xFF9E, 0xFF9F):
            continue
        f = unicodedata.normalize("NFKC", h)
        h2f[h] = f
        f2h[f] = h
    # 濁音・半濁音(基底文字 + 濁点/半濁点)
    for cp in range(0x30A1, 0x30FA + 1):
        f = chr(cp)
        d = unicodedata.normalize("NFKD", f)
        if len(d) == 2 and d[1] in "゙゚" and d[0] in f2h:
            f2h[f] = f2h[d[0]] + ("ﾞ" if d[1] == "゙" else "ﾟ")
    return h2f, f2h


H2F, F2H = _kana_tables()
# 半角カナ+濁点/半濁点 → 全角(結合表)
COMB = {}
for _f, _h in F2H.items():
    if len(_h) == 2:
        COMB[_h] = _f


# ---- Python側の基準実装(ブラウザ側JSと一致することを確認する) ----
def stats(s):
    chars = len(s)
    nows = sum(1 for c in s if c not in WS)
    t = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = 0 if t == "" else len(t.split("\n"))
    nb = sum(1 for c in s if c not in "\r\n")
    return [chars, nows, lines, len(s.encode("utf-8")), math.ceil(nb / 400)]


def width(s, to_full, alnum, space, kana):
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        o = ord(c)
        if to_full:
            if alnum and 0x21 <= o <= 0x7E:
                out.append(chr(o + 0xFEE0))
            elif space and c == " ":
                out.append("　")
            elif kana and c in H2F:
                nx = s[i + 1] if i + 1 < n else ""
                if nx in ("ﾞ", "ﾟ") and (c + nx) in COMB:
                    out.append(COMB[c + nx])
                    i += 1
                else:
                    out.append(H2F[c])
            else:
                out.append(c)
        else:
            if alnum and 0xFF01 <= o <= 0xFF5E:
                out.append(chr(o - 0xFEE0))
            elif space and c == "　":
                out.append(" ")
            elif kana and c in F2H:
                out.append(F2H[c])
            else:
                out.append(c)
        i += 1
    return "".join(out)


def kana(s, to_kata):
    out = []
    for c in s:
        o = ord(c)
        if to_kata and 0x3041 <= o <= 0x3096:
            out.append(chr(o + 0x60))
        elif not to_kata and 0x30A1 <= o <= 0x30F6:
            out.append(chr(o - 0x60))
        else:
            out.append(c)
    return "".join(out)


def lineops(s, trim, drop_empty, dedupe, order):
    lines = s.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if trim:
        lines = [x.strip(WS) for x in lines]
    if drop_empty:
        lines = [x for x in lines if x != ""]
    if dedupe:
        seen, r = set(), []
        for x in lines:
            if x not in seen:
                seen.add(x)
                r.append(x)
        lines = r
    if order == "asc":
        lines = sorted(lines)
    elif order == "desc":
        lines = sorted(lines, reverse=True)
    elif order == "reverse":
        lines = lines[::-1]
    return "\n".join(lines)


# ---- ブラウザ側JS ----
CORE_JS = """
var WS=' \\t\\n\\r\\u3000';
var H2F=%s,F2H=%s,COMB=%s;
function cps(s){return Array.from(s)}
function stats(s){var a=cps(s),nows=0,nb=0,i;for(i=0;i<a.length;i++){if(WS.indexOf(a[i])<0)nows++;if(a[i]!=='\\r'&&a[i]!=='\\n')nb++}
var t=s.replace(/\\r\\n/g,'\\n').replace(/\\r/g,'\\n'),lines=t===''?0:t.split('\\n').length;
return [a.length,nows,lines,new TextEncoder().encode(s).length,Math.ceil(nb/400)]}
function width(s,toFull,alnum,space,kana){var a=cps(s),out=[],i,c,o,nx;
for(i=0;i<a.length;i++){c=a[i];o=c.codePointAt(0);
if(toFull){
if(alnum&&o>=0x21&&o<=0x7E)out.push(String.fromCodePoint(o+0xFEE0));
else if(space&&c===' ')out.push('\\u3000');
else if(kana&&H2F.hasOwnProperty(c)){nx=i+1<a.length?a[i+1]:'';
if((nx==='\\uff9e'||nx==='\\uff9f')&&COMB.hasOwnProperty(c+nx)){out.push(COMB[c+nx]);i++}else out.push(H2F[c])}
else out.push(c)}
else{
if(alnum&&o>=0xFF01&&o<=0xFF5E)out.push(String.fromCodePoint(o-0xFEE0));
else if(space&&c==='\\u3000')out.push(' ');
else if(kana&&F2H.hasOwnProperty(c))out.push(F2H[c]);
else out.push(c)}}
return out.join('')}
function kana(s,toKata){return cps(s).map(function(c){var o=c.codePointAt(0);
if(toKata&&o>=0x3041&&o<=0x3096)return String.fromCodePoint(o+0x60);
if(!toKata&&o>=0x30A1&&o<=0x30F6)return String.fromCodePoint(o-0x60);return c}).join('')}
function cmp(x,y){var a=cps(x),b=cps(y),i;for(i=0;i<a.length&&i<b.length;i++){var d=a[i].codePointAt(0)-b[i].codePointAt(0);if(d)return d}return a.length-b.length}
function trimWs(x){var a=cps(x),s=0,e=a.length;while(s<e&&WS.indexOf(a[s])>=0)s++;while(e>s&&WS.indexOf(a[e-1])>=0)e--;return a.slice(s,e).join('')}
function lineops(s,trim,dropEmpty,dedupe,order){var l=s.replace(/\\r\\n/g,'\\n').replace(/\\r/g,'\\n').split('\\n');
if(trim)l=l.map(trimWs);
if(dropEmpty)l=l.filter(function(x){return x!==''});
if(dedupe){var seen={},r=[];l.forEach(function(x){if(!Object.prototype.hasOwnProperty.call(seen,x)){seen[x]=1;r.push(x)}});l=r}
if(order==='asc')l=l.slice().sort(cmp);else if(order==='desc')l=l.slice().sort(function(a,b){return cmp(b,a)});else if(order==='reverse')l=l.slice().reverse();
return l.join('\\n')}
function $(id){return document.getElementById(id)}
function fmt(n){return n.toLocaleString('ja-JP')}
""" % (json.dumps(H2F, ensure_ascii=True), json.dumps(F2H, ensure_ascii=True), json.dumps(COMB, ensure_ascii=True))

COUNT_JS = """
function run(){var r=stats($('t').value);
$('out').innerHTML='<table><tr><th>文字数(改行・空白を含む)</th><td>'+fmt(r[0])+'</td></tr><tr><th>文字数(空白・改行を除く)</th><td>'+fmt(r[1])+'</td></tr><tr><th>行数</th><td>'+fmt(r[2])+'</td></tr><tr><th>UTF-8のバイト数</th><td>'+fmt(r[3])+'</td></tr><tr><th>400字詰め原稿用紙の枚数の目安</th><td>'+fmt(r[4])+'枚</td></tr></table>'}
$('t').oninput=run;run();
"""

WIDTH_JS = """
function run(){var d=$('d').value==='full';$('o').value=width($('t').value,d,$('a').checked,$('s').checked,$('k').checked)}
['t','d','a','s','k'].forEach(function(i){$(i).oninput=run;$(i).onchange=run});run();
"""

KANA_JS = """
function run(){$('o').value=kana($('t').value,$('d').value==='kata')}
['t','d'].forEach(function(i){$(i).oninput=run;$(i).onchange=run});run();
"""

LINES_JS = """
function run(){$('o').value=lineops($('t').value,$('a').checked,$('b').checked,$('c').checked,$('d').value)}
['t','a','b','c','d'].forEach(function(i){$(i).oninput=run;$(i).onchange=run});run();
"""


def build(page, write):
    slug = META["slug"]
    p = lambda path, title, desc, body: page(SITE, f"{slug}/{path}", title, desc, body, NAV, DISC)
    ta = lambda i, v="", ro="": f"<textarea id='{i}' rows='8' style='width:100%;box-sizing:border-box' {ro}>{esc(v)}</textarea>"

    p("index.html", "テキスト整形ツール集|文字数・全角半角・かな変換・行の整理",
      "文字数カウント、全角半角変換、ひらがなとカタカナの変換、行の重複削除や並べ替えを、ブラウザだけで行える無料ツール集です。",
      "<h1>テキスト整形ツール集</h1><p>入力した文章は、ブラウザの中だけで処理されます。サーバーには送信されません。</p>"
      "<div class='card'><a href='count.html'><strong>文字数カウント</strong></a><br>文字数・行数・バイト数・原稿用紙の枚数</div>"
      "<div class='card'><a href='width.html'><strong>全角半角変換</strong></a><br>英数字・記号・スペース・カタカナ</div>"
      "<div class='card'><a href='kana.html'><strong>ひらがな⇔カタカナ</strong></a><br>かなの相互変換</div>"
      "<div class='card'><a href='lines.html'><strong>行の整理</strong></a><br>空行の削除・重複の削除・並べ替え</div>"
      "<h2>解説ページ</h2><ul class='links'><li><a href='chars-bytes.html'>文字数とバイト数の違い</a></li><li><a href='zenkaku-hankaku.html'>全角と半角の基礎知識</a></li>"
      "<li><a href='line-breaks.html'>改行コードと空白文字</a></li><li><a href='convert-table.html'>変換の対応表</a></li></ul>")

    p("count.html", "文字数カウント|文字数・行数・バイト数を数える",
      "文章を貼り付けると、文字数(空白を含む・除く)、行数、UTF-8のバイト数、400字詰め原稿用紙の枚数の目安を表示します。",
      "<h1>文字数カウント</h1><div class='card'>" + ta("t", "ここに文章を入力します。\nこの2行目も数えます。") + "</div><div id='out' class='card'></div>"
      "<h2>数え方</h2><ul><li>1文字は、見た目の1文字ではなくUnicodeの1コードポイントとして数えます。絵文字や合成文字は、見た目より多く数えることがあります</li>"
      "<li>空白は、半角スペース、タブ、全角スペース、改行を指します</li>"
      "<li>原稿用紙の枚数は、改行を除いた文字数を400で割って切り上げた目安です。禁則処理や段落の字下げは考慮しません</li>"
      "<li>投稿先ごとの文字数の数え方は異なることがあります。<a href='chars-bytes.html'>文字数とバイト数の違い</a>と、投稿先の公式の案内を確認してください</li></ul>"
      f"<script>{CORE_JS}{COUNT_JS}</script>")

    p("width.html", "全角半角変換|英数字・スペース・カタカナ",
      "英数字・記号、スペース、カタカナを、全角と半角の間で相互に変換します。",
      "<h1>全角半角変換</h1><div class='card'><label>変換方向 <select id='d'><option value='half'>全角→半角</option><option value='full'>半角→全角</option></select></label><br>"
      "<label><input id='a' type='checkbox' checked> 英数字・記号</label> <label><input id='s' type='checkbox' checked> スペース</label> <label><input id='k' type='checkbox'> カタカナ</label><br><br>"
      "入力" + ta("t", "ＡＢＣ１２３　全角のテキスト ｶﾀｶﾅ") + "変換結果" + ta("o", "", "readonly") + "</div>"
      "<h2>変換の範囲</h2><ul><li>英数字・記号は、ASCIIの範囲(半角の「!」から「~」)と、対応する全角文字の間で変換します</li>"
      "<li>カタカナは、半角カナと全角カナの間で変換します。濁点・半濁点は、半角では1文字ぶんの別の文字になります</li>"
      "<li>漢字やひらがなは変換されません。詳しくは<a href='zenkaku-hankaku.html'>全角と半角の基礎知識</a>と<a href='convert-table.html'>変換の対応表</a>を参照してください</li></ul>"
      f"<script>{CORE_JS}{WIDTH_JS}</script>")

    p("kana.html", "ひらがな⇔カタカナ変換|かなを相互に変換",
      "ひらがなをカタカナに、カタカナをひらがなに変換します。ブラウザの中だけで処理されます。",
      "<h1>ひらがな⇔カタカナ変換</h1><div class='card'><label>変換方向 <select id='d'><option value='kata'>ひらがな→カタカナ</option><option value='hira'>カタカナ→ひらがな</option></select></label><br><br>"
      "入力" + ta("t", "これはひらがなのぶんしょうです。") + "変換結果" + ta("o", "", "readonly") + "</div>"
      "<h2>注意点</h2><ul><li>ひらがなとカタカナは、Unicodeの上で一定の間隔で並んでいるため、その差で変換しています</li>"
      "<li>漢字は変換されません。読み仮名への変換(ふりがな付け)は行いません</li>"
      "<li>長音記号(ー)、句読点、半角カナは、そのまま残ります。半角カナは<a href='width.html'>全角半角変換</a>で扱えます</li></ul>"
      f"<script>{CORE_JS}{KANA_JS}</script>")

    p("lines.html", "行の整理|空行削除・重複削除・並べ替え",
      "複数行のテキストについて、前後の空白の削除、空行の削除、重複行の削除、並べ替えを行います。",
      "<h1>行の整理</h1><div class='card'>"
      "<label><input id='a' type='checkbox' checked> 各行の前後の空白を削除</label><br><label><input id='b' type='checkbox' checked> 空行を削除</label><br>"
      "<label><input id='c' type='checkbox' checked> 重複した行を削除(最初の行を残す)</label><br>"
      "<label>並び順 <select id='d'><option value='none'>そのまま</option><option value='asc'>文字コード順(昇順)</option><option value='desc'>文字コード順(降順)</option><option value='reverse'>行を逆順にする</option></select></label><br><br>"
      "入力" + ta("t", "りんご\nみかん\n\nりんご\n  ばなな  \nみかん") + "変換結果" + ta("o", "", "readonly") + "</div>"
      "<h2>注意点</h2><ul><li>並べ替えは文字コード(Unicodeの番号)の順です。五十音順や辞書順とは一致しない場合があります</li>"
      "<li>改行コードは、結果ではすべて同じ形式(LF)に揃えます。違いは<a href='line-breaks.html'>改行コードと空白文字</a>を参照してください</li>"
      "<li>重複の判定は、完全に同じ文字列かどうかで行います。全角と半角は別の文字として扱います</li></ul>"
      f"<script>{CORE_JS}{LINES_JS}</script>")

    p("chars-bytes.html", "文字数とバイト数の違い|文字コードの基本",
      "文字数とバイト数がなぜ違うのか、UTF-8で日本語が何バイトになるかの目安と、数え方の注意点を解説します。",
      "<h1>文字数とバイト数の違い</h1><p>文字数は文字の個数、バイト数はコンピュータが保存するときのデータ量です。同じ文章でも、文字コードによってバイト数は変わります。</p>"
      "<h2>UTF-8の場合の目安</h2><table><tr><th>文字の種類</th><th>1文字のバイト数</th></tr>"
      "<tr><td>半角の英数字・基本的な記号</td><td>1バイト</td></tr><tr><td>ひらがな・カタカナ・一般的な漢字・全角の記号</td><td>3バイト</td></tr>"
      "<tr><td>絵文字や一部の珍しい漢字</td><td>4バイト</td></tr></table>"
      "<p>たとえば「abc」は3バイト、「あいう」は9バイトです。<a href='count.html'>文字数カウント</a>では、UTF-8のバイト数も表示します。</p>"
      "<h2>数え方が分かれる例</h2><ul><li>「é」のように、基本の文字と記号を組み合わせて表せる文字は、1文字として数えるか2文字として数えるかが仕組みによって変わります</li>"
      "<li>絵文字は、内部では複数のコードポイントで表されることがあり、見た目は1つでも数が増えることがあります</li>"
      "<li>古い仕組みでは、半角を1、全角を2と数える方式もあります</li></ul>"
      "<p class='note'>投稿サイトや応募フォームなどの文字数制限は、サービスごとに数え方が異なります。必ず提供元の公式の案内で確認してください。</p>")

    p("zenkaku-hankaku.html", "全角と半角の基礎知識|使い分けの考え方",
      "全角文字と半角文字の違い、混在で困りやすい場面、統一するときの考え方を解説します。",
      "<h1>全角と半角の基礎知識</h1><p>全角は日本語の文字と同じ幅で表示される文字、半角はその約半分の幅で表示される文字です。もともとは文字の見た目の幅を指す言葉で、文字コード上でも別の文字として区別されます。</p>"
      "<h2>混在で困りやすい場面</h2><ul><li>検索や並べ替えで、全角と半角の同じ文字が別のものとして扱われることがある</li>"
      "<li>同じ見た目の英数字でも、全角と半角が混ざると、重複の判定や集計が合わないことがある</li>"
      "<li>フォームやシステムが、半角のみ、または全角のみの入力を求める場合がある</li></ul>"
      "<h2>統一のおおまかな考え方</h2><ul><li>英数字と記号は、半角にそろえることが多い</li><li>日本語の文章中のカタカナは、全角が一般的。半角カナは、互換性のため残る古い形式として扱われる</li>"
      "<li>最終的な書式は、提出先や利用するシステムの指定に従う</li></ul>"
      "<p><a href='width.html'>全角半角変換</a>で一括して変換できます。変換される範囲は<a href='convert-table.html'>変換の対応表</a>にあります。</p>")

    p("line-breaks.html", "改行コードと空白文字|LF・CRLFとスペースの種類",
      "改行コード(LF、CRLF)の違いと、半角スペース・全角スペース・タブなど空白文字の種類を解説します。",
      "<h1>改行コードと空白文字</h1>"
      "<h2>改行コード</h2><table><tr><th>名前</th><th>内容</th><th>主な使われ方</th></tr>"
      "<tr><td>LF</td><td>改行1文字</td><td>Linuxやmacの文章ファイルなど</td></tr><tr><td>CRLF</td><td>復帰と改行の2文字</td><td>Windowsの文章ファイルなど</td></tr>"
      "<tr><td>CR</td><td>復帰1文字</td><td>ごく古いmacの形式</td></tr></table>"
      "<p>見た目は同じ改行でも、コードが違うと、ファイルの扱いやバイト数、行数の数え方が変わる場合があります。本サイトのツールは、3種類とも改行として扱います。</p>"
      "<h2>空白文字の種類</h2><table><tr><th>種類</th><th>特徴</th></tr><tr><td>半角スペース</td><td>キーボードのスペースキーで入力する空白</td></tr>"
      "<tr><td>全角スペース</td><td>日本語の文字と同じ幅の空白。見た目では半角との区別がつきにくい</td></tr><tr><td>タブ</td><td>次の位置までそろえる空白。表示幅は環境で変わる</td></tr></table>"
      "<p class='note'>文章の前後にある見えない空白は、重複の判定や検索の妨げになります。<a href='lines.html'>行の整理</a>で前後の空白を取り除けます。</p>")

    rows = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in
                   [("全角英字・数字(Ａ〜Ｚ、ａ〜ｚ、０〜９)", "半角英字・数字"), ("全角記号(！、＃、＄、％、＆、（、）、＋、＝、？、＠ など)", "半角記号"),
                    ("全角スペース", "半角スペース"), ("全角カタカナ(ガ、パ など濁点付きを含む)", "半角カナ(濁点・半濁点は別の1文字)")])
    p("convert-table.html", "変換の対応表|全角半角・かなの変換範囲",
      "全角半角変換とかな変換で、どの文字がどう変換されるかの対応を、一覧で示します。",
      "<h1>変換の対応表</h1><h2>全角半角変換</h2><table><tr><th>全角</th><th>半角</th></tr>" + rows + "</table>"
      "<p class='note'>全角と半角の間で完全には一対一にならない文字(例:一部の記号や、全角のチルダ・波ダッシュなど)があります。重要な文書では、変換後の結果を目で確認してください。</p>"
      "<h2>ひらがな⇔カタカナ</h2><table><tr><th>変換</th><th>範囲</th></tr><tr><td>ひらがな→カタカナ</td><td>「ぁ」から「ゖ」まで</td></tr>"
      "<tr><td>カタカナ→ひらがな</td><td>「ァ」から「ヶ」まで</td></tr><tr><td>変換されないもの</td><td>長音記号(ー)、句読点、漢字、半角カナ、「ヷ」などの特殊な文字</td></tr></table>"
      "<p><a href='width.html'>全角半角変換</a> / <a href='kana.html'>かな変換</a></p>")
