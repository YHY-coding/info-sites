"""AWS 追加単元(2026-11-12)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-cognito", "Amazon Cognitoの用途", 2,
     "自分のWebアプリやモバイルアプリの利用者向けに、サインアップ・サインインと認証情報の管理を提供するサービス。",
     "自社が運営する会員制施設の受付で、会員登録と本人確認、会員証の発行を代行してくれるようなもの。",
     ["Amazon Cognitoは、アプリの利用者(エンドユーザー)の認証と認可を扱うサービス",
      "ユーザープールは、利用者の登録・サインインを管理する仕組み。外部のIDプロバイダを使ったサインインとも連携できる",
      "IDプール(ID Pools)は、サインインした利用者に、AWSのリソースを使うための一時的な認証情報を渡す仕組み",
      "自前で認証の仕組みを作らずに済むので、開発や運用の手間を減らせる",
      "AWSアカウントを使う社員向けの管理はIAM Identity Center、自社アプリの利用者向けはCognito、と使い分ける",
      "機能名や設定の細部は変更されることがあるため、公式で確認"],
     ["「アプリの利用者のサインインを管理」→ Cognito", "「社員が複数AWSアカウントへSSO」→ IAM Identity Center"],
     [("aws-iam-identity-center", "IAM Identity Center"), ("aws-iam-role-federation", "IAMロールとフェデレーション")],
     [("自社のモバイルアプリの利用者のサインインや登録を管理するAWSサービスは。", "Amazon Cognito"),
      ("社員向けの複数アカウントSSOと、アプリ利用者向けの認証は、それぞれどのサービスか。", "IAM Identity Center と Amazon Cognito")]),
]

QUIZ = [
    ("自社のモバイルアプリの利用者がサインアップとサインインをできるようにしたい。認証の仕組みを自前で作らず使えるAWSサービスはどれか。",
     ["Amazon Cognito", "AWS Backup", "Amazon Redshift", "AWS Direct Connect"], 0,
     "Amazon Cognitoは、アプリ利用者の登録・認証を提供する。社員向けのSSOはIAM Identity Centerが担う。"),
]
