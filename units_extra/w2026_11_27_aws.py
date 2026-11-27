"""AWS 追加単元(2026-11-27 週次)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-athena-glue-emr", "Athena・Glue・EMRの使い分け", 3,
     "Athenaは、S3上のデータにSQLで問い合わせるサービス。Glueは、データの整理(カタログ化・変換)を担うサービス。EMRは、大規模データを分散処理するクラスタを用意するサービス。",
     "図書館にたとえると、Glueは本の目録を作って棚を整える司書、Athenaは目録を使って必要な情報をその場で調べる窓口、EMRは大量の資料を大勢で手分けして分析する作業部屋。",
     ["Amazon Athenaは、S3に置いたデータへ標準的なSQLで直接問い合わせできる。サーバーを用意せずに使え、料金は主にスキャンしたデータ量に応じる(詳細は公式で確認)",
      "AWS Glueは、データの抽出・変換・ロード(ETL)を行うサーバーレスのサービス。Glue Data Catalogでデータの場所や構造(スキーマ)の情報を管理する",
      "Amazon EMRは、HadoopやSparkなどのビッグデータ処理基盤を、マネージドなクラスタとして使えるサービス。大規模な分散処理に向く",
      "Glueでカタログ化したデータを、Athenaで問い合わせる、という組み合わせがよくある",
      "手軽にSQLで調べたいならAthena、データの変換や整理の流れを作るならGlue、処理の自由度や規模が必要ならEMR、と考える",
      "保存したデータを、継続的に高速に集計する用途には、データウェアハウスのRedshiftが候補になる",
      "どのサービスを選ぶかは、データ量・頻度・求める自由度による。細かな機能や料金は公式で確認する"],
     ["「S3のデータにSQLで問い合わせる」と来たらAthena、「ETL・データカタログ」と来たらGlue、と対応づける",
      "「HadoopやSparkなどの大規模分散処理」と来たらEMR、と覚える"],
     [("aws-redshift-usage", "Redshiftの用途"), ("aws-kinesis-family", "Kinesisの種類"), ("aws-s3-storage-classes", "S3のストレージクラス(深掘り)")],
     [("S3上のデータに、サーバーを用意せずSQLで問い合わせるサービスは。", "Amazon Athena"),
      ("データの抽出・変換・ロード(ETL)を行うサーバーレスのサービスは。", "AWS Glue")]),
]

QUIZ = [
    ("S3に置いたデータへ、サーバーを用意せずに標準的なSQLで直接問い合わせたい。最も適したサービスはどれか。",
     ["Amazon Athena", "Amazon EMR", "AWS Glue DataBrew", "Amazon ElastiCache"], 0,
     "S3上のデータにSQLで問い合わせるのがAthena。EMRは分散処理クラスタ、GlueはETLとデータカタログが中心。"),
]
