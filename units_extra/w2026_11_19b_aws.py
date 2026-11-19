"""AWS 追加単元(2026-11-19 b)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-cloudformation-cdk", "CloudFormationとCDK", 3,
     "CloudFormationは、テンプレート(設計図)に書いた通りにAWSのリソースをまとめて作る・変更する・消すサービス。CDKは、プログラミング言語でその設計図を書く仕組み。",
     "家の設計図があれば、同じ家を何軒でも同じ仕様で建てられる。CDKは、設計図を手書きせずプログラムで生成する道具。",
     ["CloudFormationは、インフラをコードで定義する「Infrastructure as Code(IaC)」のサービス",
      "テンプレートはJSONまたはYAML形式で書き、リソースのまとまりを「スタック」として作成・更新・削除する",
      "同じテンプレートから、開発用・本番用など、同じ構成の環境を繰り返し作れる。手作業による設定ミスを減らせる",
      "AWS CDK(Cloud Development Kit)は、一般的なプログラミング言語でインフラを定義し、CloudFormationのテンプレートに変換して展開する",
      "CloudFormation自体の利用に追加料金はなく、作成されたリソースの分が課金される。最新の料金体系は公式で確認",
      "更新前に変更内容を確認する仕組み(変更セット)や、設定が手作業で変えられていないかを調べる仕組みもある。詳細は公式で確認"],
     ["「テンプレートでインフラを自動構築」=CloudFormation、と結びつける",
      "プログラミング言語で書ける=CDK、設計図の単位=スタック、の対応も押さえる"],
     [("aws-management", "管理・監視"), ("aws-systems-manager", "Systems Managerの機能"), ("aws-well-architected", "Well-Architectedフレームワーク")],
     [("AWSのリソースをテンプレートで定義し、まとめて作成・管理するサービスは。", "AWS CloudFormation"),
      ("CloudFormationで、まとめて管理されるリソースの単位を何と呼ぶか。", "スタック")]),
]

QUIZ = [
    ("AWSのインフラ構成をテンプレートとしてコード化し、同じ環境を繰り返し自動で構築したい。最も適切なサービスはどれか。",
     ["AWS CloudFormation", "Amazon Route 53", "AWS Direct Connect", "Amazon Polly"], 0,
     "CloudFormationは、テンプレートに基づいてリソースをスタックとして作成・更新・削除できる。"),
]
