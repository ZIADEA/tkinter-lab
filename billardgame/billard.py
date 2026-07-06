import tkinter as tk
import math
import random

# ─── Constantes ───────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1000, 600
TABLE_X1, TABLE_Y1 = 60, 60
TABLE_X2, TABLE_Y2 = 940, 540
RAIL = 30
PLAY_X1 = TABLE_X1 + RAIL
PLAY_Y1 = TABLE_Y1 + RAIL
PLAY_X2 = TABLE_X2 - RAIL
PLAY_Y2 = TABLE_Y2 - RAIL
CX = (PLAY_X1 + PLAY_X2) / 2
CY = (PLAY_Y1 + PLAY_Y2) / 2

BALL_RADIUS = 12
FRICTION = 0.984
MIN_SPEED = 0.12
POCKET_RADIUS = 18
MAX_POWER = 24
SUBSTEPS = 3          # sous-étapes physiques par frame

FELT_COLOR   = "#1a6b3c"
FELT_DARK    = "#155a32"
RAIL_COLOR   = "#6b3a1f"
RAIL_DARK    = "#3d2010"
RAIL_HIGH    = "#8b5a2f"
CLOTH_LINE   = "#1d7a45"
CUE_COLOR    = "#d4a853"
POCKET_COLOR = "#080808"
BG_COLOR     = "#1a1008"
SCORE_BG     = "#0d0d0d"
DIAMOND_COLOR = "#d4a853"

BALL_COLORS = {
    0:  ("white",   "#e0e0e0", ""),
    1:  ("#f5c518", "#d4a800", "1"),
    2:  ("#1a3fa6", "#1530a0", "2"),
    3:  ("#cc2200", "#aa1500", "3"),
    4:  ("#7b2fa6", "#5b1090", "4"),
    5:  ("#e05810", "#c04500", "5"),
    6:  ("#1a8a30", "#0f6820", "6"),
    7:  ("#8b2020", "#701515", "7"),
    8:  ("#1a1a1a", "#000000", "8"),
    9:  ("#f5c518", "#d4a800", "9"),
    10: ("#1a3fa6", "#1530a0", "10"),
    11: ("#cc2200", "#aa1500", "11"),
    12: ("#7b2fa6", "#5b1090", "12"),
    13: ("#e05810", "#c04500", "13"),
    14: ("#1a8a30", "#0f6820", "14"),
    15: ("#8b2020", "#701515", "15"),
}

POCKETS = [
    (PLAY_X1 + 2,  PLAY_Y1 + 2),
    (CX,           PLAY_Y1 - 4),
    (PLAY_X2 - 2,  PLAY_Y1 + 2),
    (PLAY_X1 + 2,  PLAY_Y2 - 2),
    (CX,           PLAY_Y2 + 4),
    (PLAY_X2 - 2,  PLAY_Y2 - 2),
]


# ─── Bille ────────────────────────────────────────────────────────────────────
class Ball:
    __slots__ = ("num", "x", "y", "vx", "vy", "potted",
                 "color", "shade", "label", "striped")

    def __init__(self, num, x, y):
        self.num = num
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.potted = False
        self.color, self.shade, self.label = BALL_COLORS[num]
        self.striped = num >= 9

    @property
    def speed(self):
        return math.hypot(self.vx, self.vy)

    def move(self, dt=1.0):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= FRICTION
        self.vy *= FRICTION
        if self.speed < MIN_SPEED:
            self.vx = self.vy = 0.0

    def bounce_walls(self):
        r = BALL_RADIUS
        if self.x - r < PLAY_X1:
            self.x = PLAY_X1 + r
            self.vx = abs(self.vx) * 0.82
        elif self.x + r > PLAY_X2:
            self.x = PLAY_X2 - r
            self.vx = -abs(self.vx) * 0.82
        if self.y - r < PLAY_Y1:
            self.y = PLAY_Y1 + r
            self.vy = abs(self.vy) * 0.82
        elif self.y + r > PLAY_Y2:
            self.y = PLAY_Y2 - r
            self.vy = -abs(self.vy) * 0.82

    def check_pocket(self):
        for px, py in POCKETS:
            if math.hypot(self.x - px, self.y - py) < POCKET_RADIUS + BALL_RADIUS * 0.4:
                self.potted = True
                self.vx = self.vy = 0.0
                return True
        return False


