"""AWS 追加単元(2026-10-28)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-peering-tgw", "VPCピアリングとTransit Gateway", 3,
     "VPC同士をつなぐ方法。1対1の直結がピアリング、ハブで多数をつなぐのがTransit Gateway。",
     "ピアリングは2つの建物を渡り廊下で直結すること。Transit Gatewayは駅のターミナルで、多数の建物をまとめて乗り換えさせること。",
     ["VPCピアリングは、2つのVPC間をプライベートな経路で接続する。別アカウントや別リージョンのVPCとも接続できる",
      "ピアリングは、接続先同士の1対1の関係で、第三のVPC経由の中継はしない",
      "VPCの数が増えると、ピアリングは接続数が増えて管理が複雑になる",
      "Transit Gatewayは、多数のVPCやオンプレミスの接続を、ハブ&スポーク型でまとめる",
      "接続するVPC同士のIPアドレス範囲は重ならないようにする。料金などの詳細は公式で確認"],
     ["「2つのVPCを1対1で接続」→ VPCピアリング", "「多数のVPCをハブでまとめる」→ Transit Gateway"],
     [("aws-igw-nat", "インターネットゲートウェイとNATゲートウェイ"), ("aws-networking", "VPCとネットワーク(Route 53・CloudFront・Direct Connect)")],
     [("多数のVPCやオンプレミスをハブ型でまとめて接続するサービスは何か。", "Transit Gateway"),
      ("2つのVPCを1対1で接続する機能は何か。", "VPCピアリング")]),
]

QUIZ = [
    ("多数のVPCとオンプレミス環境を、中央のハブでまとめて接続したい。適切なサービスはどれか。",
     ["Transit Gateway", "NATゲートウェイ", "AWS Backup", "Amazon Polly"], 0,
     "Transit Gatewayがハブ型接続を提供する。ピアリングは1対1向き。"),
]
