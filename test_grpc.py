#!/usr/bin/env python3
"""
gRPCサーバーのテストスクリプト

このスクリプトは、3D Car Control ServerのgRPC APIをテストします。
"""

import grpc
import time
import sys
import os

# kuksa_val_v1パッケージをインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from kuksa_val_v1 import val_pb2, val_pb2_grpc, types_pb2

def test_server_connection():
    """サーバー接続をテスト"""
    print("🔍 サーバー接続をテスト中...")
    
    try:
        channel = grpc.insecure_channel('localhost:50051')
        stub = val_pb2_grpc.VALStub(channel)
        
        # サーバー情報を取得
        request = val_pb2.GetServerInfoRequest()
        response = stub.GetServerInfo(request)
        
        print(f"✅ サーバー接続成功")
        print(f"   サーバー名: {response.name}")
        print(f"   バージョン: {response.version}")
        return True
        
    except grpc.RpcError as e:
        print(f"❌ サーバー接続失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def test_get_vehicle_data():
    """車両データの取得をテスト"""
    print("\n📊 車両データ取得をテスト中...")
    
    try:
        channel = grpc.insecure_channel('localhost:50051')
        stub = val_pb2_grpc.VALStub(channel)
        
        # テスト用のパス
        test_paths = [
            "Vehicle.Cabin.Door.Row1.DriverSide.IsOpen",
            "Vehicle.Body.Lights.Beam.High.IsOn",
            "Vehicle.AverageSpeed"
        ]
        
        entries = []
        for path in test_paths:
            entries.append(val_pb2.EntryRequest(
                path=path,
                view=types_pb2.VIEW_CURRENT_VALUE
            ))
        
        request = val_pb2.GetRequest(entries=entries)
        response = stub.Get(request)
        
        print("✅ 車両データ取得成功")
        for entry in response.entries:
            value = None
            if entry.value.HasField('bool'):
                value = entry.value.bool
            elif entry.value.HasField('uint32'):
                value = entry.value.uint32
            elif entry.value.HasField('float'):
                value = entry.value.float
            elif entry.value.HasField('string'):
                value = entry.value.string
            
            print(f"   {entry.path}: {value}")
        
        if response.errors:
            print("⚠️  エラー:")
            for error in response.errors:
                print(f"   {error.path}: {error.error.message}")
        
        return True
        
    except grpc.RpcError as e:
        print(f"❌ 車両データ取得失敗: {e}")
        return False

def test_set_vehicle_data():
    """車両データの設定をテスト"""
    print("\n🔧 車両データ設定をテスト中...")
    
    try:
        channel = grpc.insecure_channel('localhost:50051')
        stub = val_pb2_grpc.VALStub(channel)
        
        # テスト用のデータ
        test_data = [
            ("Vehicle.Cabin.Door.Row1.DriverSide.IsOpen", True),
            ("Vehicle.Body.Lights.Beam.High.IsOn", True),
            ("Vehicle.AverageSpeed", 50.0)
        ]
        
        for path, value in test_data:
            print(f"   設定中: {path} = {value}")
            
            # Datapointを作成
            datapoint = types_pb2.Datapoint()
            
            if isinstance(value, bool):
                datapoint.bool = value
            elif isinstance(value, int):
                datapoint.uint32 = value
            elif isinstance(value, float):
                datapoint.float = value
            elif isinstance(value, str):
                datapoint.string = value
            
            entry = types_pb2.DataEntry(
                path=path,
                value=datapoint
            )
            
            update = val_pb2.EntryUpdate(entry=entry)
            request = val_pb2.SetRequest(updates=[update])
            
            response = stub.Set(request)
            
            if response.error.code != 0:
                print(f"   ❌ エラー: {response.error.message}")
            elif response.errors:
                print(f"   ❌ エラー:")
                for error in response.errors:
                    print(f"     {error.path}: {error.error.message}")
            else:
                print(f"   ✅ 成功")
        
        print("✅ 車両データ設定テスト完了")
        return True
        
    except grpc.RpcError as e:
        print(f"❌ 車両データ設定失敗: {e}")
        return False

def test_invalid_path():
    """無効なパスのテスト"""
    print("\n🚫 無効なパスのテスト中...")
    
    try:
        channel = grpc.insecure_channel('localhost:50051')
        stub = val_pb2_grpc.VALStub(channel)
        
        # 存在しないパスをテスト
        entries = [val_pb2.EntryRequest(
            path="Vehicle.Invalid.Path",
            view=types_pb2.VIEW_CURRENT_VALUE
        )]
        
        request = val_pb2.GetRequest(entries=entries)
        response = stub.Get(request)
        
        if response.errors:
            print("✅ 無効なパスが正しくエラーとして処理されました")
            for error in response.errors:
                print(f"   エラー: {error.path} - {error.error.message}")
            return True
        else:
            print("❌ 無効なパスがエラーとして処理されませんでした")
            return False
        
    except grpc.RpcError as e:
        print(f"❌ 無効なパステスト失敗: {e}")
        return False

def main():
    """メイン関数"""
    print("🧪 3D Car Control Server gRPCテスト")
    print("=" * 50)
    
    tests = [
        ("サーバー接続", test_server_connection),
        ("車両データ取得", test_get_vehicle_data),
        ("車両データ設定", test_set_vehicle_data),
        ("無効なパス", test_invalid_path),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}テスト開始...")
        if test_func():
            passed += 1
            print(f"✅ {test_name}テスト成功")
        else:
            print(f"❌ {test_name}テスト失敗")
    
    print("\n" + "=" * 50)
    print(f"📊 テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 全てのテストが成功しました！")
        return 0
    else:
        print("⚠️  一部のテストが失敗しました。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 