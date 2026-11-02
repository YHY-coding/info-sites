"""AWS 追加単元(2026-11-02)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-dx-vpn", "Direct ConnectとVPNの比較", 3,
     "オンプレミスとAWSをつなぐ2つの方法。専用線で接続するDirect Connectと、インターネット上に暗号化した通り道を作るVPN。",
     "Direct Connectは自社専用の私道を引くこと、VPNは公道の上に鍵付きの護送車を走らせることにあたる。",
     ["Direct Connectは、お客様の拠点とAWSを専用線で結ぶ。通信がインターネットを経由しない",
      "通信品質が安定しやすい一方、開通までに準備の時間がかかることがある",
      "Site-to-Site VPNは、インターネット上に暗号化したトンネルを作って接続する。短い準備で始めやすい",
      "VPNはインターネットの状況に影響を受けうる",
      "両者を併用して、専用線を主に、VPNを予備にする構成もある",
      "VPNは通信を暗号化する。Direct Connect自体は暗号化を自動では行わないため、必要なら別途対策を考える",
      "料金や速度の選択肢は公式で確認"],
     ["「専用線、安定した通信」→ Direct Connect", "「インターネット経由、暗号化、早く始められる」→ VPN"],
     [("aws-networking", "VPCとネットワーク(Route 53・CloudFront・Direct Connect)"), ("aws-peering-tgw", "VPCピアリングとTransit Gateway")],
     [("インターネットを経由せず、拠点とAWSを専用線で結ぶサービスは。", "AWS Direct Connect"),
      ("インターネット上に暗号化したトンネルを作る接続方法は。", "Site-to-Site VPN")]),
]

QUIZ = [
    ("オンプレミスとAWSの間を、インターネットを経由せずに専用線で接続したい。適切なサービスはどれか。",
     ["AWS Direct Connect", "Amazon Route 53", "AWS WAF", "Amazon SQS"], 0,
     "Direct Connectは専用線での接続。VPNはインターネット経由の暗号化通信。"),
]
