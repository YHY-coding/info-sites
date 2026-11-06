"""AWS 追加単元(2026-11-26)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-control-tower", "Control TowerとLanding Zone", 2,
     "複数アカウントの環境を、推奨される構成とルールで素早く整え、継続して管理するAWS Control Tower。",
     "新しい支店を開くたびに、本社が用意した標準の設計図とルールブックで、同じ形に整えてくれる仕組み。",
     ["AWS Control Towerは、複数のAWSアカウントの環境を、ベストプラクティスに沿って構築・管理するサービス",
      "ランディングゾーンは、その土台となる、複数アカウント構成の安全な環境のこと",
      "ガードレールは、守るべきルール。予防的なものと、検出的なものがある",
      "AWS Organizationsの上に構築され、アカウントの新規作成も標準化して行える",
      "利用できる機能やリージョンは更新されるため、公式で確認"],
     ["「複数アカウント環境を推奨構成で素早く構築」→ Control Tower", "ルール(ガードレール)で統制を維持する"],
     [("aws-organizations-scp", "Organizationsとサービスコントロールポリシー"), ("aws-management", "管理・監視(CloudWatch・CloudFormation・Organizations)")],
     [("AWSの複数アカウント環境を、推奨構成で構築・管理するサービスは。", "AWS Control Tower"),
      ("Control Towerで、守るべきルールにあたるものを何と呼ぶか。", "ガードレール")]),
]

QUIZ = [
    ("複数のAWSアカウントの環境を、推奨される構成とガードレールで素早く整えて管理したい。適切なサービスはどれか。",
     ["AWS Control Tower", "Amazon Polly", "AWS Snowball", "Amazon Kinesis"], 0,
     "Control Towerは、ランディングゾーンとガードレールによって、複数アカウント環境を標準化して管理する。"),
]
