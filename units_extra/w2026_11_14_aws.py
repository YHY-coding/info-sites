"""AWS 追加単元(2026-11-14)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-cloudwatch-metrics-alarms", "CloudWatchのメトリクスとアラーム", 3,
     "CloudWatchは、リソースの状態を数値で集め、しきい値を超えたら通知や自動処理につなげる。",
     "体温計(メトリクス)と、熱が高いと鳴る警報器(アラーム)の組み合わせ。",
     ["メトリクスは、時間とともに記録される数値のデータ。EC2のCPU使用率などが、AWSの各サービスから自動で送られる",
      "アラームは、メトリクスが決めたしきい値を超えたときに、状態が変わる仕組み。通知(SNS)やAuto Scalingの動作につなげられる",
      "CloudWatch Logsは、アプリケーションやサービスのログを集めて保存・検索する機能",
      "独自の数値は、カスタムメトリクスとして送れる。メモリ使用率など、標準で取れないものに使う",
      "EventBridge(旧CloudWatch Events)は、イベントを受けて処理を起動する用途で使う",
      "標準の送信間隔や保存期間、料金は、公式で確認"],
     ["「しきい値を超えたら通知」=CloudWatchアラーム。操作の記録はCloudTrail",
      "CloudWatchアラームは、Auto Scalingの起点にもなる"],
     [("aws-cloudtrail-cloudwatch-config", "CloudTrailとCloudWatchとConfigの比較"), ("aws-management", "管理・監視")],
     [("メトリクスがしきい値を超えたときに状態が変わる、CloudWatchの仕組みは。", "アラーム"),
      ("アプリケーションのログを集めて保存・検索するCloudWatchの機能は。", "CloudWatch Logs")]),
]

QUIZ = [
    ("EC2インスタンスのCPU使用率が高い状態が続いたら、担当者にメールで知らせたい。組み合わせとして適切なものはどれか。",
     ["CloudWatchアラームとAmazon SNS", "CloudTrailとAWS Artifact", "AWS ConfigとAmazon S3", "AWS Backupと S3 Glacier"], 0,
     "CloudWatchアラームがしきい値を検知し、SNSで通知できる。"),
]
