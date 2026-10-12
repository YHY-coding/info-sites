"""AWSクラウドプラクティショナー 追加単元(2026-10-12週)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-elb-types", "Elastic Load Balancingの種類", 3,
     "ELBは、届いた通信を複数のターゲットへ振り分けるサービス。用途に応じて数種類のロードバランサーがある。",
     "混雑した窓口で、案内係が空いている窓口へお客さんを誘導してくれるようなもの。",
     ["Application Load Balancer(ALB): HTTP/HTTPSの通信向け。パスやホスト名に応じた振り分けができる(レイヤー7)",
      "Network Load Balancer(NLB): TCP/UDPなどの通信向け。高い性能と低い遅延が必要な場面に向く(レイヤー4)",
      "Gateway Load Balancer(GWLB): ファイアウォールなどの仮想アプライアンスへ通信を流すときに使う",
      "ヘルスチェックにより、異常なターゲットへは通信を送らない",
      "複数のアベイラビリティゾーンにまたがって使うことで、可用性を高められる。料金の詳細は公式で確認"],
     ["「HTTP/HTTPSをパスなどで振り分けたい」→ ALB", "「TCP/UDPで高性能」→ NLB", "「仮想アプライアンスへ通信を流す」→ GWLB"],
     [("aws-ec2", "EC2"), ("aws-networking", "ネットワーク")],
     [("HTTP/HTTPSの通信を、パスやホスト名に応じて振り分けるロードバランサーは?", "ALB"),
      ("ロードバランサーが、異常なターゲットへ通信を送らないために行う確認は?", "ヘルスチェック")]),
]

QUIZ = [
    ("HTTPリクエストのパスに応じて、通信を異なるターゲットへ振り分けたい。適切なものはどれか。",
     ["Application Load Balancer", "Direct Connect", "AWS Backup", "Amazon Glacier"], 0,
     "ALBはHTTP/HTTPS向けで、パスやホスト名による振り分けができる。他は専用線、バックアップ、アーカイブ用のサービス。"),
]
