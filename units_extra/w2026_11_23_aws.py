"""AWS 追加単元(2026-11-23)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-api-gateway", "API Gatewayの用途", 3,
     "Amazon API Gatewayは、APIを作成・公開・管理するためのマネージドサービス。外部のクライアントからのリクエストを受け付け、Lambdaなどのバックエンドにつなぐ入口になる。",
     "API Gatewayは、ビルの受付カウンターのようなもの。訪問者(リクエスト)を受け付けて、確認したうえで、担当の部署(Lambdaなどのバックエンド)に取り次ぐ。",
     ["API(Application Programming Interface)は、ソフトウェア同士がやり取りするための窓口。WebアプリやスマートフォンアプリがAPI経由でデータや機能を呼び出す",
      "API Gatewayは、APIの作成、公開、保守、監視などを、サーバーを自分で用意せずに行えるマネージドサービス",
      "バックエンドには、AWS Lambda、EC2上のアプリ、他のAWSサービスなどを接続できる",
      "認証・認可、リクエストの流量制限(スロットリング)、キャッシュ、利用状況の監視などの機能がある。詳細な機能は公式で確認",
      "Lambdaと組み合わせると、サーバーを管理しないWeb APIを構成できる(サーバーレスの代表的な構成の一つ)",
      "料金は、主にAPIへのリクエスト数などに応じた従量課金。単価や種類は公式で確認",
      "メッセージの受け渡しにはSQSやSNS、イベントの連携にはEventBridgeなどがあり、API Gatewayは外部からのAPI呼び出しの入口として使い分ける"],
     ["「APIの作成・公開・管理の入口」=API Gateway、と結びつける",
      "LambdaとAPI Gatewayの組合せ=サーバーレスなWeb APIの構成、という典型を押さえる"],
     [("aws-integration", "アプリ連携(SQS・SNS・EventBridge・API Gateway)"), ("aws-lambda-pricing-limits", "Lambdaの料金と制限(概要)"), ("aws-compute-others", "Lambda・コンテナ・その他のコンピューティング")],
     [("APIの作成・公開・管理を行い、Lambdaなどのバックエンドへの入口になるAWSのサービスは。", "Amazon API Gateway"),
      ("API GatewayとLambdaを組み合わせると、どのような構成にできるか。", "サーバーを管理しないWeb API(サーバーレス構成)")]),
]

QUIZ = [
    ("APIの作成・公開・管理を、マネージドサービスとして提供するAWSのサービスはどれか。",
     ["Amazon API Gateway", "Amazon EBS", "AWS Shield", "Amazon Glacier"], 0,
     "API GatewayはAPIの入口として、リクエストの受付、認証、流量制限などを担い、Lambdaなどのバックエンドにつなぐ。"),
]
