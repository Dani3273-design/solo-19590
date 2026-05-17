# 滑动拼图游戏

一个基于 Python 和 Pygame 开发的 6x6 滑动拼图游戏。

## 功能特性

- 🎮 随机生成像素风格拼图图片
- 🖱️ 鼠标拖拽操作，流畅的移动动画
- ⏱️ 实时计时和步数统计
- ✅ 拼图完成自动检测（子线程处理，不卡顿）
- 🏆 结算页面展示成绩
- 🎨 美观的 UI 界面，支持中文显示

## 技术栈

- Python 3.9+
- Pygame 2.5+
- Pillow 10.0+

## 项目结构

```
main/
├── game/                    # 游戏核心模块
│   ├── __init__.py
│   ├── puzzle.py           # 拼图生成、打乱、验证
│   ├── control.py          # 鼠标控制、移动动画
│   ├── ui.py               # UI界面、按钮、渲染
│   └── count.py            # 计时、记步
├── main.py                  # 游戏入口
├── requirements.txt         # 依赖文件
└── README.md               # 项目说明
```

## 模块说明

### [puzzle.py](file:///Users/yiigaa/work/solo-19591/main/game/puzzle.py)
- `PuzzleGenerator` 类：负责生成随机像素图片
- 将图片分割为 6x6 的拼图块
- 确保每个拼图块独一无二且非全白
- 可解性验证的随机打乱算法
- 拼图完成状态检测

### [control.py](file:///Users/yiigaa/work/solo-19591/main/game/control.py)
- `PuzzleController` 类：处理鼠标交互
- 拼图拖拽操作
- 平滑移动动画（缓动效果）
- 相邻空位检测

### [ui.py](file:///Users/yiigaa/work/solo-19591/main/game/ui.py)
- `UIManager` 类：界面渲染管理
- `Button` 类：可交互按钮组件
- 开始页面、游戏页面、结算页面
- 中文字体加载（支持多系统）

### [count.py](file:///Users/yiigaa/work/solo-19591/main/game/count.py)
- `GameCounter` 类：游戏数据统计
- 独立线程计时，不阻塞 UI
- 步数统计
- 时间格式化

### [main.py](file:///Users/yiigaa/work/solo-19591/main/main.py)
- `PuzzleGame` 类：游戏主控制器
- 多线程架构：UI 主线程 + 检测子线程
- 游戏状态管理（开始/游戏中/结算）
- 事件循环

## 安装和运行

### 安装依赖

```bash
cd main
pip install -r requirements.txt
```

### 运行游戏

```bash
python main.py
```

## 游戏玩法

1. 点击「开始游戏」按钮进入游戏
2. 使用鼠标按住并拖动与空位相邻的拼图块
3. 将拼图拖向空位方向，松开即可移动
4. 目标是将所有拼图块恢复到正确位置
5. 完成后会显示用时和步数统计
6. 点击「再来一局」开始新游戏

## 设计亮点

- **多线程架构**：计时和完成检测在子线程运行，确保 UI 流畅
- **缓动动画**：拼图移动采用 ease-in-out 缓动函数，视觉效果自然
- **可解性保证**：打乱算法确保生成的拼图一定有解
- **跨平台字体**：自动检测系统中文字体，避免乱码
- **拼图唯一性**：通过哈希检测确保每块拼图独一无二
