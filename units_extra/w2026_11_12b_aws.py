"""AWS 追加単元(2026-11-12)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-security-hub", "Security Hub", 2,
     "複数のセキュリティサービスの検出結果を集めて、全体の状況を一か所で確認するサービス。",
     "各部署から届く点検報告を一枚の管理表にまとめて、優先して直す項目を見渡せるようにする係。",
     ["AWS Security Hubは、GuardDutyやInspectorなどの検出結果を集約して、一か所で確認できるようにする",
      "セキュリティのベストプラクティスに沿っているかを、基準に照らして自動でチェックする機能がある",
      "複数のアカウントやリージョンの結果をまとめて見る使い方ができる",
      "検出結果を確認して、対応の優先順位をつけるためのサービスで、自動で全てを修復するものではない",
      "個別の脅威検知はGuardDuty、脆弱性検査はInspectorが担当し、Security Hubはそれらを束ねる役",
      "対応する基準や料金の細部は、公式で確認"],
     ["「セキュリティの検出結果を集約して確認」→ Security Hub", "検知はGuardDuty、集約はSecurity Hub"],
     [("aws-security-services", "主なセキュリティサービス"), ("aws-guardduty-inspector-macie", "GuardDuty・Inspector・Macieの比較"), ("aws-compliance", "コンプライアンスと監査")],
     [("複数のセキュリティサービスの検出結果を集約して確認できるサービスは。", "AWS Security Hub"),
      ("Security Hubは、検出結果を自動で全て修復するか。", "しない(集約と確認の支援が中心)")]),
]

QUIZ = [
    ("GuardDutyやInspectorなど、複数のセキュリティサービスの検出結果を一か所に集約して確認したい。適切なAWSサービスはどれか。",
     ["AWS Security Hub", "Amazon Polly", "AWS Snowball", "Amazon SQS"], 0,
     "Security Hubは検出結果の集約と、基準に沿ったチェックを行う。"),
]
