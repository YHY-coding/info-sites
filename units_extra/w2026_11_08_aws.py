"""AWS 追加単元(2026-11-08)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-secrets-manager-parameter-store", "Secrets Managerとパラメータストア", 2,
     "パスワードやAPIキーなどの秘密情報を安全に保管するSecrets Managerと、設定値を一元管理するSystems Managerのパラメータストア。",
     "Secrets Managerは「合鍵を預かって定期的に交換までしてくれる管理人」、パラメータストアは「設定メモを整理して置いておく共有の棚」のようなもの。",
     ["AWS Secrets Managerは、データベースの認証情報やAPIキーなどの秘密情報を保管し、アプリケーションから安全に取り出せるようにするサービス",
      "Secrets Managerには、秘密情報を自動でローテーション(定期的な更新)する機能があり、対応するサービスと連携できる",
      "AWS Systems Managerのパラメータストアは、設定値や文字列を階層的に保存できる。暗号化して保存することもできる",
      "どちらも、アクセス制御にはIAMを使い、暗号化にはKMSを使える。コードに秘密情報を直接書かずに済む",
      "自動ローテーションなどの機能が必要なら、Secrets Managerを検討する。料金や機能差の細部は、公式で確認"],
     ["「秘密情報の保管と自動ローテーション」→ Secrets Manager", "「設定値の一元管理(暗号化も可)」→ パラメータストア"],
     [("aws-kms-cloudhsm", "KMSとCloudHSM"), ("aws-iam", "IAM(ユーザー・グループ・ロール・ポリシー)"), ("aws-security-services", "主なセキュリティサービス")],
     [("データベースの認証情報などを保管し、自動でローテーションできるAWSサービスは。", "AWS Secrets Manager"),
      ("設定値を階層的に保存でき、Systems Managerの一機能として提供されるものは。", "パラメータストア")]),
]

QUIZ = [
    ("データベースのパスワードを安全に保管し、定期的な自動ローテーションも行いたい。適切なAWSサービスはどれか。",
     ["AWS Secrets Manager", "Amazon Polly", "AWS Snowball", "Amazon Route 53"], 0,
     "Secrets Managerは秘密情報の保管と自動ローテーションに対応する。設定値の保存だけならパラメータストアも選択肢になる。"),
]
