# 3D Car Control Server

Unity WebGLビルドを使用した3D車両制御システムです。gRPCサーバーとWebインターフェースを統合し、KUKSA VALプロトコルに基づく車両制御APIを提供します。

## 機能

- **Unity WebGL統合**: `Build/widget-3d-car-unity.loader.js`を使用してブラウザに3D車両を表示
- **gRPCサーバー**: KUKSA VALプロトコルに基づく車両制御API
- **WebSocket通信**: リアルタイムでの車両状態更新
- **Webインターフェース**: ブラウザベースの制御パネル

## 技術スタック

- **Python**: メインサーバー実装
- **gRPC**: 車両制御API
- **FastAPI**: Webサーバー
- **WebSocket**: リアルタイム通信
- **Unity WebGL**: 3D車両表示
- **Protocol Buffers**: KUKSA VALプロトコル

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. Protocol Buffersファイルの生成

```bash
python generate_proto.py
```

### 3. サーバーの起動

```bash
python car_control_server.py
```

サーバーは以下のポートで起動します：
- **Webサーバー**: http://localhost:8000
- **gRPCサーバー**: localhost:50051

## 使用方法

### Webインターフェース

1. ブラウザで http://localhost:8000 にアクセス
2. Unity WebGLビルドが読み込まれ、3D車両が表示されます
3. 右上の制御パネルから車両を操作できます

### gRPC API

gRPCクライアントの使用例：

```bash
python grpc_client_example.py
```

### サポートされている車両制御

#### ドア制御
- `Vehicle.Cabin.Door.Row1.DriverSide.IsOpen` (boolean)
- `Vehicle.Cabin.Door.Row1.DriverSide.IsLocked` (boolean)
- `Vehicle.Cabin.Door.Row1.DriverSide.Position` (uint8)

#### ライト制御
- `Vehicle.Body.Lights.Beam.High.IsOn` (boolean)
- `Vehicle.Body.Lights.Beam.Low.IsOn` (boolean)
- `Vehicle.Body.Lights.Brake.IsActive` (boolean)
- `Vehicle.Body.Lights.Hazard.IsSignaling` (boolean)

#### シート制御
- `Vehicle.Cabin.Seat.Row1.DriverSide.Position` (uint8)
- `Vehicle.Cabin.Seat.Row1.DriverSide.Height` (uint8)

#### トランク制御
- `Vehicle.Body.Trunk.Front.IsOpen` (boolean)
- `Vehicle.Body.Trunk.Rear.IsOpen` (boolean)

#### その他
- `Vehicle.AverageSpeed` (float)
- `Vehicle.Body.Windshield.Front.Wiping.Mode` (string)

## API仕様

### gRPCサービス

KUKSA VALプロトコルに基づく以下のサービスを提供：

- `Get`: 車両データの取得
- `Set`: 車両データの設定
- `Subscribe`: 車両データの購読
- `GetServerInfo`: サーバー情報の取得

### WebSocket API

リアルタイム通信のためのWebSocketエンドポイント：

- **接続**: `ws://localhost:8000/ws`
- **メッセージ形式**: JSON

```json
{
  "type": "set_value",
  "path": "Vehicle.Cabin.Door.Row1.DriverSide.IsOpen",
  "value": true
}
```

## プロジェクト構造

```
widget-3d-car-unity/
├── car_control_server.py      # メインサーバー
├── generate_proto.py          # Protocol Buffers生成スクリプト
├── grpc_client_example.py     # gRPCクライアント例
├── requirements.txt           # Python依存関係
├── kuksa_val_v1/             # 生成されたProtocol Buffers
├── proto/                    # Protocol Buffers定義
│   └── kuksa/val/v1/
│       ├── val.proto
│       └── types.proto
├── Build/                    # Unity WebGLビルド
└── TemplateData/             # Unityテンプレートデータ
```

## 開発

### 新しい車両制御の追加

1. `car_control_server.py`の`VehicleState`クラスに新しいパスを追加
2. メタデータを定義
3. Unity側で対応するコンポーネントを実装

### カスタマイズ

