"""AWS 追加単元(2026-11-01)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-global-accelerator", "Global AcceleratorとCloudFrontの違い", 3,
     "利用者からの通信をAWSのグローバルネットワークに早く乗せ、正常な配置先へ導くサービス。固定のIPアドレスが使える。",
     "高速道路の入口を近所に作り、そこから先は専用道路で目的地まで走らせるようなもの。",
     ["Global Acceleratorは、世界の入口(エッジ)から、AWSの内部ネットワーク経由でアプリケーションへ通信を届ける",
      "固定のエニーキャストIPアドレスが割り当てられ、アドレスを変えずに運用できる",
      "ヘルスチェックを行い、不調な配置先を避けて正常な側へ通信を振り分けられる",
      "TCPやUDPなど、HTTP以外の通信にも使える",
      "CloudFrontは、コンテンツをキャッシュして配信するCDN。キャッシュできる静的コンテンツに向く",
      "Global Acceleratorはキャッシュをしない。通信経路を最適化し、可用性を高めるのが目的",
      "料金の詳細は公式で確認"],
     ["「固定IP、TCP/UDP、経路の最適化」→ Global Accelerator", "「キャッシュして配信」→ CloudFront"],
     [("aws-cloudfront", "CloudFrontの仕組み"), ("aws-route53-policy", "Route 53のルーティングポリシー")],
     [("コンテンツをキャッシュせず、通信経路を最適化するのはどちらか。", "Global Accelerator"),
      ("Global Acceleratorで利用できる、固定のアドレスの種類は。", "エニーキャストIPアドレス")]),
]

QUIZ = [
    ("固定のIPアドレスを使いながら、世界の利用者の通信をAWSのネットワーク経由で正常な配置先へ導きたい。適切なサービスはどれか。",
     ["AWS Global Accelerator", "Amazon S3 Glacier", "AWS Config", "Amazon Athena"], 0,
     "固定のエニーキャストIPと経路最適化、ヘルスチェックによる振り分けはGlobal Acceleratorの特徴。"),
]
