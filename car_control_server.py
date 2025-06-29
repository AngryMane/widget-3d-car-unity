#!/usr/bin/env python3
"""
3D Car Control Server

このサーバーは以下の機能を提供します：
1. gRPCサーバー - KUKSA VALプロトコルに基づく車両制御API
2. Webサーバー - Unity WebGLビルドを表示するブラウザインターフェース
3. WebSocket - リアルタイム通信
"""

import asyncio
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Set
import threading

import grpc
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# gRPC関連のインポート
from kuksa_val_v1 import val_pb2, val_pb2_grpc
from kuksa_val_v1 import types_pb2

# 設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 車両状態管理
class VehicleState:
    """車両の状態を管理するクラス"""
    
    def __init__(self):
        self.state: Dict[str, any] = {
            # ドア関連
            "Vehicle.Cabin.Door.Row1.DriverSide.IsOpen": False,
            "Vehicle.Cabin.Door.Row1.DriverSide.IsLocked": False,
            "Vehicle.Cabin.Door.Row1.DriverSide.Position": 0,
            "Vehicle.Cabin.Door.Row1.PassengerSide.IsOpen": False,
            "Vehicle.Cabin.Door.Row1.PassengerSide.IsLocked": False,
            "Vehicle.Cabin.Door.Row1.PassengerSide.Position": 0,
            
            # ウィンドウ関連
            "Vehicle.Cabin.Door.Row1.DriverSide.Window.IsOpen": False,
            "Vehicle.Cabin.Door.Row1.DriverSide.Window.Position": 0,
            "Vehicle.Cabin.Door.Row1.PassengerSide.Window.IsOpen": False,
            "Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position": 0,
            
            # シート関連
            "Vehicle.Cabin.Seat.Row1.DriverSide.Position": 0,
            "Vehicle.Cabin.Seat.Row1.DriverSide.Height": 0,
            "Vehicle.Cabin.Seat.Row1.PassengerSide.Position": 0,
            "Vehicle.Cabin.Seat.Row1.PassengerSide.Height": 0,
            
            # ライト関連
            "Vehicle.Body.Lights.Beam.High.IsOn": False,
            "Vehicle.Body.Lights.Beam.Low.IsOn": False,
            "Vehicle.Body.Lights.Brake.IsActive": False,
            "Vehicle.Body.Lights.Hazard.IsSignaling": False,
            "Vehicle.Body.Lights.LicensePlate.IsOn": False,
            
            # トランク関連
            "Vehicle.Body.Trunk.Front.IsOpen": False,
            "Vehicle.Body.Trunk.Front.IsLocked": False,
            "Vehicle.Body.Trunk.Front.Position": 0,
            "Vehicle.Body.Trunk.Front.IsLightOn": False,
            "Vehicle.Body.Trunk.Rear.IsOpen": False,
            "Vehicle.Body.Trunk.Rear.IsLocked": False,
            "Vehicle.Body.Trunk.Rear.Position": 0,
            "Vehicle.Body.Trunk.Rear.IsLightOn": False,
            
            # ミラー関連
            "Vehicle.Body.Mirrors.DriverSide.IsFolded": False,
            "Vehicle.Body.Mirrors.DriverSide.IsLocked": False,
            "Vehicle.Body.Mirrors.PassengerSide.IsFolded": False,
            "Vehicle.Body.Mirrors.PassengerSide.IsLocked": False,
            
            # その他
            "Vehicle.AverageSpeed": 0.0,
            "Vehicle.Body.Windshield.Front.Wiping.Mode": "OFF",
            "Vehicle.Body.Windshield.Rear.Wiping.Mode": "OFF",
        }
        
        # メタデータ定義
        self.metadata: Dict[str, types_pb2.Metadata] = self._create_metadata()
        
    def _create_metadata(self) -> Dict[str, types_pb2.Metadata]:
        """メタデータを作成"""
        metadata = {}
        
        # ブール値のメタデータ
        bool_paths = [
            "Vehicle.Cabin.Door.Row1.DriverSide.IsOpen",
            "Vehicle.Cabin.Door.Row1.DriverSide.IsLocked",
            "Vehicle.Cabin.Door.Row1.PassengerSide.IsOpen",
            "Vehicle.Cabin.Door.Row1.PassengerSide.IsLocked",
            "Vehicle.Cabin.Door.Row1.DriverSide.Window.IsOpen",
            "Vehicle.Cabin.Door.Row1.PassengerSide.Window.IsOpen",
            "Vehicle.Body.Lights.Beam.High.IsOn",
            "Vehicle.Body.Lights.Beam.Low.IsOn",
            "Vehicle.Body.Lights.Brake.IsActive",
            "Vehicle.Body.Lights.Hazard.IsSignaling",
            "Vehicle.Body.Lights.LicensePlate.IsOn",
            "Vehicle.Body.Trunk.Front.IsOpen",
            "Vehicle.Body.Trunk.Front.IsLocked",
            "Vehicle.Body.Trunk.Front.IsLightOn",
            "Vehicle.Body.Trunk.Rear.IsOpen",
            "Vehicle.Body.Trunk.Rear.IsLocked",
            "Vehicle.Body.Trunk.Rear.IsLightOn",
            "Vehicle.Body.Mirrors.DriverSide.IsFolded",
            "Vehicle.Body.Mirrors.DriverSide.IsLocked",
            "Vehicle.Body.Mirrors.PassengerSide.IsFolded",
            "Vehicle.Body.Mirrors.PassengerSide.IsLocked",
        ]
        
        for path in bool_paths:
            metadata[path] = types_pb2.Metadata(
                data_type=types_pb2.DATA_TYPE_BOOLEAN,
                entry_type=types_pb2.ENTRY_TYPE_ACTUATOR,
                description=f"Vehicle control for {path}",
                unit="boolean"
            )
        
        # 数値のメタデータ
        uint8_paths = [
            "Vehicle.Cabin.Door.Row1.DriverSide.Position",
            "Vehicle.Cabin.Door.Row1.PassengerSide.Position",
            "Vehicle.Cabin.Door.Row1.DriverSide.Window.Position",
            "Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position",
            "Vehicle.Cabin.Seat.Row1.DriverSide.Position",
            "Vehicle.Cabin.Seat.Row1.DriverSide.Height",
            "Vehicle.Cabin.Seat.Row1.PassengerSide.Position",
            "Vehicle.Cabin.Seat.Row1.PassengerSide.Height",
            "Vehicle.Body.Trunk.Front.Position",
            "Vehicle.Body.Trunk.Rear.Position",
        ]
        
        for path in uint8_paths:
            metadata[path] = types_pb2.Metadata(
                data_type=types_pb2.DATA_TYPE_UINT8,
                entry_type=types_pb2.ENTRY_TYPE_ACTUATOR,
                description=f"Vehicle control for {path}",
                unit="percentage",
                value_restriction=types_pb2.ValueRestriction(
                    unsigned=types_pb2.ValueRestrictionUint(min=0, max=100)
                )
            )
        
        # 浮動小数点のメタデータ
        float_paths = [
            "Vehicle.AverageSpeed",
        ]
        
        for path in float_paths:
            metadata[path] = types_pb2.Metadata(
                data_type=types_pb2.DATA_TYPE_FLOAT,
                entry_type=types_pb2.ENTRY_TYPE_SENSOR,
                description=f"Vehicle sensor for {path}",
                unit="km/h"
            )
        
        # 文字列のメタデータ
        string_paths = [
            "Vehicle.Body.Windshield.Front.Wiping.Mode",
            "Vehicle.Body.Windshield.Rear.Wiping.Mode",
        ]
        
        for path in string_paths:
            metadata[path] = types_pb2.Metadata(
                data_type=types_pb2.DATA_TYPE_STRING,
                entry_type=types_pb2.ENTRY_TYPE_ACTUATOR,
                description=f"Vehicle control for {path}",
                value_restriction=types_pb2.ValueRestriction(
                    string=types_pb2.ValueRestrictionString(
                        allowed_values=["OFF", "SLOW", "FAST"]
                    )
                )
            )
        
        return metadata
    
    def get_value(self, path: str) -> any:
        """指定されたパスの値を取得"""
        return self.state.get(path)
    
    def set_value(self, path: str, value: any) -> bool:
        """指定されたパスの値を設定"""
        if path in self.state:
            self.state[path] = value
            return True
        return False
    
    def get_metadata(self, path: str) -> Optional[types_pb2.Metadata]:
        """指定されたパスのメタデータを取得"""
        return self.metadata.get(path)

