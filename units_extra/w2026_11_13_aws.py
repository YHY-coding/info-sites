"""AWS 追加単元(2026-11-13)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-cloudtrail-cloudwatch-config", "CloudTrailとCloudWatchとConfigの比較", 3,
     "操作の記録はCloudTrail、性能の監視はCloudWatch、設定の変更履歴はConfigが担当する。",
     "CloudTrailは「誰がいつ何をしたか」の防犯カメラ、CloudWatchは体温計のような計測器、Configは設備の状態を記録する台帳。",
     ["AWS CloudTrailは、アカウントで行われた操作(API呼び出し)を記録する。誰が、いつ、何をしたかを後から調べられる",
      "Amazon CloudWatchは、CPU使用率などの数値(メトリクス)やログを集めて監視し、しきい値を超えたらアラームで通知できる",
      "AWS Configは、リソースの設定を記録し、変更の履歴や、決めたルールに沿っているかを確認できる",
      "「誰が操作したか」を調べたい→CloudTrail、「負荷が高くなったので通知したい」→CloudWatch、「設定がいつどう変わったか」→Config",
      "3つは役割が違うため、組み合わせて使うことが多い",
      "保存期間や料金などの細部は、公式で確認"],
     ["「誰が何をしたか」=CloudTrail、「性能の監視とアラーム」=CloudWatch、「設定の変更履歴」=Config"],
     [("aws-management", "管理サービス"), ("aws-security-services", "主なセキュリティサービス"), ("aws-compliance", "コンプライアンスと監査")],
     [("AWSアカウントで行われた操作(API呼び出し)を記録するサービスは。", "AWS CloudTrail"),
      ("リソースの設定の変更履歴を記録し、ルールとの適合を確認するサービスは。", "AWS Config")]),
]

QUIZ = [
    ("あるEC2インスタンスのCPU使用率がしきい値を超えたときに通知を受け取りたい。適切なサービスはどれか。",
     ["Amazon CloudWatch", "AWS CloudTrail", "AWS Artifact", "AWS Snowball"], 0,
     "CloudWatchはメトリクスを監視し、アラームで通知できる。CloudTrailは操作の記録用。"),
]
