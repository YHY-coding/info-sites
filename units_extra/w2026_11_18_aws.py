"""AWS 追加単元(2026-11-18)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-systems-manager", "Systems Managerの機能", 3,
     "Systems Managerは、多数のサーバーなどを、まとめて確認・操作・設定管理するための機能群。",
     "大きなビルの管理室。各部屋に行かなくても、遠隔でまとめて点検や設定変更ができる。",
     ["EC2インスタンスやオンプレミスのサーバーを、一元的に管理する運用管理サービス",
      "Run Commandは、複数のサーバーに対して、まとめてコマンドを実行する機能",
      "Session Managerは、ブラウザやCLIからサーバーに接続する機能。SSH用のポートを開けずに運用でき、操作の記録も残せる",
      "Patch Managerは、OSなどのパッチ適用を自動化・管理する機能",
      "Parameter Storeは、設定値や秘密情報を保管する機能。Secrets Managerとの違いは別ページで確認できる",
      "管理対象にするには、エージェントの導入と、必要な権限(IAMロール)の付与が前提になる。詳細は公式で確認",
      "機能の一部は追加料金の対象になることがある。料金は公式で確認"],
     ["「多数のサーバーにまとめてパッチ適用・コマンド実行」=Systems Manager",
      "「SSHのポートを開けずにサーバーへ接続」=Session Manager、と覚える"],
     [("aws-secrets-manager-parameter-store", "Secrets Managerとパラメータストア"), ("aws-cloudtrail-cloudwatch-config", "CloudTrail・CloudWatch・Configの比較"), ("aws-management", "管理・監視")],
     [("多数のサーバーにまとめてコマンドを実行するSystems Managerの機能は。", "Run Command"),
      ("SSH用のポートを開けずにサーバーへ接続できるSystems Managerの機能は。", "Session Manager")]),
]

QUIZ = [
    ("多数のEC2インスタンスに、OSのパッチ適用を一括で管理・自動化したい。最も適切なサービスはどれか。",
     ["AWS Systems Manager", "Amazon Rekognition", "AWS Direct Connect", "Amazon Route 53"], 0,
     "Systems ManagerのPatch Managerで、パッチ適用を一元的に管理できる。"),
]
