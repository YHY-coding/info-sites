"""AWS 追加単元(2026-11-09)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-shield-waf-firewall-manager", "ShieldとWAFとFirewall Manager", 2,
     "DDoS攻撃から守るShield、Webアプリへの不正なリクエストを防ぐWAF、複数アカウントのルールを一括管理するFirewall Manager。",
     "Shieldは「会場に押し寄せる大群を食い止める警備員」、WAFは「入場者の持ち物を検査する係」、Firewall Managerは「全支店の警備ルールを本部から配る担当」のようなもの。",
     ["AWS Shieldは、DDoS攻撃から守るサービス。基本的な保護は標準で提供され、より高度な保護を行う有料の層もある",
      "AWS WAFは、Webアプリケーションに届くHTTP/HTTPSリクエストを、ルールに基づいて許可・拒否する。SQLインジェクションなどへの対策に使う",
      "WAFは、CloudFrontやApplication Load Balancerなどと組み合わせて使える",
      "AWS Firewall Managerは、AWS Organizationsの複数アカウントにまたがって、WAFのルールなどを一元的に管理・適用する",
      "「DDoS対策」「リクエストの中身の検査」「複数アカウントの一括管理」という役割の違いを区別する",
      "各サービスの保護範囲や料金の細部は、公式で確認"],
     ["「DDoS攻撃からの保護」→ Shield", "「Webリクエストのフィルタリング」→ WAF", "「複数アカウントでルールを一括管理」→ Firewall Manager"],
     [("aws-security-services", "主なセキュリティサービス"), ("aws-network-security", "セキュリティグループとネットワークACL"), ("aws-cloudfront", "CloudFrontの仕組み")],
     [("DDoS攻撃からの保護を提供するAWSサービスは。", "AWS Shield"),
      ("複数アカウントにまたがってWAFのルールを一括管理するサービスは。", "AWS Firewall Manager")]),
]

QUIZ = [
    ("Webアプリケーションに届くリクエストを検査し、SQLインジェクションなどの不正なものを拒否したい。適切なAWSサービスはどれか。",
     ["AWS WAF", "AWS Snowball", "Amazon Polly", "AWS Backup"], 0,
     "AWS WAFはHTTP/HTTPSリクエストをルールに基づいて許可・拒否する。DDoS対策の中心はAWS Shield。"),
]
