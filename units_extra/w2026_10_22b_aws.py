"""AWS 追加単元(2026-10-22 第2便)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-aurora-vs-rds", "AuroraとRDSの違い", 3,
     "AuroraはAWSが作ったMySQL・PostgreSQL互換のデータベース。通常のRDSエンジンより高い性能と可用性を狙った設計になっている。",
     "RDSが「規格品の既製車」なら、Auroraは同じ免許で乗れるAWS専用チューンのスポーツモデル。",
     ["Auroraは、MySQL互換・PostgreSQL互換として使えるマネージドなデータベース",
      "ストレージが複数のアベイラビリティゾーンにまたがって自動的に複製され、耐久性と可用性が高い",
      "ストレージ容量は、使用量に合わせて自動で拡張される",
      "リードレプリカを追加して読み取りを分散できる",
      "性能の倍率、料金、対応バージョンなどの数値や細部は、公式で確認"],
     ["「MySQL・PostgreSQL互換で高性能・高可用」→ Aurora", "RDS系は管理型で、OSの管理はAWSの責任"],
     [("aws-database", "データベース(RDS・Aurora・DynamoDB・Redshift)"), ("aws-rds-features", "RDSの機能(マルチAZ・リードレプリカ)")],
     [("MySQL・PostgreSQL互換で、高い性能と可用性を狙ったAWSのデータベースは何か。", "Amazon Aurora"),
      ("Auroraのストレージは、どのように可用性を高めているか。", "複数のAZにまたがって自動的に複製される")]),
]

QUIZ = [
    ("MySQL互換のまま、高い性能と可用性を求めるマネージドなデータベースはどれか。",
     ["Amazon Aurora", "Amazon S3", "AWS Lambda", "Amazon CloudFront"], 0,
     "AuroraはMySQL・PostgreSQL互換で、複数AZにまたがる自動複製などにより高い可用性を実現する。"),
]