# ─── Jeu ──────────────────────────────────────────────────────────────────────
class BillardGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Billard 8-Ball")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT)

        self._build_sidebar()
        self._init_game()

        self.canvas.bind("<Motion>",          self._on_move)
        self.canvas.bind("<ButtonPress-1>",   self._on_press)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        self._loop()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        side = tk.Frame(self.root, bg=SCORE_BG, width=220)
        side.pack(side=tk.RIGHT, fill=tk.Y)
        side.pack_propagate(False)

        tk.Label(side, text="BILLARD", font=("Georgia", 20, "bold"),
                 bg=SCORE_BG, fg="#d4a853").pack(pady=(20, 2))
        tk.Label(side, text="8-Ball Pool", font=("Georgia", 10, "italic"),
                 bg=SCORE_BG, fg="#777").pack(pady=(0, 14))

        self._sep(side)

        # Joueurs
        for i, name in enumerate(["Joueur 1", "Joueur 2"], 1):
            f = tk.Frame(side, bg=SCORE_BG)
            f.pack(fill=tk.X, padx=16, pady=6)
            lbl = tk.Label(f, text=name, font=("Georgia", 12, "bold"),
                           bg=SCORE_BG, fg="#ccc", anchor="w")
            lbl.pack(side=tk.LEFT)
            grp_lbl = tk.Label(f, text="", font=("Georgia", 9),
                               bg=SCORE_BG, fg="#999", anchor="e")
            grp_lbl.pack(side=tk.RIGHT, padx=(4, 0))
            score_lbl = tk.Label(f, text="0", font=("Courier", 14, "bold"),
                                 bg=SCORE_BG, fg="#d4a853", width=3)
            score_lbl.pack(side=tk.RIGHT)
            setattr(self, f"p{i}_label", lbl)
            setattr(self, f"p{i}_score_lbl", score_lbl)
            setattr(self, f"p{i}_grp_lbl", grp_lbl)

        self._sep(side)

        # Tour
        tk.Label(side, text="Tour :", font=("Georgia", 10),
                 bg=SCORE_BG, fg="#aaa").pack(pady=(8, 0))
        self.turn_lbl = tk.Label(side, text="Joueur 1",
                                 font=("Georgia", 13, "bold"),
                                 bg=SCORE_BG, fg="#4fc3f7")
        self.turn_lbl.pack()

        self._sep(side)

        # Puissance
        tk.Label(side, text="Puissance", font=("Georgia", 10),
                 bg=SCORE_BG, fg="#aaa").pack()
        self.power_canvas = tk.Canvas(side, width=170, height=20,
                                      bg="#222", highlightthickness=1,
                                      highlightbackground="#444")
        self.power_canvas.pack(pady=4)

        self._sep(side)

        # Billes restantes
        tk.Label(side, text="Restantes", font=("Georgia", 9),
                 bg=SCORE_BG, fg="#777").pack(pady=(6, 2))
        self.remaining_canvas = tk.Canvas(side, width=180, height=50,
                                          bg="#111", highlightthickness=0)
        self.remaining_canvas.pack()

        self._sep(side)

        # Status
        self.status_lbl = tk.Label(side, text="Visez et tirez !",
                                   font=("Georgia", 10, "italic"),
                                   bg=SCORE_BG, fg="#aaa",
                                   wraplength=180, justify=tk.CENTER)
        self.status_lbl.pack(pady=6, padx=10)

        self._sep(side)

        btn = tk.Button(side, text="Nouvelle Partie",
                        font=("Georgia", 11, "bold"),
                        bg="#d4a853", fg="#1a1008", activebackground="#c09840",
                        relief=tk.FLAT, cursor="hand2",
                        command=self._new_game, padx=14, pady=8)
        btn.pack(pady=8)

    @staticmethod
    def _sep(parent):
        tk.Frame(parent, bg="#333", height=1).pack(fill=tk.X, padx=16, pady=6)

    # ── Init ──────────────────────────────────────────────────────────────────
    def _init_game(self):
        self.balls = []
        self.shooting = False
        self.aiming = False
        self.placing_cue = False       # mode placement bille blanche
        self.mouse_x = CX
        self.mouse_y = CY + 120
        self.drag_start = None
        self.power = 0.0
        self.scores = [0, 0]
        self.turn = 0                  # 0 = J1, 1 = J2
        self.groups = [None, None]     # "pleines" / "rayees"
        self.game_over = False
        self.first_contact = None      # premier contact du tir
        self.potted_this_shot = []
        self.cue_ball_potted = False
        self.foul = False
        self.message = ""
        self.message_color = "#fff"
        self.message_timer = 0
        self.break_shot = True         # cassage

        self._place_balls()
        self._update_sidebar()

    def _place_balls(self):
        # Bille blanche
        cue = Ball(0, PLAY_X1 + (PLAY_X2 - PLAY_X1) * 0.25, CY)
        self.balls.append(cue)

        # Melange des 15 billes avec 8 au centre du triangle
        nums = list(range(1, 16))
        random.shuffle(nums)
        idx8 = nums.index(8)
        nums[4], nums[idx8] = nums[idx8], nums[4]

        tip_x = PLAY_X1 + (PLAY_X2 - PLAY_X1) * 0.70
        r = BALL_RADIUS * 2.08
        positions = []
        for row in range(5):
            for col in range(row + 1):
                bx = tip_x + row * r * math.cos(math.radians(30))
                by = CY + (col - row / 2.0) * r
                positions.append((bx, by))

        for i, (bx, by) in enumerate(positions):
            self.balls.append(Ball(nums[i], bx, by))

    @property
    def cue_ball(self):
        return self.balls[0] if self.balls else None

    def _all_stopped(self):
        return all(b.speed < MIN_SPEED for b in self.balls if not b.potted)

    # ── Physique ──────────────────────────────────────────────────────────────
    def _step(self):
        active = [b for b in self.balls if not b.potted]

        for _ in range(SUBSTEPS):
            for b in active:
                b.move(1.0 / SUBSTEPS)
                b.bounce_walls()

            # Collisions bille-bille
            for i in range(len(active)):
                for j in range(i + 1, len(active)):
                    self._collide(active[i], active[j])

        # Poches
        just_potted = []
        for b in list(active):
            if b.check_pocket():
                just_potted.append(b)

        if just_potted:
            self.potted_this_shot.extend(just_potted)
            if any(b.num == 0 for b in just_potted):
                self.cue_ball_potted = True

        if self._all_stopped() and self.shooting:
            self._end_shot()

    def _collide(self, a, b):
        dx = b.x - a.x
        dy = b.y - a.y
        dist = math.hypot(dx, dy)
        min_dist = 2 * BALL_RADIUS
        if dist == 0 or dist > min_dist:
            return

        nx, ny = dx / dist, dy / dist
        overlap = min_dist - dist
        a.x -= nx * overlap * 0.5
        a.y -= ny * overlap * 0.5
        b.x += nx * overlap * 0.5
        b.y += ny * overlap * 0.5

        dvx = a.vx - b.vx
        dvy = a.vy - b.vy
        dot = dvx * nx + dvy * ny
        if dot <= 0:
            return

        # Restitution elastique
        restitution = 0.96
        a.vx -= dot * nx * restitution
        a.vy -= dot * ny * restitution
        b.vx += dot * nx * restitution
        b.vy += dot * ny * restitution

        # Enregistrer premier contact
        if self.first_contact is None:
            if a.num == 0:
                self.first_contact = b.num
            elif b.num == 0:
                self.first_contact = a.num

    # ── Fin de tir ────────────────────────────────────────────────────────────
    def _end_shot(self):
        self.shooting = False
        potted = [b for b in self.potted_this_shot if b.num != 0]
        cb_potted = self.cue_ball_potted
        first_hit = self.first_contact

        self.cue_ball_potted = False
        self.potted_this_shot = []
        self.first_contact = None

        if self.game_over:
            return

        player = self.turn
        opponent = 1 - player
        foul = False

        # -- Detection de fautes --
        # Pas de contact
        if first_hit is None and not cb_potted:
            foul = True
            self._set_message("Faute ! Aucune bille touchee", "#ffa726")

        # Bille blanche empochee
        if cb_potted:
            foul = True
            self._set_message("Faute ! Bille blanche empochee", "#ffa726")

        # Mauvaise bille en premier (sauf cassage et groupes non definis)
        if not foul and not self.break_shot and self.groups[player] and first_hit:
            grp = self.groups[player]
            if grp == "pleines" and not (1 <= first_hit <= 7) and first_hit != 8:
                if self._player_balls_remaining(player) > 0:
                    foul = True
                    self._set_message("Faute ! Mauvaise bille touchee", "#ffa726")
            elif grp == "rayees" and not (9 <= first_hit <= 15) and first_hit != 8:
                if self._player_balls_remaining(player) > 0:
                    foul = True
                    self._set_message("Faute ! Mauvaise bille touchee", "#ffa726")

        self.break_shot = False

        # -- Verifier bille 8 --
        eight_potted = any(b.num == 8 for b in potted)
        if eight_potted:
            remaining = self._player_balls_remaining(player)
            if foul or remaining > 0 or self.groups[player] is None:
                winner = opponent
                reason = "8 empochee trop tot" if remaining > 0 else "faute sur le 8"
                self._set_message(f"Joueur {winner + 1} gagne ! ({reason})", "#ff5555")
                self.scores[winner] += 1
            else:
                self._set_message(f"Joueur {player + 1} gagne !", "#55ffaa")
                self.scores[player] += 1
            self.game_over = True
            self._update_sidebar()
            return

        # -- Attribution des groupes au premier empochage --
        if self.groups[0] is None and potted and not foul:
            nums = [b.num for b in potted if b.num != 8]
            if nums:
                has_solid = any(1 <= n <= 7 for n in nums)
                has_stripe = any(9 <= n <= 15 for n in nums)
                if has_solid and not has_stripe:
                    self.groups[player] = "pleines"
                    self.groups[opponent] = "rayees"
                    self._set_message("Groupes attribues !", "#4fc3f7")
                elif has_stripe and not has_solid:
                    self.groups[player] = "rayees"
                    self.groups[opponent] = "pleines"
                    self._set_message("Groupes attribues !", "#4fc3f7")

        # -- Gestion de la faute --
        if foul:
            self.foul = True
            self._respawn_cue_placement()
            self.turn = opponent
            self._update_sidebar()
            return

        # -- Compter empochages legaux --
        legal_potted = 0
        for b in potted:
            grp = self.groups[player]
            if grp is None:
                legal_potted += 1
            elif grp == "pleines" and 1 <= b.num <= 7:
                legal_potted += 1
            elif grp == "rayees" and 9 <= b.num <= 15:
                legal_potted += 1

        if legal_potted > 0:
            self.scores[player] += legal_potted
            self._set_message(f"+{legal_potted} bille(s) ! Rejouez", "#4fc3f7")
        else:
            if potted:
                self._set_message("Bille adverse empochee", "#ffa726")
                self.scores[opponent] += len(potted)
            self.turn = opponent

        self._update_sidebar()

    def _player_balls_remaining(self, player):
        grp = self.groups[player]
        if grp is None:
            return 7
        active = [b for b in self.balls if not b.potted]
        if grp == "pleines":
            return sum(1 for b in active if 1 <= b.num <= 7)
        else:
            return sum(1 for b in active if 9 <= b.num <= 15)

    def _respawn_cue_placement(self):
        """Active le mode de placement libre de la bille blanche."""
        cb = self.cue_ball
        cb.potted = False
        cb.vx = cb.vy = 0
        cb.x = PLAY_X1 + (PLAY_X2 - PLAY_X1) * 0.25
        cb.y = CY
        self.placing_cue = True
        self.status_lbl.config(text="Placez la bille blanche\n(clic pour confirmer)",
                               fg="#4fc3f7")

    def _valid_cue_position(self, x, y):
        """Verifie que la position est valide (pas de chevauchement)."""
        if x - BALL_RADIUS < PLAY_X1 or x + BALL_RADIUS > PLAY_X2:
            return False
        if y - BALL_RADIUS < PLAY_Y1 or y + BALL_RADIUS > PLAY_Y2:
            return False
        for b in self.balls:
            if b.num == 0 or b.potted:
                continue
            if math.hypot(b.x - x, b.y - y) < BALL_RADIUS * 2.2:
                return False
        return True

    def _set_message(self, msg, color="#fff"):
        self.message = msg
        self.message_color = color
        self.message_timer = 140

    # ── Tir ───────────────────────────────────────────────────────────────────
    def _shoot(self):
        if self.shooting or self.game_over or self.placing_cue:
            return
        cb = self.cue_ball
        if cb is None or cb.potted:
            return
        dx = cb.x - self.mouse_x
        dy = cb.y - self.mouse_y
        dist = math.hypot(dx, dy)
        if dist == 0 or self.power < 0.5:
            return
        spd = min(self.power, MAX_POWER)
        cb.vx = (dx / dist) * spd
        cb.vy = (dy / dist) * spd
        self.shooting = True
        self.aiming = False
        self.power = 0.0
        self.potted_this_shot = []
        self.cue_ball_potted = False
        self.first_contact = None

    # ── Souris ────────────────────────────────────────────────────────────────
    def _on_move(self, e):
        self.mouse_x, self.mouse_y = e.x, e.y
        if self.placing_cue:
            cb = self.cue_ball
            mx, my = e.x, e.y
            mx = max(PLAY_X1 + BALL_RADIUS, min(mx, PLAY_X2 - BALL_RADIUS))
            my = max(PLAY_Y1 + BALL_RADIUS, min(my, PLAY_Y2 - BALL_RADIUS))
            cb.x, cb.y = mx, my

    def _on_press(self, e):
        if self.game_over:
            return

        if self.placing_cue:
            cb = self.cue_ball
            if self._valid_cue_position(cb.x, cb.y):
                self.placing_cue = False
                self.status_lbl.config(text="Visez et tirez !", fg="#aaa")
            return

        if self.shooting:
            return
        self.drag_start = (e.x, e.y)
        self.aiming = True

    def _on_drag(self, e):
        if not self.aiming or self.drag_start is None:
            return
        dx = e.x - self.drag_start[0]
        dy = e.y - self.drag_start[1]
        dist = math.hypot(dx, dy)
        self.power = min(dist / 5.5, MAX_POWER)
        self.mouse_x = self.drag_start[0]
        self.mouse_y = self.drag_start[1]

    def _on_release(self, e):
        if not self.aiming:
            return
        self.mouse_x, self.mouse_y = self.drag_start
        self._shoot()
        self.drag_start = None
        self.aiming = False

    # ── Sidebar update ────────────────────────────────────────────────────────
    def _update_sidebar(self):
        for i in range(2):
            lbl = getattr(self, f"p{i + 1}_label")
            slbl = getattr(self, f"p{i + 1}_score_lbl")
            grp_lbl = getattr(self, f"p{i + 1}_grp_lbl")
            slbl.config(text=str(self.scores[i]))
            if i == self.turn and not self.game_over:
                lbl.config(fg="#4fc3f7")
            else:
                lbl.config(fg="#aaa")
            grp = self.groups[i]
            if grp:
                grp_lbl.config(text=f"({grp})", fg="#d4a853")
            else:
                grp_lbl.config(text="", fg="#777")

        self.turn_lbl.config(text=f"Joueur {self.turn + 1}")

        if not self.game_over:
            rem = self._player_balls_remaining(self.turn)
            can_8 = rem == 0 and self.groups[self.turn] is not None
            if can_8:
                self.status_lbl.config(text="Empoche la 8 pour gagner !", fg="#55ffaa")
            elif not self.placing_cue:
                self.status_lbl.config(text="Visez et tirez !", fg="#aaa")

        # Billes restantes
        self._draw_remaining_balls()

    def _draw_remaining_balls(self):
        rc = self.remaining_canvas
        rc.delete("all")
        active = [b for b in self.balls if not b.potted and b.num != 0]
        solids = sorted([b for b in active if 1 <= b.num <= 7], key=lambda b: b.num)
        stripes = sorted([b for b in active if 9 <= b.num <= 15], key=lambda b: b.num)
        eight = [b for b in active if b.num == 8]

        for idx, b in enumerate(solids):
            cx = 14 + idx * 22
            cy = 14
            rc.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                           fill=b.color, outline="#333")
        for idx, b in enumerate(stripes):
            cx = 14 + idx * 22
            cy = 38
            rc.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                           fill="white", outline="#333")
            rc.create_arc(cx - 8, cy - 8, cx + 8, cy + 8,
                          start=45, extent=90, fill=b.color, outline="")
            rc.create_arc(cx - 8, cy - 8, cx + 8, cy + 8,
                          start=225, extent=90, fill=b.color, outline="")
        if eight:
            cx = 170
            cy = 26
            rc.create_oval(cx - 9, cy - 9, cx + 9, cy + 9,
                           fill="#1a1a1a", outline="#333")
            rc.create_text(cx, cy, text="8", fill="white",
                           font=("Arial", 7, "bold"))

    # ── Dessin ────────────────────────────────────────────────────────────────
    def _draw(self):
        c = self.canvas
        c.delete("all")

        # Fond
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BG_COLOR, outline="")

        # Bord bois externe
        c.create_rectangle(TABLE_X1 - 12, TABLE_Y1 - 12,
                           TABLE_X2 + 12, TABLE_Y2 + 12,
                           fill="#2a1500", outline="#1a0a00", width=3)
        c.create_rectangle(TABLE_X1 - 8, TABLE_Y1 - 8,
                           TABLE_X2 + 8, TABLE_Y2 + 8,
                           fill=RAIL_DARK, outline="")

        # Rails
        c.create_rectangle(TABLE_X1, TABLE_Y1, TABLE_X2, TABLE_Y2,
                           fill=RAIL_COLOR, outline=RAIL_DARK, width=2)

        # Highlight sur les rails
        c.create_line(TABLE_X1, TABLE_Y1, TABLE_X2, TABLE_Y1,
                      fill=RAIL_HIGH, width=2)
        c.create_line(TABLE_X1, TABLE_Y1, TABLE_X1, TABLE_Y2,
                      fill=RAIL_HIGH, width=1)

        # Tapis vert
        c.create_rectangle(PLAY_X1, PLAY_Y1, PLAY_X2, PLAY_Y2,
                           fill=FELT_COLOR, outline="")

        # Texture tapis (lignes subtiles)
        for y_off in range(0, int(PLAY_Y2 - PLAY_Y1), 6):
            y = PLAY_Y1 + y_off
            c.create_line(PLAY_X1, y, PLAY_X2, y,
                          fill=CLOTH_LINE, width=1)

        # Diamants decoratifs sur les rails
        self._draw_diamonds(c)

        # Ligne de tete (zone de placement)
        head_x = PLAY_X1 + (PLAY_X2 - PLAY_X1) * 0.25
        c.create_line(head_x, PLAY_Y1 + 4, head_x, PLAY_Y2 - 4,
                      fill="#2a8a50", width=1, dash=(5, 8))

        # Point foot
        foot_x = PLAY_X1 + (PLAY_X2 - PLAY_X1) * 0.70
        c.create_oval(foot_x - 3, CY - 3, foot_x + 3, CY + 3,
                      fill="#2a8a50", outline="")

        # Poches
        for px, py in POCKETS:
            c.create_oval(px - POCKET_RADIUS - 2, py - POCKET_RADIUS - 2,
                          px + POCKET_RADIUS + 2, py + POCKET_RADIUS + 2,
                          fill="#050505", outline="")
            c.create_oval(px - POCKET_RADIUS, py - POCKET_RADIUS,
                          px + POCKET_RADIUS, py + POCKET_RADIUS,
                          fill=POCKET_COLOR, outline="#111", width=2)
            c.create_oval(px - POCKET_RADIUS + 4, py - POCKET_RADIUS + 4,
                          px - POCKET_RADIUS + 10, py - POCKET_RADIUS + 10,
                          fill="#181818", outline="")

        # Billes (ombre d'abord, puis billes)
        visible = [b for b in self.balls if not b.potted]
        for b in visible:
            self._draw_ball_shadow(c, b)
        for b in visible:
            self._draw_ball(c, b)

        # Indicateur de placement
        if self.placing_cue:
            cb = self.cue_ball
            if cb:
                valid = self._valid_cue_position(cb.x, cb.y)
                color = "#55ff55" if valid else "#ff5555"
                c.create_oval(cb.x - BALL_RADIUS - 6, cb.y - BALL_RADIUS - 6,
                              cb.x + BALL_RADIUS + 6, cb.y + BALL_RADIUS + 6,
                              outline=color, width=2, dash=(3, 3))

        # Queue de billard et ligne de visee
        if not self.shooting and not self.game_over and not self.placing_cue:
            cb = self.cue_ball
            if cb and not cb.potted:
                self._draw_aim_line(c, cb)
                self._draw_cue(c, cb)

        # Puissance
        self._draw_power()

        # Message flottant
        if self.message_timer > 0:
            self.message_timer -= 1
            fade = min(1.0, self.message_timer / 30.0)
            if fade > 0.3:
                c.create_rectangle(CX - 220, 15, CX + 220, 52,
                                   fill="#111111", outline="#333333", width=1)
                c.create_text(CX, 34, text=self.message,
                              font=("Georgia", 14, "bold"),
                              fill=self.message_color)

        # Game over overlay
        if self.game_over:
            c.create_rectangle(PLAY_X1, PLAY_Y1, PLAY_X2, PLAY_Y2,
                               fill="#000000", stipple="gray50")
            c.create_rectangle(CX - 250, CY - 65, CX + 250, CY + 65,
                               fill="#0d0d0d", outline="#d4a853", width=3)
            c.create_text(CX, CY - 20, text=self.message,
                          font=("Georgia", 22, "bold"),
                          fill=self.message_color)
            c.create_text(CX, CY + 25,
                          text="Cliquez 'Nouvelle Partie' pour rejouer",
                          font=("Georgia", 11, "italic"), fill="#888")

    def _draw_diamonds(self, c):
        """Dessine les diamants sur les rails (reperes de visee)."""
        ds = 5
        x_positions = []
        pw = PLAY_X2 - PLAY_X1
        for i in range(1, 8):
            x_positions.append(PLAY_X1 + pw * i / 8.0)
        for x in x_positions:
            y = (TABLE_Y1 + PLAY_Y1) / 2.0
            c.create_polygon(x, y - ds, x + ds, y, x, y + ds, x - ds, y,
                             fill=DIAMOND_COLOR, outline="")
            y = (TABLE_Y2 + PLAY_Y2) / 2.0
            c.create_polygon(x, y - ds, x + ds, y, x, y + ds, x - ds, y,
                             fill=DIAMOND_COLOR, outline="")
        y_positions = []
        ph = PLAY_Y2 - PLAY_Y1
        for i in range(1, 4):
            y_positions.append(PLAY_Y1 + ph * i / 4.0)
        for y in y_positions:
            x = (TABLE_X1 + PLAY_X1) / 2.0
            c.create_polygon(x, y - ds, x + ds, y, x, y + ds, x - ds, y,
                             fill=DIAMOND_COLOR, outline="")
            x = (TABLE_X2 + PLAY_X2) / 2.0
            c.create_polygon(x, y - ds, x + ds, y, x, y + ds, x - ds, y,
                             fill=DIAMOND_COLOR, outline="")

    def _draw_ball_shadow(self, c, b):
        r = BALL_RADIUS
        c.create_oval(b.x - r + 4, b.y - r + 4,
                      b.x + r + 4, b.y + r + 4,
                      fill="#0a2a15", outline="")

    def _draw_ball(self, c, b):
        x, y, r = b.x, b.y, BALL_RADIUS

        if b.striped and b.num != 0:
            c.create_oval(x - r, y - r, x + r, y + r,
                          fill="white", outline="#ccc", width=1)
            c.create_arc(x - r, y - r, x + r, y + r,
                         start=25, extent=130, fill=b.color, outline="")
            c.create_arc(x - r, y - r, x + r, y + r,
                         start=205, extent=130, fill=b.color, outline="")
        elif b.num == 0:
            c.create_oval(x - r, y - r, x + r, y + r,
                          fill="white", outline="#ddd", width=1)
        else:
            c.create_oval(x - r, y - r, x + r, y + r,
                          fill=b.color, outline=b.shade, width=1)

        # Reflet
        rx, ry = x - r * 0.35, y - r * 0.40
        c.create_oval(rx - 3, ry - 3, rx + 3, ry + 2,
                      fill="white", outline="")

        # Numero
        if b.num != 0:
            nr = 5 if b.num < 10 else 6
            c.create_oval(x - nr, y - nr, x + nr, y + nr,
                          fill="white", outline="")
            c.create_text(x, y, text=b.label,
                          font=("Arial", 6 if b.num >= 10 else 7, "bold"),
                          fill="black")

    def _draw_aim_line(self, c, cb):
        """Dessine la ligne de visee pointillee."""
        dx = cb.x - self.mouse_x
        dy = cb.y - self.mouse_y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        nx, ny = dx / dist, dy / dist

        for i in range(12):
            d = BALL_RADIUS + 10 + i * 14
            fx = cb.x - nx * d
            fy = cb.y - ny * d
            if fx < PLAY_X1 or fx > PLAY_X2 or fy < PLAY_Y1 or fy > PLAY_Y2:
                break
            sz = max(1, 3 - i * 0.2)
            c.create_oval(fx - sz, fy - sz, fx + sz, fy + sz,
                          fill="#88cc88", outline="")

        # Ghost ball (prediction de collision)
        self._draw_ghost_ball(c, cb, -nx, -ny)

    def _draw_ghost_ball(self, c, cb, dx, dy):
        """Montre ou la bille blanche va frapper la premiere bille."""
        best_dist = float("inf")
        best_ball = None

        sx, sy = cb.x, cb.y
        for b in self.balls:
            if b.num == 0 or b.potted:
                continue
            ex, ey = b.x - sx, b.y - sy
            proj = ex * dx + ey * dy
            if proj < BALL_RADIUS:
                continue
            perp_sq = (ex * ex + ey * ey) - proj * proj
            hit_dist_sq = (2 * BALL_RADIUS) ** 2
            if perp_sq < hit_dist_sq and proj < best_dist:
                best_dist = proj
                best_ball = b

        if best_ball and best_dist < 600:
            gx = sx + dx * best_dist
            gy = sy + dy * best_dist
            c.create_oval(gx - BALL_RADIUS, gy - BALL_RADIUS,
                          gx + BALL_RADIUS, gy + BALL_RADIUS,
                          outline="#88cc88", width=1, dash=(3, 3))

    def _draw_cue(self, c, cb):
        dx = cb.x - self.mouse_x
        dy = cb.y - self.mouse_y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        nx, ny = dx / dist, dy / dist

        offset = BALL_RADIUS + 6 + (self.power * 2.5 if self.aiming else 0)

        tip_x = cb.x + nx * offset
        tip_y = cb.y + ny * offset
        end_x = tip_x + nx * 200
        end_y = tip_y + ny * 200

        # Manche (bois fonce)
        c.create_line(tip_x + nx * 50, tip_y + ny * 50,
                      end_x, end_y,
                      fill="#5a3010", width=7, capstyle=tk.ROUND)
        # Corps principal
        c.create_line(tip_x + nx * 10, tip_y + ny * 10,
                      tip_x + nx * 55, tip_y + ny * 55,
                      fill=CUE_COLOR, width=6, capstyle=tk.ROUND)
        # Virole (bague blanche)
        c.create_line(tip_x + nx * 4, tip_y + ny * 4,
                      tip_x + nx * 12, tip_y + ny * 12,
                      fill="#cccccc", width=5, capstyle=tk.ROUND)
        # Procede (embout bleu)
        c.create_line(tip_x, tip_y,
                      tip_x + nx * 6, tip_y + ny * 6,
                      fill="#3a6090", width=4, capstyle=tk.ROUND)

    def _draw_power(self):
        pc = self.power_canvas
        pc.delete("all")
        ratio = self.power / MAX_POWER
        w = int(170 * ratio)
        if w > 0:
            r = int(min(255, 510 * ratio))
            g = int(max(0, 255 * (1 - ratio * 1.2)))
            b_val = 0
            color = f"#{min(r,255):02x}{max(g,0):02x}{b_val:02x}"
            pc.create_rectangle(0, 0, w, 20,
                                fill=color, outline="")
        pct = int(ratio * 100)
        pc.create_text(85, 10, text=f"{pct}%",
                       font=("Arial", 8, "bold"), fill="white")

    # ── Boucle principale ─────────────────────────────────────────────────────
    def _loop(self):
        if self.shooting:
            self._step()
        self._draw()
        self.root.after(16, self._loop)

    def _new_game(self):
        self.balls = []
        self._init_game()


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    game = BillardGame(root)
    root.mainloop()
