#!/usr/bin/env python3
"""
Protocol BuffersファイルからPythonコードを生成するスクリプト
"""

import os
import subprocess
import sys

def generate_proto_files():
    """Protocol BuffersファイルからPythonコードを生成"""
    
    # プロトコルファイルのパス
    proto_dir = "proto"
    output_dir = "kuksa_val_v1"
    
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 必要なファイル
    proto_files = [
        "proto/kuksa/val/v1/types.proto",
        "proto/kuksa/val/v1/val.proto"
    ]
    
    try:
        # grpcio-toolsを使用してPythonコードを生成
        cmd = [
            sys.executable, "-m", "grpc_tools.protoc",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            f"--proto_path={proto_dir}",
            "--proto_path=proto/kuksa/val/v1"
        ] + proto_files
        
        print("Protocol BuffersファイルからPythonコードを生成中...")
        print(f"コマンド: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Pythonコードの生成が完了しました")
            print(f"出力ディレクトリ: {output_dir}")
            
            # 生成されたファイルを確認
            generated_files = [
                f"{output_dir}/kuksa/val/v1/types_pb2.py",
                f"{output_dir}/kuksa/val/v1/types_pb2_grpc.py",
                f"{output_dir}/kuksa/val/v1/val_pb2.py",
                f"{output_dir}/kuksa/val/v1/val_pb2_grpc.py"
            ]
            
            for file_path in generated_files:
                if os.path.exists(file_path):
                    print(f"✅ 生成されたファイル: {file_path}")
                else:
                    print(f"❌ ファイルが見つかりません: {file_path}")
                    
        else:
            print("❌ Pythonコードの生成に失敗しました")
            print(f"エラー: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = generate_proto_files()
    if success:
        print("\n🎉 セットアップが完了しました！")
        print("次のコマンドでサーバーを起動できます:")
        print("python car_control_server.py")
    else:
        print("\n❌ セットアップに失敗しました")
        sys.exit(1) 