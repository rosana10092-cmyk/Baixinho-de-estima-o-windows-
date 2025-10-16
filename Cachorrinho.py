# cachorrinho.py
# Cachorrinho virtual simples para Windows (tkinter)
# Salve como 'cachorrinho.py' e execute com Python 3.x

import tkinter as tk
import random
import time

# CONFIG
WIDTH, HEIGHT = 160, 120          # tamanho do "pet" (canvas)
SPEED_MIN, SPEED_MAX = 1, 4      # velocidade de movimento
ANIM_INTERVAL = 150              # ms entre frames de animação
MOVE_INTERVAL = 40               # ms entre updates de posição
TRANSPARENT_COLOR = "#ff00ff"    # cor que será tornada transparente no Windows

class Cachorrinho:
    def __init__(self, root):
        self.root = root
        # Janela sem borda, sempre acima
        root.overrideredirect(True)
        root.wm_attributes("-topmost", True)
        # definir cor de fundo que será transparente
        root.config(bg=TRANSPARENT_COLOR)
        # Algumas versões do Windows aceitam:
        try:
            root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        except Exception:
            pass

        # Criar canvas do tamanho do pet
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                highlightthickness=0, bg=TRANSPARENT_COLOR)
        self.canvas.pack()

        # Posição inicial
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        self.x = random.randint(0, max(0, screen_w - WIDTH))
        self.y = random.randint(0, max(0, screen_h - HEIGHT - 40))  # reserve barra de tarefas
        root.geometry(f"{WIDTH}x{HEIGHT}+{self.x}+{self.y}")

        # Velocidade
        self.vx = random.choice([-1, 1]) * random.randint(SPEED_MIN, SPEED_MAX)
        self.vy = 0

        # Estado de animação
        self.frame = 0
        self.is_jumping = False
        self.jump_start = 0

        # Desenhos (serão redesenhados a cada frame)
        self.drawn_items = []

        # Interações de mouse
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.drag_offset = None

        # Start loops
        self.animate()
        self.move_loop()

    def draw_dog(self):
        # Limpa desenhos antigos
        for item in self.drawn_items:
            self.canvas.delete(item)
        self.drawn_items.clear()

        # Base do corpo
        body = self.canvas.create_oval(30, 40, 120, 90, fill="#D18B47", outline="")
        self.drawn_items.append(body)

        # Cabeça
        head = self.canvas.create_oval(80, 10, 140, 60, fill="#D18B47", outline="")
        self.drawn_items.append(head)

        # Orelha
        ear = self.canvas.create_polygon(92, 12, 106, 6, 114, 28, fill="#A15D2A", outline="")
        self.drawn_items.append(ear)

        # Olho
        eye = self.canvas.create_oval(108, 28, 116, 36, fill="black", outline="")
        self.drawn_items.append(eye)

        # Focinho
        snout = self.canvas.create_oval(122, 36, 138, 46, fill="#B06B38", outline="")
        self.drawn_items.append(snout)

        # Pata da frente (apoio)
        if self.frame % 2 == 0:
            paw1 = self.canvas.create_rectangle(40, 85, 56, 95, fill="#C97F45", outline="")
            paw2 = self.canvas.create_rectangle(80, 85, 96, 95, fill="#C97F45", outline="")
        else:
            paw1 = self.canvas.create_rectangle(44, 85, 60, 95, fill="#C97F45", outline="")
            paw2 = self.canvas.create_rectangle(76, 85, 92, 95, fill="#C97F45", outline="")
        self.drawn_items += [paw1, paw2]

        # Cauda (animação simples)
        if self.frame % 2 == 0:
            tail = self.canvas.create_line(20, 60, 5, 50, width=6, capstyle=tk.ROUND)
        else:
            tail = self.canvas.create_line(20, 60, 2, 70, width=6, capstyle=tk.ROUND)
        self.drawn_items.append(tail)

        # Olhar animado se pular
        if self.is_jumping:
            self.canvas.create_text(100, 20, text=":)", font=("Arial", 12))
        # sombra
        self.drawn_items.append(self.canvas.create_oval(40, 92, 120, 100, fill="#000000", stipple="gray50", outline=""))

    def animate(self):
        # Atualiza frame de animação
        self.frame += 1
        # Se estiver pulando, calcula deslocamento vertical
        if self.is_jumping:
            t = (time.time() - self.jump_start)
            # movimento parabólico simples
            height = max(0, 40 * (1 - (t / 0.6)**2))
            self.root.geometry(f"{WIDTH}x{HEIGHT}+{int(self.x)}+{int(self.y - height)}")
            if t > 0.6:
                self.is_jumping = False
        else:
            # garantir que janela esteja na posição base
            self.root.geometry(f"{WIDTH}x{HEIGHT}+{int(self.x)}+{int(self.y)}")

        self.draw_dog()
        self.root.after(ANIM_INTERVAL, self.animate)

    def move_loop(self):
        # Atualiza posição
        if not self.drag_offset:
            self.x += self.vx
            self.y += self.vy

            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()

            # Rebater nas bordas da tela
            if self.x <= 0 or self.x + WIDTH >= screen_w:
                self.vx = -self.vx
                self.x = max(0, min(self.x, screen_w - WIDTH))
            if self.y <= 0 or self.y + HEIGHT >= screen_h - 40:
                self.vy = -self.vy
                self.y = max(0, min(self.y, screen_h - HEIGHT - 40))

            # Mudança de direção ocasional
            if random.random() < 0.02:
                self.vx = random.choice([-1, 1]) * random.randint(SPEED_MIN, SPEED_MAX)
                self.vy = random.randint(-1, 1)

        # Atualiza geometria (se não estiver pulando, animate cuidará)
        if not self.is_jumping:
            self.root.geometry(f"{WIDTH}x{HEIGHT}+{int(self.x)}+{int(self.y)}")

        # Próximo movimento
        self.root.after(MOVE_INTERVAL, self.move_loop)

    def on_click(self, event):
        # Clicar faz pular
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_start = time.time()
        # Preparar drag
        self.drag_offset = (event.x_root - self.x, event.y_root - self.y)

    def on_drag(self, event):
        if self.drag_offset:
            new_x = event.x_root - self.drag_offset[0]
            new_y = event.y_root - self.drag_offset[1]
            self.x = new_x
            self.y = new_y
            self.root.geometry(f"{WIDTH}x{HEIGHT}+{int(self.x)}+{int(self.y)}")

    def on_release(self, event):
        self.drag_offset = None

if __name__ == "__main__":
    root = tk.Tk()
    # Minimizar a presença na barra de tarefas: algumas versões do Windows ainda mostram,
    # mas isso evita título padrão.
    try:
        root.wm_attributes("-toolwindow", True)
    except Exception:
        pass
    pet = Cachorrinho(root)
    root.mainloop()
