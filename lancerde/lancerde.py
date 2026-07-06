# lancerde — Exporté depuis TkLearn Studio
# =============================================
import tkinter as tk
from tkinter import ttk

# Créer la fenêtre principale
window = tk.Tk()
window.title("lancerde")
window.geometry("600x500")
window.configure(bg="#1a1a2e")

# 'root' est un Frame dans la fenêtre (comme dans TkLearn Studio)
root = tk.Frame(window, bg="#1a1a2e")
root.pack(fill=tk.BOTH, expand=True)

# ── Code de l'application ──
# === Lanceur de Dés — Multi-dés avec statistiques et histogramme ===
import tkinter as tk
import random

canvas = tk.Canvas(root, width=460, height=440, bg="#16213e", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# ── État ──
history = []
freq = {}  # fréquence des totaux
num_dice = [2]
animating = [False]

canvas.create_text(230, 22, text="Lanceur de Des", font=("Georgia", 16, "bold"), fill="#64b5f6")

# ── Dessiner un dé avec points réalistes ──
def draw_die(cx, cy, value, size=55):
    s = size
    # Ombre
    canvas.create_rectangle(cx-s+3, cy-s+5, cx+s+3, cy+s+5, fill="#0d1117", outline="", tag="dice")
    # Corps du dé avec coins arrondis (simulé)
    canvas.create_rectangle(cx-s, cy-s, cx+s, cy+s, fill="#f8f8f8", outline="#bbb", width=2, tag="dice")
    # Cadre interne
    canvas.create_rectangle(cx-s+4, cy-s+4, cx+s-4, cy+s-4, fill="#ffffff", outline="#ddd", width=1, tag="dice")
    # Points
    DOT_POS = {
        1: [(0,0)], 2: [(-1,-1),(1,1)], 3: [(-1,-1),(0,0),(1,1)],
        4: [(-1,-1),(1,-1),(-1,1),(1,1)], 5: [(-1,-1),(1,-1),(0,0),(-1,1),(1,1)],
        6: [(-1,-1),(1,-1),(-1,0),(1,0),(-1,1),(1,1)]
    }
    dot_r = 7
    for dx, dy in DOT_POS.get(value, []):
        x, y = cx + dx * (s*0.52), cy + dy * (s*0.52)
        # Point avec dégradé simulé
        canvas.create_oval(x-dot_r-1, y-dot_r-1, x+dot_r+1, y+dot_r+1, fill="#333", outline="", tag="dice")
        canvas.create_oval(x-dot_r, y-dot_r, x+dot_r, y+dot_r, fill="#e74c3c", outline="#c0392b", width=1, tag="dice")
        canvas.create_oval(x-dot_r+2, y-dot_r+2, x+dot_r-3, y+dot_r-3, fill="#ff6b6b", outline="", tag="dice")

# ── Histogramme des fréquences ──
def draw_histogram():
    canvas.delete("hist")
    if not freq:
        return
    max_f = max(freq.values())
    bar_area_y = 290
    bar_h_max = 100
    min_val = num_dice[0]
    max_val = num_dice[0] * 6
    count = max_val - min_val + 1
    bar_w = min(30, 380 // max(count, 1))
    start_x = 230 - (count * bar_w) // 2
    for i, val in enumerate(range(min_val, max_val+1)):
        f = freq.get(val, 0)
        bh = (f / max_f * bar_h_max) if max_f > 0 else 0
        x = start_x + i * bar_w
        # Barre
        color = "#3949ab" if f < max_f else "#6bff6b"
        canvas.create_rectangle(x+1, bar_area_y+bar_h_max-bh, x+bar_w-1, bar_area_y+bar_h_max,
                               fill=color, outline="#1a1a2e", tag="hist")
        # Label
        canvas.create_text(x+bar_w//2, bar_area_y+bar_h_max+12, text=str(val),
                          font=("Arial", 7), fill="#888", tag="hist")
        if f > 0:
            canvas.create_text(x+bar_w//2, bar_area_y+bar_h_max-bh-10, text=str(f),
                              font=("Arial", 7), fill="#aaa", tag="hist")
    canvas.create_text(230, bar_area_y+bar_h_max+30, text=f"Lancers: {len(history)}  |  Moyenne: {sum(history)/len(history):.1f}",
                      font=("Arial", 10), fill="#888", tag="hist")

# ── Animation de lancer ──
def roll(step=0):
    if step < 10:
        canvas.delete("dice")
        positions = [(140, 150), (320, 150), (230, 150)]
        for i in range(num_dice[0]):
            cx, cy = positions[i] if i < len(positions) else (140 + i*90, 150)
            draw_die(cx, cy, random.randint(1, 6))
        root.after(70, roll, step + 1)
    else:
        canvas.delete("dice")
        values = []
        positions = [(140, 150), (320, 150), (230, 150)]
        for i in range(num_dice[0]):
            v = random.randint(1, 6)
            values.append(v)
            cx, cy = positions[i] if i < len(positions) else (140 + i*90, 150)
            draw_die(cx, cy, v)
        total = sum(values)
        history.append(total)
        freq[total] = freq.get(total, 0) + 1
        canvas.delete("result")
        canvas.create_text(230, 225, text=f"Total : {total}", font=("Arial", 16, "bold"), fill="#6bff6b", tag="result")
        draw_histogram()
        animating[0] = False

def on_roll(e=None):
    if not animating[0]:
        animating[0] = True
        roll()

canvas.bind("<Button-1>", on_roll)

# ── Boutons nombre de dés ──
btn_frame = tk.Frame(root, bg="#16213e")
btn_frame.pack(pady=3)
tk.Label(btn_frame, text="Nombre de des:", font=("Arial", 10), bg="#16213e", fg="#888").pack(side=tk.LEFT, padx=5)
for n in [1, 2, 3]:
    def set_n(v=n):
        num_dice[0] = v
        history.clear()
        freq.clear()
        canvas.delete("dice", "result", "hist")
    tk.Button(btn_frame, text=str(n), font=("Arial", 10, "bold"), bg="#3949ab", fg="white",
              width=3, bd=0, cursor="hand2", command=set_n).pack(side=tk.LEFT, padx=2)

canvas.create_text(230, 430, text="Cliquez sur le canvas pour lancer", font=("Arial", 9), fill="#555")



# ── Boucle principale ──
window.mainloop()