- **ポート変更**: `car_control_server.py`のポート設定を変更
- **車両モデル**: Unityプロジェクトで新しい3Dモデルを使用
- **API拡張**: KUKSA VALプロトコルに基づいて新しいAPIを追加

## トラブルシューティング

### Unity WebGLが読み込まれない

1. `Build/`ディレクトリにUnity WebGLファイルが存在することを確認
2. ブラウザのコンソールでエラーメッセージを確認
3. Webサーバーが正しく起動していることを確認

### gRPC接続エラー

1. gRPCサーバーがポート50051で起動していることを確認
2. ファイアウォール設定を確認
3. Protocol Buffersファイルが正しく生成されていることを確認

## ライセンス

このプロジェクトはApache License 2.0の下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。

# List APIs:

## Group 1: Speed & Wiper & Trunk
```
Vehicle.AverageSpeed
Vehicle.Body.Windshield.Front.Wiping.Mode
Vehicle.Body.Windshield.Rear.Wiping.Mode
Vehicle.Body.Trunk.Front.IsLocked
Vehicle.Body.Trunk.Front.IsOpen
Vehicle.Body.Trunk.Front.Position
Vehicle.Body.Trunk.Front.IsLightOn
Vehicle.Body.Trunk.Rear.IsLocked
Vehicle.Body.Trunk.Rear.IsOpen
Vehicle.Body.Trunk.Rear.Position
Vehicle.Body.Trunk.Rear.IsLightOn
```

## Group 2: Row1: Door & Seat & Window
```
Vehicle.Cabin.Door.Row1.DriverSide.IsLocked
Vehicle.Cabin.Door.Row1.DriverSide.IsOpen
Vehicle.Cabin.Door.Row1.DriverSide.Position
Vehicle.Cabin.Door.Row1.DriverSide.Window.IsOpen
Vehicle.Cabin.Door.Row1.DriverSide.Window.Position
Vehicle.Cabin.Seat.Row1.DriverSide.Position
Vehicle.Cabin.Seat.Row1.DriverSide.Height

Vehicle.Cabin.Door.Row1.PassengerSide.IsLocked
Vehicle.Cabin.Door.Row1.PassengerSide.IsOpen
Vehicle.Cabin.Door.Row1.PassengerSide.Position
Vehicle.Cabin.Door.Row1.PassengerSide.Window.IsOpen
Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position
Vehicle.Cabin.Seat.Row1.PassengerSide.Position
Vehicle.Cabin.Seat.Row1.PassengerSide.Height
```

## Group 3: Row2 Door & Seat & Window
```
Vehicle.Cabin.Door.Row2.DriverSide.IsLocked
Vehicle.Cabin.Door.Row2.DriverSide.IsOpen
Vehicle.Cabin.Door.Row2.DriverSide.Position
Vehicle.Cabin.Door.Row2.DriverSide.Window.IsOpen
Vehicle.Cabin.Door.Row2.DriverSide.Window.Position
Vehicle.Cabin.Seat.Row2.DriverSide.Position
Vehicle.Cabin.Seat.Row2.DriverSide.Height

Vehicle.Cabin.Door.Row2.PassengerSide.IsLocked
Vehicle.Cabin.Door.Row2.PassengerSide.IsOpen
Vehicle.Cabin.Door.Row2.PassengerSide.Position
Vehicle.Cabin.Door.Row2.PassengerSide.Window.IsOpen
Vehicle.Cabin.Door.Row2.PassengerSide.Window.Position
Vehicle.Cabin.Seat.Row2.PassengerSide.Position
Vehicle.Cabin.Seat.Row2.PassengerSide.Height
```

## Group 4: Lights & Mirrors
```
Vehicle.Body.Lights.Beam.High.IsOn
Vehicle.Body.Lights.Beam.Low.IsOn
Vehicle.Body.Lights.Brake.IsActive
Vehicle.Body.Lights.Hazard.IsSignaling
Vehicle.Body.Lights.LicensePlate.IsOn
Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Color
Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.IsLightOn
Vehicle.Cabin.Light.AmbientLight.Row1.PassengerSide.Color
Vehicle.Cabin.Light.AmbientLight.Row1.PassengerSide.IsLightOn
Vehicle.Body.Mirrors.DriverSide.IsFolded
Vehicle.Body.Mirrors.DriverSide.IsLocked
Vehicle.Body.Mirrors.PassengerSide.IsFolded
Vehicle.Body.Mirrors.PassengerSide.IsLocked
```


