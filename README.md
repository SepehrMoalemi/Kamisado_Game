# Kamisado GUI in Python

A Python code to play [Kamisado](https://www.yucata.de/en/Rules/Kamisado) with a friend!

## ▶️ Installation
### 0. Create a Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate    # On macOS/Linux
venv\Scripts\activate.bat   # On Windows
```

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Game

```bash
python main.py
```

---

## 🧾 Requirements

- Python 3.7 or newer
- `pygame` version 2.0 or newer

---

## 📁 Project Structure

```
.
├── main.py             # Game settings
├── game.py             # Game logic (rules, turns, win condition)
└── board.py            # GUI rendering with Pygame
```

---

## 🛠 Features

- Fully playable 2-player Kamisado
- Drag-and-drop **and** click-to-move support
- Enforced piece selection by square color
- Highlighting for legal moves and selected pieces
- Multiple piece rendering styles (circle and rook)