# WebSocket接続管理
class ConnectionManager:
    """WebSocket接続を管理するクラス"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._message_queue = []
        self._lock = threading.Lock()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        if self.active_connections:
            await asyncio.gather(
                *[connection.send_text(message) for connection in self.active_connections]
            )
    
    def broadcast_sync(self, message: str):
        """同期的なブロードキャスト（gRPCスレッドから呼び出し用）"""
        with self._lock:
            self._message_queue.append(message)
    
    def get_pending_messages(self):
        """保留中のメッセージを取得"""
        with self._lock:
            messages = self._message_queue.copy()
            self._message_queue.clear()
            return messages

# gRPCサービス実装
class VALServicer(val_pb2_grpc.VALServicer):
    """KUKSA VALプロトコルのgRPCサービス実装"""
    
    def __init__(self, vehicle_state: VehicleState, connection_manager: ConnectionManager):
        self.vehicle_state = vehicle_state
        self.connection_manager = connection_manager
        self.subscribers: Set[str] = set()
    
    def Get(self, request, context):
        """データエントリを取得"""
        logger.info(f"Get request received: {request}")
        
        entries = []
        errors = []
        
        for entry_request in request.entries:
            path = entry_request.path
            value = self.vehicle_state.get_value(path)
            metadata = self.vehicle_state.get_metadata(path)
            
            if value is not None:
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
                
                # DataEntryを作成
                entry = types_pb2.DataEntry(
                    path=path,
                    value=datapoint
                )
                
                # メタデータを追加
                if metadata and entry_request.view in [types_pb2.VIEW_METADATA, types_pb2.VIEW_ALL]:
                    entry.metadata.CopyFrom(metadata)
                
                entries.append(entry)
            else:
                # エラーを作成
                error = val_pb2.DataEntryError(
                    path=path,
                    error=val_pb2.Error(
                        code=404,
                        reason="NOT_FOUND",
                        message=f"Path {path} not found"
                    )
                )
                errors.append(error)
        
        return val_pb2.GetResponse(entries=entries, errors=errors)
    
    def Set(self, request, context):
        """データエントリの値を設定"""
        logger.info(f"Set request received: {request}")
        
        errors = []
        
        for update in request.updates:
            path = update.entry.path
            value = None
            
            # 値の取得
            datapoint = update.entry.value
            if datapoint.HasField('bool'):
                value = datapoint.bool
            elif datapoint.HasField('uint32'):
                value = datapoint.uint32
            elif datapoint.HasField('float'):
                value = datapoint.float
            elif datapoint.HasField('string'):
                value = datapoint.string
            
            if value is not None:
                success = self.vehicle_state.set_value(path, value)
                if success:
                    # WebSocketを通じてUnityに通知（同期的に）
                    message = {
                        "type": "vehicle_update",
                        "path": path,
                        "value": value
                    }
                    self.connection_manager.broadcast_sync(json.dumps(message))
                else:
                    error = val_pb2.DataEntryError(
                        path=path,
                        error=val_pb2.Error(
                            code=400,
                            reason="BAD_REQUEST",
                            message=f"Failed to set value for {path}"
                        )
                    )
                    errors.append(error)
            else:
                error = val_pb2.DataEntryError(
                    path=path,
                    error=val_pb2.Error(
                        code=400,
                        reason="BAD_REQUEST",
                        message=f"Invalid value type for {path}"
                    )
                )
                errors.append(error)
        
        return val_pb2.SetResponse(errors=errors)
    
    def Subscribe(self, request, context):
        """データエントリの変更を購読"""
        logger.info(f"Subscribe request received: {request}")
        
        # 購読者を追加
        subscriber_id = str(id(context))
        self.subscribers.add(subscriber_id)
        
        try:
            while context.is_active():
                # 定期的に状態を送信（実際の実装では変更検知が必要）
                yield val_pb2.SubscribeResponse()
                context.abort(grpc.StatusCode.UNIMPLEMENTED, "Streaming not fully implemented")
        finally:
            self.subscribers.discard(subscriber_id)
    
    def GetServerInfo(self, request, context):
        """サーバー情報を取得"""
        return val_pb2.GetServerInfoResponse(
            name="3D-Car-Control-Server",
            version="1.0.0"
        )
    
    async def _notify_unity(self, path: str, value: any):
        """Unityに変更を通知（非同期版）"""
        message = {
            "type": "vehicle_update",
            "path": path,
            "value": value
        }
        await self.connection_manager.broadcast(json.dumps(message))

# FastAPIアプリケーション
app = FastAPI(title="3D Car Control Server", version="1.0.0")

# 静的ファイルのマウント
app.mount("/Build", StaticFiles(directory="Build"), name="build")
app.mount("/TemplateData", StaticFiles(directory="TemplateData"), name="templatedata")

# グローバル変数
vehicle_state = VehicleState()
connection_manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """メインHTMLページを返す"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>3D Car Control</title>
        <link rel="shortcut icon" href="TemplateData/favicon.ico">
        <link rel="stylesheet" href="TemplateData/style.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.46.0/tabler-icons.min.css">
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body>
        <div id="unity-container" class="unity-desktop">
            <canvas id="unity-canvas" tabindex="-1"></canvas>
            <div id="unity-loading-bar">
                <div id="unity-logo"></div>
                <div id="unity-progress-bar-empty">
                    <div id="unity-progress-bar-full"></div>
                </div>
            </div>
            <div id="unity-warning"></div>
            <div id="unity-footer"></div>
        </div>

        <div id="control-panel" class="fixed top-4 right-4 bg-white p-4 rounded-lg shadow-lg">
            <h3 class="text-lg font-bold mb-4">車両制御パネル</h3>
            <div class="space-y-2">
                <button onclick="controlDoor('Vehicle.Cabin.Door.Row1.DriverSide.IsOpen', true)" 
                        class="bg-blue-500 text-white px-3 py-1 rounded text-sm">
                    ドア開
                </button>
                <button onclick="controlDoor('Vehicle.Cabin.Door.Row1.DriverSide.IsOpen', false)" 
                        class="bg-red-500 text-white px-3 py-1 rounded text-sm">
                    ドア閉
                </button>
                <button onclick="controlLight('Vehicle.Body.Lights.Beam.High.IsOn', true)" 
                        class="bg-yellow-500 text-white px-3 py-1 rounded text-sm">
                    ハイビームON
                </button>
                <button onclick="controlLight('Vehicle.Body.Lights.Beam.High.IsOn', false)" 
                        class="bg-gray-500 text-white px-3 py-1 rounded text-sm">
                    ハイビームOFF
                </button>
            </div>
        </div>

        <script src="Build/widget-3d-car-unity.loader.js"></script>
        <script src="FromUnity.js"></script>
        <script>
            var canvas = document.querySelector("#unity-canvas");
            var unityInstance;

            function unityShowBanner(msg, type) {
                var warningBanner = document.querySelector("#unity-warning");
                function updateBannerVisibility() {
                    warningBanner.style.display = warningBanner.children.length ? 'block' : 'none';
                }
                var div = document.createElement('div');
                div.innerHTML = msg;
                warningBanner.appendChild(div);
                if (type == 'error') div.style = 'background: red; padding: 10px;';
                else if (type == 'warning') div.style = 'background: yellow; padding: 10px;';
                updateBannerVisibility();
            }

            var buildUrl = "Build";
            var loaderUrl = buildUrl + "/widget-3d-car-unity.loader.js";
            var config = {
                arguments: [],
                dataUrl: buildUrl + "/widget-3d-car-unity.data.unityweb",
                frameworkUrl: buildUrl + "/widget-3d-car-unity.framework.js.unityweb",
                codeUrl: buildUrl + "/widget-3d-car-unity.wasm.unityweb",
                streamingAssetsUrl: "StreamingAssets",
                companyName: "DefaultCompany",
                productName: "3D Car Control",
                productVersion: "1.0",
                showBanner: unityShowBanner,
            };

            if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
                var meta = document.createElement('meta');
                meta.name = 'viewport';
                meta.content = 'width=device-width, height=device-height, initial-scale=1.0, user-scalable=no, shrink-to-fit=yes';
                document.getElementsByTagName('head')[0].appendChild(meta);
                document.querySelector("#unity-container").className = "unity-mobile";
                canvas.className = "unity-mobile";
            } else {
                canvas.style.width = "100vw";
                canvas.style.height = "100vh";
            }

            document.querySelector("#unity-loading-bar").style.display = "block";

            var script = document.createElement("script");
            script.src = loaderUrl;
            script.onload = () => {
                createUnityInstance(canvas, config, (progress) => {
                    document.querySelector("#unity-progress-bar-full").style.width = 100 * progress + "%";
                }).then((instance) => {
                    unityInstance = instance;
                    document.querySelector("#unity-loading-bar").style.display = "none";
                    console.log("Unity instance created successfully");
                }).catch((message) => {
                    alert(message);
                });
            };
            document.body.appendChild(script);

            // WebSocket接続
            var ws = new WebSocket('ws://localhost:8000/ws');
            ws.onmessage = function(event) {
                var data = JSON.parse(event.data);
                if (data.type === 'vehicle_update' && unityInstance) {
                    // Unityにメッセージを送信
                    var message = JSON.stringify({
                        name: data.path,
                        action: data.value.toString(),
                        options: ''
                    });
                    unityInstance.SendMessage("CarController", "ControlComponent", message);
                }
            };

            function controlDoor(path, isOpen) {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'set_value',
                        path: path,
                        value: isOpen
                    }));
                }
            }

            function controlLight(path, isOn) {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'set_value',
                        path: path,
                        value: isOn
                    }));
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            # 保留中のメッセージを送信
            pending_messages = connection_manager.get_pending_messages()
            for message in pending_messages:
                await websocket.send_text(message)
            
            # 新しいメッセージを待機
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "set_value":
                path = message.get("path")
                value = message.get("value")
                
                if path and value is not None:
                    success = vehicle_state.set_value(path, value)
                    if success:
                        # 他のクライアントに通知
                        await connection_manager.broadcast(json.dumps({
                            "type": "vehicle_update",
                            "path": path,
                            "value": value
                        }))
                        
                        # Unityに直接通知
                        if 'unityInstance' in globals():
                            unity_message = json.dumps({
                                "name": path,
                                "action": str(value),
                                "options": ""
                            })
                            # ここでUnityインスタンスにメッセージを送信
                    
                    await websocket.send_text(json.dumps({
                        "type": "response",
                        "success": success,
                        "path": path,
                        "value": value
                    }))
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

@app.get("/FromUnity.js")
async def from_unity_js():
    return FileResponse("FromUnity.js", media_type="application/javascript")

def serve_grpc():
    """gRPCサーバーを起動"""
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    val_pb2_grpc.add_VALServicer_to_server(
        VALServicer(vehicle_state, connection_manager), 
        server
    )
    
    # gRPCサーバーをポート50051で起動
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    server.start()
    logger.info(f"gRPCサーバーが起動しました: {listen_addr}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)

async def main():
    """メイン関数"""
    # gRPCサーバーを別スレッドで起動
    import threading
    grpc_thread = threading.Thread(target=serve_grpc, daemon=True)
    grpc_thread.start()
    
    # FastAPIサーバーを起動
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main()) 