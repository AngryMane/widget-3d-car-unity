#!/bin/bash

# 3D Car Control Server 起動スクリプト

echo "🚗 3D Car Control Server を起動しています..."

# 依存関係の確認
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 が見つかりません。Python3をインストールしてください。"
    exit 1
fi

# 仮想環境の確認と作成
if [ ! -d "venv" ]; then
    echo "📦 仮想環境を作成しています..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
echo "🔧 仮想環境をアクティベートしています..."
source venv/bin/activate

# 依存関係のインストール
echo "📦 依存関係をインストールしています..."
pip install -r requirements.txt

# Protocol Buffersファイルの生成
echo "🔨 Protocol Buffersファイルを生成しています..."
python generate_proto.py

# サーバーの起動
echo "🚀 サーバーを起動しています..."
echo "📱 Webインターフェース: http://localhost:8000"
echo "🔌 gRPCサーバー: localhost:50051"
echo "⏹️  停止するには Ctrl+C を押してください"
echo ""

python car_control_server.py 