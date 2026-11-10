"""AWS 追加単元(2026-11-10)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-guardduty-inspector-macie", "GuardDuty・Inspector・Macieの比較", 2,
     "脅威を検知するGuardDuty、脆弱性を調べるInspector、S3内の機微な情報を見つけるMacie。",
     "GuardDutyは「不審な動きを見張る監視員」、Inspectorは「建物の弱点を点検する検査員」、Macieは「書庫で重要書類を探し出す係」のようなもの。",
     ["Amazon GuardDutyは、ログなどを分析して、不審な動きや脅威を検知する。エージェントの導入なしに有効化できる",
      "Amazon Inspectorは、EC2やコンテナイメージなどのソフトウェアの脆弱性を自動で調べる",
      "Amazon Macieは、機械学習を使って、S3内の個人情報などの機微なデータを見つけて保護を支援する",
      "3つとも、見つかった結果を確認して対応するためのサービス。自動で全てを修復するものではない",
      "「脅威の検知」「脆弱性の検査」「機微データの発見」という目的の違いで区別する",
      "対応範囲や料金の細部は、公式で確認"],
     ["「脅威・不審なアクティビティの検知」→ GuardDuty", "「脆弱性の検査」→ Inspector", "「S3の機微データの発見」→ Macie"],
     [("aws-security-services", "主なセキュリティサービス"), ("aws-shield-waf-firewall-manager", "ShieldとWAFとFirewall Manager"), ("aws-compliance", "コンプライアンスと監査")],
     [("ログを分析して不審な動きや脅威を検知するサービスは。", "Amazon GuardDuty"),
      ("S3内の個人情報などの機微なデータを見つけるサービスは。", "Amazon Macie")]),
]

QUIZ = [
    ("EC2インスタンスやコンテナイメージのソフトウェアの脆弱性を、自動で調べたい。適切なAWSサービスはどれか。",
     ["Amazon Inspector", "Amazon Macie", "AWS Snowball", "Amazon Polly"], 0,
     "Inspectorは脆弱性の検査。GuardDutyは脅威の検知、Macieは機微データの発見。"),
]
