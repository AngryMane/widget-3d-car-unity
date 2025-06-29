#!/usr/bin/env python3
"""
gRPCクライアントの使用例

このスクリプトは、3D Car Control ServerのgRPC APIを使用する例を示します。
"""

import grpc
import time
from kuksa_val_v1 import val_pb2, val_pb2_grpc, types_pb2

def create_grpc_channel():
    """gRPCチャンネルを作成"""
    return grpc.insecure_channel('localhost:50051')

def get_vehicle_info(stub):
    """車両情報を取得"""
    print("=== 車両情報の取得 ===")
    
    # 複数のパスを一度に取得
    paths = [
        "Vehicle.Cabin.Door.Row1.DriverSide.IsOpen",
        "Vehicle.Body.Lights.Beam.High.IsOn",
        "Vehicle.AverageSpeed"
    ]
    
    entries = []
    for path in paths:
        entries.append(val_pb2.EntryRequest(
            path=path,
            view=types_pb2.VIEW_CURRENT_VALUE
        ))
    
    request = val_pb2.GetRequest(entries=entries)
    
    try:
        response = stub.Get(request)
        
        print("取得結果:")
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
            
            print(f"  {entry.path}: {value}")
        
        if response.errors:
            print("エラー:")
            for error in response.errors:
                print(f"  {error.path}: {error.error.message}")
                
    except grpc.RpcError as e:
        print(f"gRPCエラー: {e}")

def set_vehicle_value(stub, path, value):
    """車両の値を設定"""
    print(f"=== 車両値の設定: {path} = {value} ===")
    
    # データタイプに応じてDatapointを作成
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
    
    try:
        response = stub.Set(request)
        
        if response.error.code != 0:
            print(f"エラー: {response.error.message}")
        elif response.errors:
            print("エラー:")
            for error in response.errors:
                print(f"  {error.path}: {error.error.message}")
        else:
            print("✅ 値の設定が成功しました")
            
    except grpc.RpcError as e:
        print(f"gRPCエラー: {e}")

def get_server_info(stub):
    """サーバー情報を取得"""
    print("=== サーバー情報の取得 ===")
    
    request = val_pb2.GetServerInfoRequest()
    
    try:
        response = stub.GetServerInfo(request)
        print(f"サーバー名: {response.name}")
        print(f"バージョン: {response.version}")
        
    except grpc.RpcError as e:
        print(f"gRPCエラー: {e}")

def main():
    """メイン関数"""
    print("🚗 3D Car Control Server gRPCクライアント")
    print("=" * 50)
    
    # gRPCチャンネルを作成
    with create_grpc_channel() as channel:
        stub = val_pb2_grpc.VALStub(channel)
        
        # サーバー情報を取得
        get_server_info(stub)
        print()
        
        # 現在の車両情報を取得
        get_vehicle_info(stub)
        print()
        
        # ドアを開く
        set_vehicle_value(stub, "Vehicle.Cabin.Door.Row1.DriverSide.IsOpen", True)
        print()
        
        # 少し待機
        time.sleep(1)
        
        # ハイビームを点灯
        set_vehicle_value(stub, "Vehicle.Body.Lights.Beam.High.IsOn", True)
        print()
        
        # 少し待機
        time.sleep(1)
        
        # 更新された車両情報を取得
        get_vehicle_info(stub)
        print()
        
        # ドアを閉じる
        set_vehicle_value(stub, "Vehicle.Cabin.Door.Row1.DriverSide.IsOpen", False)
        print()
        
        # ハイビームを消灯
        set_vehicle_value(stub, "Vehicle.Body.Lights.Beam.High.IsOn", False)
        print()
        
        print("✅ クライアントの実行が完了しました")

if __name__ == "__main__":
    main() 