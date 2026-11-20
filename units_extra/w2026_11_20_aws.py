"""AWS 追加単元(2026-11-20)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-beanstalk-lightsail", "Elastic BeanstalkとLightsail", 3,
     "Elastic Beanstalkは、アプリのコードを渡すと、実行環境の準備や管理をAWSが整えてくれるサービス。Lightsailは、サーバー・ストレージ・ネットワークを、手軽な定額プランで使えるサービス。",
     "Beanstalkは、荷物(コード)を預けると、配送の手配をまとめてやってくれる宅配サービス。Lightsailは、必要な機能が最初から揃ったセット商品。",
     ["Elastic Beanstalkは、アプリケーションのコードをアップロードすると、サーバーの用意、負荷分散、自動増減、監視などの設定をAWSが自動で組み立てる",
      "裏側ではEC2などの通常のAWSリソースが使われており、必要に応じて利用者が設定を調整できる。Beanstalk自体に追加料金はなく、使ったリソース分が課金される",
      "対応する言語や実行環境は、公式で確認",
      "Lightsailは、仮想サーバー、ストレージ、データベース、ネットワークなどをまとめて、わかりやすいプランで提供するサービス",
      "小規模なウェブサイト、ブログ、開発・検証用の環境など、手軽に始めたい場面に向く",
      "細かな設計の自由度を重視するならEC2、運用の手間を減らしたいならBeanstalk、手軽さと分かりやすさならLightsail、という使い分け",
      "料金プランの内容は変わることがあるため、公式で確認"],
     ["「コードを渡すと環境構築や管理を任せられる」=Elastic Beanstalk、と対応づける",
      "「簡単・手軽・定額のプランで小規模向け」=Lightsail、と対応づける"],
     [("aws-ec2", "EC2"), ("aws-compute-others", "その他のコンピューティングサービス"), ("aws-cloudformation-cdk", "CloudFormationとCDK")],
     [("コードをアップロードすると、環境の構築や負荷分散などをAWSが自動で整えるサービスは。", "Elastic Beanstalk"),
      ("小規模なサイトなどを、手軽なプランで始められるAWSのサービスは。", "Lightsail")]),
]

QUIZ = [
    ("アプリケーションのコードをアップロードするだけで、実行環境の用意や負荷分散、自動増減などをAWSが自動的に構成するサービスはどれか。",
     ["Elastic Beanstalk", "AWS Config", "Amazon Macie", "AWS Backup"], 0,
     "Elastic Beanstalkは、コードを渡すと環境の構築と管理をAWSが行う。裏ではEC2などが使われる。"),
]
