# mon_application — Exporté depuis TkLearn Studio
# =============================================
import tkinter as tk
from tkinter import ttk

# Créer la fenêtre principale
window = tk.Tk()
window.title("mon_application")
window.geometry("600x500")
window.configure(bg="#1a1a2e")

# 'root' est un Frame dans la fenêtre (comme dans TkLearn Studio)
root = tk.Frame(window, bg="#1a1a2e")
root.pack(fill=tk.BOTH, expand=True)

# ── Code de l'application ──
# === Snake — Obstacles, particules, vitesse croissante, score ===
import tkinter as tk
import random

canvas = tk.Canvas(root, width=460, height=420, bg="#0a0a1a", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

CELL = 18
COLS = 460 // CELL
ROWS = (420 - 40) // CELL
OFFSET_Y = 40
snake = [(COLS//2, ROWS//2)]
direction = ["Right"]
food = [None]
obstacles = []
score = [0]
high_score = [0]
speed = [120]
game_running = [False]
particles = []

# ── Couleurs ──
SNAKE_HEAD = "#6bff6b"
SNAKE_BODY = "#27ae60"
FOOD_COLOR = "#ff6b6b"
OBSTACLE_COLOR = "#555577"

canvas.create_text(230, 18, text="Snake", font=("Georgia", 14, "bold"), fill="#6bff6b")
score_text = canvas.create_text(120, 18, text="Score: 0", font=("Arial", 10), fill="#888")
hs_text = canvas.create_text(350, 18, text="Best: 0", font=("Arial", 10), fill="#555")

def spawn_food():
    while True:
        pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
        if pos not in snake and pos not in obstacles:
            food[0] = pos
            return

def spawn_obstacles(count=5):
    obstacles.clear()
    for _ in range(count):
        while True:
            pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if pos not in snake and pos != food[0]:
                obstacles.append(pos)
                break

def add_particles(x, y, color, count=6):
    for _ in range(count):
        dx = random.uniform(-3, 3)
        dy = random.uniform(-3, 3)
        life = random.randint(5, 12)
        particles.append([x, y, dx, dy, life, color])

def draw():
    canvas.delete("game")
    # Grille subtile
    for r in range(ROWS):
        for c in range(COLS):
            if (r + c) % 2 == 0:
                x, y = c * CELL, OFFSET_Y + r * CELL
                canvas.create_rectangle(x, y, x+CELL, y+CELL, fill="#0d0d1f", outline="", tag="game")

    # Obstacles
    for ox, oy in obstacles:
        x, y = ox * CELL, OFFSET_Y + oy * CELL
        canvas.create_rectangle(x+1, y+1, x+CELL-1, y+CELL-1, fill=OBSTACLE_COLOR, outline="#444", tag="game")

    # Nourriture (pulsation)
    if food[0]:
        fx, fy = food[0]
        x, y = fx * CELL + CELL//2, OFFSET_Y + fy * CELL + CELL//2
        r = CELL//2 - 1
        canvas.create_oval(x-r-2, y-r-2, x+r+2, y+r+2, fill="#ff4444", outline="", tag="game")
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=FOOD_COLOR, outline="", tag="game")
        canvas.create_oval(x-r+3, y-r+3, x-1, y-1, fill="#ff9999", outline="", tag="game")

    # Serpent
    for i, (sx, sy) in enumerate(snake):
        x, y = sx * CELL, OFFSET_Y + sy * CELL
        if i == 0:
            canvas.create_rectangle(x+1, y+1, x+CELL-1, y+CELL-1, fill=SNAKE_HEAD, outline="#1a1a2e", tag="game")
            # Yeux
            canvas.create_oval(x+3, y+3, x+7, y+7, fill="#000", outline="", tag="game")
            canvas.create_oval(x+CELL-7, y+3, x+CELL-3, y+7, fill="#000", outline="", tag="game")
        else:
            shade = max(30, 100 - i * 5)
            color = f"#00{shade:02x}00"
            try:
                canvas.create_rectangle(x+1, y+1, x+CELL-1, y+CELL-1, fill=color, outline="#0a0a1a", tag="game")
            except Exception:
                canvas.create_rectangle(x+1, y+1, x+CELL-1, y+CELL-1, fill=SNAKE_BODY, outline="#0a0a1a", tag="game")

    # Particules
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 1
        if p[4] <= 0:
            particles.remove(p)
        else:
            sz = max(1, p[4] // 3)
            canvas.create_oval(p[0]-sz, p[1]-sz, p[0]+sz, p[1]+sz, fill=p[5], outline="", tag="game")

    canvas.itemconfig(score_text, text=f"Score: {score[0]}")
    canvas.itemconfig(hs_text, text=f"Best: {high_score[0]}")

def move():
    if not game_running[0]:
        return
    hx, hy = snake[0]
    d = direction[0]
    if d == "Up": hy -= 1
    elif d == "Down": hy += 1
    elif d == "Left": hx -= 1
    elif d == "Right": hx += 1

    # Traverser les murs
    hx %= COLS
    hy %= ROWS

    new_head = (hx, hy)

    # Collision avec soi-même ou obstacle
    if new_head in snake[1:] or new_head in obstacles:
        game_over()
        return

    snake.insert(0, new_head)

    # Manger
    if new_head == food[0]:
        score[0] += 10
        add_particles(hx * CELL + CELL//2, OFFSET_Y + hy * CELL + CELL//2, "#ffd700", 10)
        spawn_food()
        # Augmenter vitesse
        speed[0] = max(50, speed[0] - 2)
        # Ajouter obstacles tous les 50 points
        if score[0] % 50 == 0 and score[0] > 0:
            spawn_obstacles(3 + score[0] // 50)
    else:
        snake.pop()

    draw()
    root.after(speed[0], move)

def game_over():
    game_running[0] = False
    if score[0] > high_score[0]:
        high_score[0] = score[0]
    add_particles(snake[0][0]*CELL+CELL//2, OFFSET_Y+snake[0][1]*CELL+CELL//2, "#ff0000", 20)
    draw()
    canvas.create_text(230, 220, text=f"Game Over\nScore: {score[0]}", font=("Arial", 18, "bold"),
                      fill="#ff6b6b", tag="game", justify="center")
    canvas.create_text(230, 280, text="Espace pour rejouer", font=("Arial", 10), fill="#888", tag="game")

def start():
    snake.clear()
    snake.append((COLS//2, ROWS//2))
    direction[0] = "Right"
    score[0] = 0
    speed[0] = 120
    particles.clear()
    game_running[0] = True
    spawn_obstacles(5)
    spawn_food()
    draw()
    move()

def on_key(event):
    if event.keysym == "space":
        if not game_running[0]:
            start()
        return
    opposites = {"Up":"Down","Down":"Up","Left":"Right","Right":"Left"}
    if event.keysym in opposites and event.keysym != opposites.get(direction[0]):
        direction[0] = event.keysym

canvas.bind("<Key>", on_key)
canvas.focus_set()

canvas.create_text(230, 200, text="SNAKE", font=("Georgia", 28, "bold"), fill="#6bff6b")
canvas.create_text(230, 240, text="Espace pour commencer\nFleches pour diriger", font=("Arial", 10), fill="#888", justify="center")



# ── Boucle principale ──
window.mainloop()
