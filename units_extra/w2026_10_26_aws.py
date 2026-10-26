"""AWS 追加単元(2026-10-26)。独自の言い回しで作成。"""

META = dict(append_to="aws")
DOMAINS = {}

UNITS = [
    ("aws-dms-sct", "DMSとSCT(データベース移行)", 3,
     "AWS DMSは、データベースのデータをAWSへ移すサービス。SCTは、異なる種類のデータベース間で、構造(スキーマ)などの変換を助けるツール。",
     "引っ越しで、荷物を運ぶ業者がDMS、家具が新居の間取りに合うよう寸法を調整する作業がSCT。",
     ["DMS(Database Migration Service)は、元のデータベースから移行先へデータをコピーする。移行中も元のDBを使い続けられる構成を取れる",
      "移行先が同じ種類のDB(同種移行)でも、種類の異なるDB(異種移行)でも使える",
      "SCT(Schema Conversion Tool)は、異種移行のときに、テーブル構造やプログラム部分の変換を支援する",
      "同種移行では変換作業が少なく、異種移行ではSCTによる変換と確認が重要になる",
      "ネットワーク越しにデータを継続的に反映する使い方もあるが、対応するDBの種類や条件は公式で確認"],
     ["「データベースの移行サービス」→ DMS", "「異なるDB間のスキーマ変換」→ SCT"],
     [("aws-migration-tools", "移行のツール(DMS・Snow・Migration Hub)"), ("aws-database", "データベース(RDS・Aurora・DynamoDB・Redshift)")],
     [("データベースのデータをAWSへ移行するためのサービスは何か。", "AWS DMS(Database Migration Service)"),
      ("異なる種類のデータベース間で、スキーマの変換を支援するツールは何か。", "AWS SCT(Schema Conversion Tool)")]),
]

QUIZ = [
    ("オンプレミスのデータベースのデータをAWS上のデータベースへ移行するために使うサービスはどれか。",
     ["AWS DMS", "Amazon CloudFront", "AWS Shield", "Amazon SNS"], 0,
     "DMSはデータベース移行用。CloudFrontはCDN、Shieldは攻撃対策、SNSは通知サービス。"),
]
