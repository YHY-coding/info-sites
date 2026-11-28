"""AWS 追加単元(2026-11-28 週次)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-quicksight", "QuickSightの用途", 3,
     "Amazon QuickSightは、データをグラフや表にして、ダッシュボードで共有できるBI(ビジネスインテリジェンス)サービス。",
     "家計簿にたとえると、バラバラのレシートの数字を、グラフ付きの見やすい報告書にまとめて、家族みんなで見られるようにする道具。",
     ["QuickSightは、AWSのマネージドなBIサービス。データを可視化し、ダッシュボードを作って共有できる",
      "S3、Athena、Redshift、RDSなど、AWS内のさまざまなデータの出どころにつなげられる(対応先は公式で確認)",
      "サーバーを自分で用意せずに使え、利用するユーザー数や使い方に応じて料金がかかる(詳細は公式で確認)",
      "機械学習を使った機能で、傾向の予測や異常の検出、自然言語での問い合わせなどに対応している(提供状況は公式で確認)",
      "データを集めて変換するのはGlueやKinesis、データに問い合わせるのはAthena、グラフにして見せるのはQuickSight、と役割を分けて考える",
      "データの置き場として大量の集計に向くRedshiftと組み合わせる使い方もよくある"],
     ["「ダッシュボード」「BI」「データの可視化」と来たらQuickSight、と対応づける",
      "SQLで問い合わせるAthena、ETLのGlueと、役割を混同しない"],
     [("aws-athena-glue-emr", "Athena・Glue・EMRの使い分け"), ("aws-redshift-usage", "Redshiftの用途")],
     [("AWSで、データを可視化してダッシュボードで共有するBIサービスは。", "Amazon QuickSight"),
      ("S3上のデータにSQLで問い合わせるサービスは(QuickSightと役割を区別)。", "Amazon Athena")]),
]

QUIZ = [
    ("データをグラフにして、ダッシュボードで関係者に共有したい。最も適したAWSサービスはどれか。",
     ["Amazon QuickSight", "AWS Glue", "Amazon SQS", "AWS CloudTrail"], 0,
     "BIによる可視化とダッシュボード共有はQuickSight。Glueはデータ変換、SQSはキュー、CloudTrailは操作の記録。"),
]
