"""AWS 追加単元(2026-11-26 週次)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-kinesis-family", "Kinesisの種類", 3,
     "Kinesisは、絶え間なく流れてくるデータ(ストリーミングデータ)を受け取り、処理・配信するためのサービス群。",
     "川の水をそのまま流しながら、浄水・分流・貯水槽への配水を行う設備のようなもの。データを溜めてから処理するのでなく、流れている間に扱う。",
     ["Kinesis Data Streams は、データを受け取り、一定期間保持して、複数のアプリケーションが読み取れるようにするサービス。処理の仕組みは、利用者が作る",
      "Amazon Data Firehose(旧 Kinesis Data Firehose)は、流れてくるデータを、S3 などの保存先へ自動で届けるサービス。管理の手間が少ない",
      "Kinesis Video Streams は、カメラなどの映像データを取り込み、保存や分析に使うためのサービス",
      "ストリーミング分析のサービスとして、Managed Service for Apache Flink があり、流れるデータをリアルタイムに集計・変換できる",
      "使い分けの目安は、自分で処理を書いて細かく制御するなら Data Streams、保存先へ届けるだけなら Firehose",
      "用途の例は、アクセスログの収集、IoT機器のセンサーデータ、クリックの流れの分析など",
      "サービス名や機能は変更されることがあるため、最新の名称と仕様は公式ドキュメントで確認する"],
     ["流れ続けるデータをリアルタイムに扱う、という話が出たら Kinesis を思い浮かべる",
      "保存先へそのまま届ける=Firehose、細かく処理する=Data Streams、映像=Video Streams、と対応させる"],
     [("aws-analytics-ai", "分析・AIサービスの概要"), ("aws-sqs-sns-eventbridge", "SQS・SNS・EventBridgeの使い分け")],
     [("S3 などの保存先へ、流れてくるデータを自動で届けるKinesis系のサービスは。", "Amazon Data Firehose"),
      ("カメラの映像データを取り込む Kinesis のサービスは。", "Kinesis Video Streams")]),
]

QUIZ = [
    ("センサーやログから絶え間なく届くデータを受け取り、複数のアプリケーションが読み取れるよう一定期間保持するサービスはどれか。",
     ["Kinesis Data Streams", "Amazon S3 Glacier", "AWS Backup", "Amazon Route 53"], 0,
     "ストリーミングデータの受け取りと保持は Kinesis Data Streams。保存先へ届けるだけなら Firehose も候補になる。"),
]