# Instruction: 
For example:
```js
let OBJECT_MAPPING = [
  {
    // The name of the Unity object to be controlled
    entity: 'row1_door1',

    // Placeholder for additional behavior (e.g., "islocked" status check)
    behaviour: "",

    // The key or field name in the browser used to control this feature
    optionsName: 'row1_door1_open',

    // The default API path used to retrieve this object's state
    api: 'Vehicle.Cabin.Door.Row1.Driver.IsOpen',

    // The data type expected from the API or browser (in this case, true/false)
    dataType: "boolean",

    // Last known value to prevent unnecessary updates
    lastValue: false,

    // Maps the boolean value from browser or API to corresponding action in Unity
    actionMaps: {
      "true": "true",   // "true" from browser/API triggers Unity action "true"
      "false": "false"  // "false" from browser/API triggers Unity action "false"
    }
  },
  // ...
];
```


# Unity 2022.3.7f1 Setup Guide with WebGL Build

## ✅ Requirements

- Unity Hub (latest version)
- Unity Editor version **2022.3.7f1**
- WebGL Build Support Module

---

## 📥 Step 1: Install Unity Hub

1. Download Unity Hub from the official site: [https://unity.com/download](https://unity.com/download)
2. Install and open Unity Hub.

---

## 🧱 Step 2: Install Unity 2022.3.7f1

1. Open Unity Hub and go to the **Installs** tab.
2. Click **"Install Editor"**, then go to the **"Archive"** section.
3. Find and download the version [Unity 2022.3.7f1](https://unity.com/releases/editor/qa/lts-releases).
4. Download the **.unityhub** install file and open it to install via Unity Hub.

> ✅ **Make sure to select "WebGL Build Support" during installation.**

If you've already installed Unity without WebGL:
- Go to **Installs** tab → click **⋮** next to version 2022.3.7f1 → select **"Add Modules"** → install **WebGL Build Support**.

---

## 🎮 Step 3: Create a New Unity Project

1. Go to the **Projects** tab → click **"New Project"**.
2. Choose the **3D** template.
3. Select version **2022.3.7f1**.
4. Name your project and click **Create**.

---

## ⚙️ Step 4: Configure WebGL Build

1. Open your project.
2. Go to **File → Build Settings**.
3. Select **WebGL** in the platform list → click **Switch Platform**.

### Optional Player Settings:
- Go to **Player Settings**:
  - **Resolution and Presentation**:
    - Set Canvas Width/Height as needed.
    - Enable **Run In Background** if required.
  - **Publishing Settings**:
    - Set Compression Format to **Brotli** or **Gzip**.
    - Enable **Decompression Fallback** for better compatibility.

---

## 🚀 Step 5: Build the Project

1. Add your main scene in **Build Settings** → click **Add Open Scenes**.
2. Click **Build**, then choose a folder (e.g., `Build/`) to export the WebGL files.

> The output will include files like:
## 🧪 Testing the Build

To test the WebGL build locally, use a local server:

### Option 1: Live Server (VS Code extension)
- Install the **Live Server** extension.
- Right-click `MainIndex.html` → **Open with Live Server**.

## 🧱 Project Code Structure

This project is a WebGL-based Unity application that controls a 3D car model. The car has various interactive features such as opening/closing doors, turning lights on/off, and adjusting seat positions. All functionalities are encapsulated and managed by a centralized controller.

### 🏗 Code Architecture


### 🔁 Flow Overview

1. Individual car parts (door, seat, lights...) are modular scripts.
2. `CarController` acts as the integration hub that references all parts.
3. External HTML communicates with Unity WebGL through JavaScript API calls.
4. Unity receives commands (as JSON or strings) and forwards them to the appropriate component.
5. Each component implements a shared interface for consistent communication (`IActions`, `ILockable`, etc).

### 🧩 Key Features

- Modular component design for easy expansion.
- Centralized command processing via `CarController`.
- HTML integration for remote or UI-based control.
- Interface-driven architecture for flexibility.

---



