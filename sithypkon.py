"""
SITHYPKON  –  20 Levels
=========================================
NEW:
  • Ant has walk / jump / hurt animations (sprite sheet slicing from single image)
  • Ladybug & Fish roam freely with AI:
      - Wander randomly around the whole level
      - CHASE the ant when within detection range
      - Bounce off walls and platform edges
      - Fish floats/swoops through the air
      - Ladybug patrols ground + platforms

Controls:
  Arrow Keys / WASD  – Move & Jump
  R                  – Restart level
  ESC                – Quit

Setup:
  pip install pygame Pillow numpy
  Place ant.png, ladybug.png, fish.png in same folder.
  py ant_escape_adventure.py
"""

import pygame, sys, math, random, os
from PIL import Image
import numpy as np

# ══════════════════════════════════════════════════════
SCREEN_W, SCREEN_H = 1100, 620
FPS        = 60
GRAVITY    = 0.55
JUMP_FORCE = -13.5
SPEED      = 4
GY         = SCREEN_H - 65   # ground y
WORLD_W    = 4000

# ══════════════════════════════════════════════════════
#  THEMES
# ══════════════════════════════════════════════════════
THEMES = {
 1: {"name":"Sunny Grassland",    "sky":[(135,206,235),(190,240,180)], "gc":(72,160,55),  "ec":(40,120,30),  "deco":"grass"},
 2: {"name":"Rocky Cliffs",       "sky":[(170,150,120),(220,200,170)], "gc":(130,110,85), "ec":(90,75,55),   "deco":"rocks"},
 3: {"name":"Muddy Riverside",    "sky":[(100,170,220),(160,215,245)], "gc":(110,170,80), "ec":(70,130,50),  "deco":"river"},
 4: {"name":"Dark Cave",          "sky":[(30,30,60),  (55,55,100)],   "gc":(70,60,90),   "ec":(45,35,65),   "deco":"stalactite"},
 5: {"name":"Flower Garden",      "sky":[(255,180,220),(255,220,245)], "gc":(200,100,180),"ec":(160,60,140), "deco":"flowers"},
 6: {"name":"Giant Tree Forest",  "sky":[(60,110,50), (100,160,80)],  "gc":(50,90,40),   "ec":(30,60,20),   "deco":"trees"},
 7: {"name":"Spider Web Forest",  "sky":[(50,40,60),  (80,70,90)],    "gc":(60,50,70),   "ec":(40,30,50),   "deco":"webs"},
 8: {"name":"Night Forest",       "sky":[(10,10,35),  (25,25,65)],    "gc":(30,40,70),   "ec":(15,20,50),   "deco":"fireflies"},
 9: {"name":"Ant Colony",         "sky":[(180,130,80),(220,170,120)],  "gc":(160,100,60), "ec":(120,70,30),  "deco":"tunnels"},
10: {"name":"Desert Canyon",      "sky":[(220,160,80),(255,195,110)],  "gc":(180,100,50), "ec":(140,70,20),  "deco":"canyon"},
11: {"name":"Crystal Cave",       "sky":[(40,20,80),  (80,50,130)],   "gc":(120,60,200), "ec":(80,30,160),  "deco":"crystals"},
12: {"name":"Frozen Tundra",      "sky":[(200,230,255),(235,248,255)], "gc":(160,210,240),"ec":(120,180,220),"deco":"snow"},
13: {"name":"Volcano Slopes",     "sky":[(80,20,0),   (160,55,10)],   "gc":(180,60,20),  "ec":(140,30,0),   "deco":"lava"},
14: {"name":"Sky Realm",          "sky":[(100,180,255),(180,225,255)], "gc":(220,240,255),"ec":(180,210,240),"deco":"clouds"},
15: {"name":"Mushroom Kingdom",   "sky":[(160,80,160),(210,130,210)],  "gc":(180,80,120), "ec":(140,40,80),  "deco":"mushrooms"},
16: {"name":"Sand Dune Desert",   "sky":[(220,200,140),(255,230,165)], "gc":(210,180,100),"ec":(170,140,60), "deco":"dunes"},
17: {"name":"Glowing Marsh",      "sky":[(25,70,45),  (55,115,75)],   "gc":(40,120,60),  "ec":(20,80,40),   "deco":"marsh"},
18: {"name":"Storm Cliffs",       "sky":[(55,55,80),  (85,85,120)],   "gc":(80,80,100),  "ec":(50,50,70),   "deco":"storm"},
19: {"name":"Royal Bridge",       "sky":[(80,60,150), (130,100,205)], "gc":(160,130,220),"ec":(120,90,180), "deco":"royal"},
20: {"name":"Ant Kingdom",        "sky":[(60,20,100), (120,55,185)],  "gc":(180,80,220), "ec":(130,40,170), "deco":"kingdom"},
}

COLLECT_INFO = {
 1:("Bread Crumb",(220,180,80)),   2:("Sugar Cube",(240,240,255)),
 3:("Water Drop",(80,200,255)),    4:("Glowstone",(120,255,150)),
 5:("Petal",(255,150,200)),        6:("Acorn",(160,120,60)),
 7:("Silk Thread",(240,240,200)),  8:("Firefly",(255,255,100)),
 9:("Ant Egg",(255,220,180)),     10:("Desert Gem",(100,220,255)),
11:("Crystal",(200,100,255)),     12:("Snowflake",(180,235,255)),
13:("Ember",(255,120,50)),        14:("Cloud Puff",(255,255,255)),
15:("Spore",(200,150,255)),       16:("Sand Pearl",(240,220,160)),
17:("Marsh Light",(100,255,150)), 18:("Storm Stone",(180,180,200)),
19:("Gold Coin",(255,215,0)),     20:("Royal Gem",(255,100,255)),
}

# ══════════════════════════════════════════════════════
#  IMAGE LOADING
# ══════════════════════════════════════════════════════
def remove_white_bg(path, threshold=230):
    img = Image.open(path).convert("RGBA")
    arr = np.array(img, dtype=np.uint8)
    r,g,b = arr[:,:,0],arr[:,:,1],arr[:,:,2]
    mask = (r>threshold)&(g>threshold)&(b>threshold)
    arr[:,:,3] = np.where(mask,0,arr[:,:,3])
    return arr

def load_sprite(path, size, threshold=230):
    if os.path.exists(path):
        try:
            arr = remove_white_bg(path,threshold)
            h,w = arr.shape[:2]
            surf = pygame.image.frombuffer(arr.tobytes(),(w,h),"RGBA").convert_alpha()
            return pygame.transform.smoothscale(surf,size)
        except Exception as e:
            print(f"Warn {path}: {e}")
    # fallback shape
    s = pygame.Surface(size,pygame.SRCALPHA)
    name = os.path.splitext(os.path.basename(path))[0].lower()
    c = {"ant":(200,40,40),"ladybug":(200,30,30),"fish":(230,130,50)}.get(name,(150,150,150))
    w,h = size
    pygame.draw.ellipse(s,c,(0,h//4,w,h*3//4))
    pygame.draw.ellipse(s,c,(w//4,0,w//2,h//2))
    pygame.draw.circle(s,(255,255,255),(w//3,h//3),w//7)
    pygame.draw.circle(s,(255,255,255),(w*2//3,h//3),w//7)
    pygame.draw.circle(s,(0,0,0),(w//3,h//3),w//14)
    pygame.draw.circle(s,(0,0,0),(w*2//3,h//3),w//14)
    return s

# ══════════════════════════════════════════════════════
#  ANIMATED SPRITE FRAMES  (fake walk cycle from 1 image)
# ══════════════════════════════════════════════════════
def make_walk_frames(base_img, n=6):
    """Generates n walk frames by bobbing + slight rotation from one image."""
    frames = []
    w,h = base_img.get_size()
    for i in range(n):
        angle = math.sin(i/n * math.pi*2) * 8       # sway -8..+8 degrees
        dy    = int(abs(math.sin(i/n * math.pi*2)) * 4)  # bounce 0..4 px
        rotated = pygame.transform.rotate(base_img, angle)
        frame = pygame.Surface((w,h+8), pygame.SRCALPHA)
        rw,rh = rotated.get_size()
        frame.blit(rotated, ((w-rw)//2, dy + (h-rh)//2))
        frames.append(frame)
    return frames

def make_jump_frame(base_img):
    """Squash the sprite upward for jump."""
    w,h = base_img.get_size()
    return pygame.transform.scale(base_img,(int(w*0.85),int(h*1.15)))

def make_hurt_frame(base_img):
    """Red tint overlay."""
    f = base_img.copy()
    red = pygame.Surface(f.get_size(), pygame.SRCALPHA)
    red.fill((255,0,0,120))
    f.blit(red,(0,0))
    return f

# ══════════════════════════════════════════════════════
#  PARTICLE
# ══════════════════════════════════════════════════════
class Particle:
    def __init__(self,x,y,color):
        self.x,self.y=float(x),float(y)
        self.vx=random.uniform(-2.5,2.5)
        self.vy=random.uniform(-5,-1)
        self.life=random.randint(25,55)
        self.max_life=self.life
        self.color=color
        self.r=random.randint(3,8)
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.18; self.life-=1
    def draw(self,surf,cx):
        a=max(0,int(255*self.life/self.max_life))
        s=pygame.Surface((self.r*2,self.r*2),pygame.SRCALPHA)
        pygame.draw.circle(s,(*self.color,a),(self.r,self.r),self.r)
        surf.blit(s,(int(self.x-cx-self.r),int(self.y-self.r)))

# ══════════════════════════════════════════════════════
#  COLLECTIBLE
# ══════════════════════════════════════════════════════
class Collectible:
    def __init__(self,x,y,color,name):
        self.base_y=float(y); self.x=float(x)
        self.color=color; self.name=name
        self.timer=random.randint(0,60)
        self.rect=pygame.Rect(x-14,y-14,28,28)
    def update(self):
        self.timer+=1
        self.rect.y=int(self.base_y+math.sin(self.timer*0.06)*6)
    def draw(self,surf,cx):
        px=int(self.x-cx); py=self.rect.y
        a=int(60+50*math.sin(self.timer*0.08))
        g=pygame.Surface((44,44),pygame.SRCALPHA)
        pygame.draw.circle(g,(*self.color,a),(22,22),20)
        surf.blit(g,(px-8,py-8))
        pts=[(px+14,py),(px+28,py+10),(px+28,py+24),(px+14,py+28),(px,py+24),(px,py+10)]
        pygame.draw.polygon(surf,self.color,pts)
        pygame.draw.polygon(surf,tuple(min(255,c+80) for c in self.color),pts,2)
        pygame.draw.circle(surf,(255,255,255),(px+9,py+8),4)

# ══════════════════════════════════════════════════════
#  PORTAL
# ══════════════════════════════════════════════════════
class Portal:
    def __init__(self,x,y):
        self.rect=pygame.Rect(x,y,64,96)
        self.timer=0; self.active=False
    def update(self): self.timer+=1
    def draw(self,surf,cx):
        t=self.timer; px=self.rect.centerx-cx; py=self.rect.centery
        if self.active:
            for i in range(6):
                r=30+i*7+int(math.sin(t*0.1+i)*5)
                a=max(0,150-i*22)
                s=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
                pygame.draw.ellipse(s,(80,255,120,a),s.get_rect())
                surf.blit(s,(px-r,py-r))
            pygame.draw.ellipse(surf,(120,255,160),(px-30,py-46,60,92),5)
            f=pygame.font.SysFont("Arial",14,bold=True)
            t2=f.render("EXIT",True,(0,220,80))
            surf.blit(t2,t2.get_rect(center=(px,self.rect.top-16)))
        else:
            pygame.draw.ellipse(surf,(80,80,80),(px-30,py-46,60,92),3)
            f=pygame.font.SysFont("Arial",12)
            t2=f.render("Locked",True,(140,140,140))
            surf.blit(t2,t2.get_rect(center=(px,self.rect.top-16)))

# ══════════════════════════════════════════════════════
#  ENEMY  
# ══════════════════════════════════════════════════════
DETECT_RANGE = 180   # pixels – enemy chases ant if closer than this
CHASE_SPEED  = 2.2
WANDER_SPEED = 1.4
FISH_SPEED   = 0.6   # fish moves slower than ladybug

class Enemy:
    def __init__(self, x, y, frames_r, frames_l, etype="walk"):
        self.frames_r = frames_r   # list of surfaces (walk animation)
        self.frames_l = frames_l
        self.etype    = etype      # "walk" or "float"
        self.rect     = frames_r[0].get_rect(midbottom=(x,y))
        self.vx       = random.choice([-WANDER_SPEED, WANDER_SPEED])
        self.vy       = 0.0
        self.frame    = 0
        self.ftimer   = 0
        self.state    = "wander"   # "wander" | "chase"
        # wander target
        self.target_x = x + random.randint(-400,400)
        self.wander_timer = 0

    def update(self, platforms, player_rect):
        self.ftimer += 1
        if self.ftimer % 18 == 0:
            self.frame = (self.frame+1) % len(self.frames_r)

        # ── decide state ──
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx,dy)
        if dist < DETECT_RANGE:
            self.state = "chase"
        else:
            self.state = "wander"

        if self.etype == "float":
            self._update_float(player_rect, dx, dy, dist)
        else:
            self._update_walk(platforms, player_rect, dx, dy, dist)

        # clamp to world
        self.rect.x = max(20, min(self.rect.x, WORLD_W-60))

    def _update_float(self, player_rect, dx, dy, dist):
        if self.state == "chase":
            spd = FISH_SPEED * 1.4
            if dist > 0:
                self.vx = (dx/dist)*spd
                self.vy = (dy/dist)*spd * 0.5
        else:
            # wander: pick a random target and swim there smoothly
            self.wander_timer += 1
            if self.wander_timer > 140 or abs(self.rect.centerx - self.target_x) < 40:
                self.target_x = random.randint(100, WORLD_W-100)
                self.wander_timer = 0
            ddx = self.target_x - self.rect.centerx
            # directly set vx toward target so fish always moves visibly
            self.vx = FISH_SPEED * (1 if ddx > 0 else -1)
            # gentle up-down wave while swimming
            self.vy = math.sin(self.wander_timer * 0.05) * 1.4

        # use float position so small speeds don't get rounded to 0
        self.fx = getattr(self, "fx", float(self.rect.x))
        self.fy = getattr(self, "fy", float(self.rect.y))
        self.fx += self.vx
        self.fy += self.vy
        # keep fish in air zone
        self.fy = max(50, min(self.fy, GY-90))
        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

    def _update_walk(self, platforms, player_rect, dx, dy, dist):
        if self.state == "chase":
            spd = CHASE_SPEED
            self.vx = spd * (1 if dx>0 else -1)
        else:
            # wander: pick random target and walk there
            self.wander_timer += 1
            if self.wander_timer > 200 or abs(self.rect.centerx - self.target_x) < 20:
                self.target_x = random.randint(60, WORLD_W-60)
                self.wander_timer = 0
            ddx = self.target_x - self.rect.centerx
            self.vx = WANDER_SPEED * (1 if ddx>0 else -1)

        # apply gravity + move
        self.vy += GRAVITY
        self.rect.x += int(self.vx)
        # horizontal wall bounce
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vx > 0: self.rect.right = p.left; self.vx *= -1; self.target_x = self.rect.centerx - 200
                else:           self.rect.left  = p.right; self.vx *= -1; self.target_x = self.rect.centerx + 200
        self.rect.y += int(self.vy)
        self.vy_resolved = False
        for p in platforms:
            if self.rect.colliderect(p) and self.vy >= 0:
                self.rect.bottom = p.top; self.vy = 0

        # fall-off guard: if about to walk off a platform edge, reverse
        probe = pygame.Rect(self.rect.x + int(self.vx*8), self.rect.bottom+2, self.rect.width, 4)
        on_something = any(probe.colliderect(p) for p in platforms)
        if not on_something and self.vy == 0 and self.state == "wander":
            self.vx *= -1
            self.target_x = self.rect.centerx + (-400 if self.vx<0 else 400)

    def draw(self, surf, cx):
        frames = self.frames_r if self.vx >= 0 else self.frames_l
        img = frames[self.frame % len(frames)]
        surf.blit(img, (self.rect.x-cx, self.rect.y))
        # draw detection circle (debug – comment out if you want)
        # pygame.draw.circle(surf,(255,0,0),(self.rect.centerx-cx,self.rect.centery),DETECT_RANGE,1)

# ══════════════════════════════════════════════════════
#  PLAYER  (animated)
# ══════════════════════════════════════════════════════
class Player:
    def __init__(self, x, y, walk_r, walk_l, jump_r, jump_l, hurt_img):
        self.walk_r  = walk_r    # list of frames
        self.walk_l  = walk_l
        self.jump_r  = jump_r    # single surface
        self.jump_l  = jump_l
        self.hurt_img= hurt_img  # single surface
        self.rect    = walk_r[0].get_rect(midbottom=(x,y))
        self.vx = self.vy = 0.0
        self.on_ground = False
        self.facing    = 1
        self.hp        = 3
        self.inv       = 0       # invincibility frames
        self.frame     = 0
        self.ftimer    = 0
        self.moving    = False

    def handle_input(self, keys):
        self.vx = 0; self.moving = False
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.vx=-SPEED; self.facing=-1; self.moving=True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx= SPEED; self.facing= 1; self.moving=True
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vy=JUMP_FORCE; self.on_ground=False

    def update(self, platforms):
        self.vy += GRAVITY
        self.rect.x += int(self.vx)
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vx>0: self.rect.right=p.left
                else:         self.rect.left =p.right
        self.rect.y += int(self.vy); self.on_ground=False
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vy>0: self.rect.bottom=p.top; self.vy=0; self.on_ground=True
                elif self.vy<0: self.rect.top=p.bottom; self.vy=0
        if self.inv>0: self.inv-=1
        # animate walk
        self.ftimer+=1
        if self.moving and self.on_ground and self.ftimer%18==0:
            self.frame=(self.frame+1)%len(self.walk_r)

    def draw(self, surf, cx):
        if self.inv>0 and (self.inv//4)%2==1: return
        img = self.walk_r[0] if self.facing==1 else self.walk_l[0]
        surf.blit(img,(self.rect.x-cx, self.rect.y))

# ══════════════════════════════════════════════════════
#  LEVEL DATA (20 unique hand-crafted layouts)
# ══════════════════════════════════════════════════════
def make_platforms(data):
    return [pygame.Rect(x,y,w,20) for x,y,w in data]

LEVEL_DATA = {
1:{"plats":[(200,GY-80,160),(420,GY-130,140),(620,GY-90,150),(850,GY-170,130),(1050,GY-110,160),(1260,GY-155,140),(1460,GY-90,160),(1670,GY-180,130),(1880,GY-120,150),(2080,GY-160,140),(2290,GY-100,160),(2500,GY-150,140),(2700,GY-90,160),(2900,GY-130,150),(3100,GY-170,130)],
   "items":[(220,GY-115),(640,GY-125),(870,GY-205),(1480,GY-125),(1900,GY-155)],
   "lb":4,"fi":0,"portal":(3150,GY-100)},

2:{"plats":[(180,GY-100,180),(400,GY-180,160),(640,GY-120,170),(870,GY-220,150),(1090,GY-160,170),(1310,GY-250,150),(1520,GY-180,160),(1730,GY-280,140),(1950,GY-200,170),(2160,GY-260,150),(2370,GY-180,160),(2580,GY-230,150),(2800,GY-160,170),(3000,GY-210,150),(3200,GY-140,160)],
   "items":[(200,GY-135),(660,GY-155),(1110,GY-195),(1740,GY-315),(2590,GY-265)],
   "lb":5,"fi":0,"portal":(3250,GY-100)},

3:{"plats":[(0,GY,260),(280,GY-40,120),(450,GY-70,120),(620,GY-40,130),(790,GY-75,110),(960,GY-50,130),(1130,GY-80,120),(1300,GY-50,130),(1480,GY-80,110),(1660,GY-50,130),(1830,GY-80,120),(2000,GY-50,130),(2180,GY-80,120),(2350,GY-50,130),(2530,GY-80,120),(2710,GY-50,130),(2900,GY-70,120),(3080,GY,260)],
   "items":[(300,GY-75),(810,GY-110),(1150,GY-115),(1850,GY-115),(2550,GY-115)],
   "lb":3,"fi":1,"portal":(3180,GY-100)},

4:{"plats":[(160,GY-90,160),(360,GY-170,140),(560,GY-110,150),(760,GY-210,130),(960,GY-150,160),(1160,GY-240,140),(1370,GY-160,160),(1590,GY-270,130),(1820,GY-200,150),(2060,GY-280,130),(2290,GY-210,150),(2520,GY-260,130),(2760,GY-180,160),(2980,GY-240,140),(3200,GY-160,150)],
   "items":[(180,GY-125),(580,GY-145),(980,GY-185),(1610,GY-305),(2080,GY-315)],
   "lb":4,"fi":1,"portal":(3250,GY-100)},

5:{"plats":[(150,GY-80,180),(380,GY-140,160),(620,GY-100,170),(840,GY-180,150),(1060,GY-130,170),(1280,GY-200,150),(1500,GY-130,170),(1720,GY-210,150),(1950,GY-150,160),(2170,GY-220,140),(2390,GY-160,170),(2620,GY-200,150),(2840,GY-130,160),(3050,GY-180,150),(3260,GY-110,160)],
   "items":[(170,GY-115),(640,GY-135),(1080,GY-165),(1740,GY-245),(2640,GY-235)],
   "lb":4,"fi":1,"portal":(3300,GY-100)},

6:{"plats":[(120,GY-100,160),(320,GY-190,150),(540,GY-150,160),(760,GY-260,140),(980,GY-200,160),(1210,GY-300,130),(1440,GY-230,150),(1680,GY-320,130),(1920,GY-250,150),(2160,GY-340,130),(2410,GY-270,150),(2660,GY-320,130),(2910,GY-250,150),(3160,GY-300,130),(3380,GY-180,150)],
   "items":[(140,GY-135),(560,GY-185),(1000,GY-235),(1700,GY-355),(2430,GY-305)],
   "lb":5,"fi":2,"portal":(3400,GY-100)},

7:{"plats":[(150,GY-100,160),(360,GY-200,140),(580,GY-140,160),(800,GY-250,130),(1020,GY-180,150),(1240,GY-290,130),(1460,GY-200,150),(1690,GY-310,130),(1930,GY-230,150),(2170,GY-320,130),(2420,GY-250,150),(2670,GY-310,130),(2920,GY-230,160),(3170,GY-280,140),(3400,GY-160,160)],
   "items":[(170,GY-135),(600,GY-175),(1040,GY-215),(1710,GY-345),(2440,GY-285)],
   "lb":5,"fi":2,"portal":(3420,GY-100)},

8:{"plats":[(120,GY-110,150),(340,GY-210,130),(560,GY-160,150),(790,GY-280,120),(1010,GY-200,150),(1240,GY-310,120),(1470,GY-230,140),(1710,GY-330,120),(1960,GY-260,140),(2210,GY-350,120),(2460,GY-280,140),(2720,GY-330,120),(2970,GY-260,140),(3220,GY-310,120),(3450,GY-180,150)],
   "items":[(140,GY-145),(580,GY-195),(1030,GY-235),(1730,GY-365),(2480,GY-315)],
   "lb":5,"fi":2,"portal":(3460,GY-100)},

9:{"plats":[(130,GY-100,170),(370,GY-180,150),(610,GY-130,160),(850,GY-230,140),(1080,GY-170,160),(1310,GY-270,140),(1540,GY-200,160),(1780,GY-300,140),(2020,GY-230,160),(2270,GY-310,140),(2520,GY-240,160),(2780,GY-290,140),(3030,GY-220,160),(3280,GY-270,140),(3480,GY-160,160)],
   "items":[(150,GY-135),(630,GY-165),(1100,GY-205),(1800,GY-335),(2540,GY-275)],
   "lb":6,"fi":2,"portal":(3500,GY-100)},

10:{"plats":[(0,GY,200),(250,GY-110,150),(480,GY-200,130),(710,GY-140,150),(940,GY-260,130),(1170,GY-190,150),(1410,GY-300,130),(1660,GY-220,150),(1910,GY-310,130),(2160,GY-240,150),(2420,GY-320,130),(2680,GY-250,150),(2950,GY-310,130),(3210,GY-230,150),(3450,GY,200)],
    "items":[(270,GY-145),(730,GY-175),(1190,GY-225),(1680,GY-255),(2180,GY-275)],
    "lb":4,"fi":3,"portal":(3460,GY-100)},

11:{"plats":[(110,GY-120,160),(340,GY-230,140),(580,GY-180,150),(820,GY-300,130),(1060,GY-240,150),(1310,GY-360,120),(1560,GY-280,140),(1820,GY-380,120),(2080,GY-310,140),(2350,GY-400,120),(2620,GY-330,140),(2900,GY-380,120),(3160,GY-300,140),(3400,GY-340,120),(3540,GY-180,150)],
    "items":[(130,GY-155),(600,GY-215),(1080,GY-275),(1840,GY-415),(2640,GY-365)],
    "lb":5,"fi":2,"portal":(3560,GY-100)},

12:{"plats":[(130,GY-100,170),(380,GY-185,155),(620,GY-140,165),(870,GY-250,145),(1110,GY-190,165),(1360,GY-290,145),(1600,GY-220,165),(1850,GY-310,140),(2100,GY-250,160),(2360,GY-330,140),(2620,GY-270,160),(2890,GY-320,140),(3150,GY-250,160),(3400,GY-300,145),(3560,GY-165,165)],
    "items":[(150,GY-135),(640,GY-175),(1130,GY-225),(1870,GY-345),(2640,GY-305)],
    "lb":6,"fi":2,"portal":(3580,GY-100)},

13:{"plats":[(100,GY-110,160),(330,GY-210,140),(570,GY-160,155),(810,GY-280,130),(1050,GY-220,155),(1300,GY-330,125),(1550,GY-260,145),(1810,GY-360,120),(2070,GY-290,145),(2340,GY-380,120),(2610,GY-310,145),(2890,GY-370,120),(3160,GY-300,145),(3420,GY-350,120),(3580,GY-180,155)],
    "items":[(120,GY-145),(590,GY-195),(1070,GY-255),(1830,GY-395),(2630,GY-345)],
    "lb":6,"fi":2,"portal":(3600,GY-100)},

14:{"plats":[(0,GY,180),(220,GY-60,130),(400,GY-130,120),(600,GY-80,130),(780,GY-160,120),(980,GY-100,130),(1180,GY-190,120),(1380,GY-120,130),(1580,GY-210,120),(1790,GY-140,130),(2000,GY-230,120),(2210,GY-160,130),(2430,GY-250,120),(2650,GY-180,130),(2880,GY-270,120),(3100,GY-200,130),(3330,GY-260,120),(3500,GY,180)],
    "items":[(240,GY-95),(620,GY-115),(1000,GY-135),(1800,GY-175),(2220,GY-195)],
    "lb":4,"fi":3,"portal":(3520,GY-100)},

15:{"plats":[(130,GY-100,165),(370,GY-200,145),(610,GY-155,160),(850,GY-270,140),(1090,GY-210,160),(1340,GY-320,130),(1590,GY-250,150),(1850,GY-350,125),(2110,GY-280,150),(2380,GY-370,125),(2650,GY-300,150),(2930,GY-360,125),(3200,GY-285,150),(3450,GY-335,130),(3600,GY-175,155)],
    "items":[(150,GY-135),(630,GY-190),(1110,GY-245),(1870,GY-385),(2670,GY-335)],
    "lb":6,"fi":3,"portal":(3620,GY-100)},

16:{"plats":[(0,GY,200),(240,GY-100,155),(480,GY-190,140),(720,GY-145,155),(960,GY-260,130),(1200,GY-200,150),(1450,GY-310,125),(1710,GY-240,145),(1980,GY-330,120),(2250,GY-260,145),(2530,GY-340,120),(2810,GY-270,145),(3090,GY-330,120),(3360,GY-250,145),(3600,GY,200)],
    "items":[(260,GY-135),(740,GY-180),(1220,GY-235),(1730,GY-275),(2270,GY-295)],
    "lb":5,"fi":3,"portal":(3620,GY-100)},

17:{"plats":[(0,GY,220),(270,GY-55,120),(450,GY-100,120),(650,GY-60,125),(830,GY-120,120),(1020,GY-70,130),(1210,GY-140,120),(1410,GY-80,130),(1610,GY-160,120),(1820,GY-100,130),(2030,GY-180,120),(2250,GY-120,130),(2470,GY-200,120),(2700,GY-140,130),(2930,GY-220,120),(3160,GY-160,130),(3390,GY-240,120),(3560,GY,220)],
    "items":[(290,GY-90),(670,GY-95),(1040,GY-105),(1840,GY-135),(2490,GY-235)],
    "lb":5,"fi":3,"portal":(3580,GY-100)},

18:{"plats":[(100,GY-120,155),(340,GY-240,135),(590,GY-190,150),(840,GY-320,120),(1090,GY-260,145),(1350,GY-380,115),(1610,GY-300,140),(1880,GY-410,110),(2150,GY-340,140),(2430,GY-430,110),(2710,GY-360,140),(3000,GY-420,110),(3280,GY-350,140),(3530,GY-400,115),(3660,GY-190,150)],
    "items":[(120,GY-155),(610,GY-225),(1110,GY-295),(1900,GY-445),(2730,GY-395)],
    "lb":6,"fi":3,"portal":(3680,GY-100)},

19:{"plats":[(0,GY,180),(210,GY-100,170),(440,GY-200,155),(680,GY-160,165),(920,GY-280,145),(1160,GY-220,165),(1410,GY-340,135),(1670,GY-270,155),(1940,GY-380,130),(2210,GY-310,150),(2490,GY-400,125),(2770,GY-330,150),(3060,GY-400,125),(3330,GY-320,150),(3570,GY-250,160),(3700,GY,180)],
    "items":[(230,GY-135),(700,GY-195),(1180,GY-255),(1690,GY-305),(2230,GY-345)],
    "lb":6,"fi":4,"portal":(3720,GY-100)},

20:{"plats":[(0,GY,200),(220,GY-100,180),(460,GY-210,160),(710,GY-170,170),(960,GY-300,145),(1210,GY-250,165),(1470,GY-380,135),(1740,GY-310,155),(2020,GY-420,125),(2300,GY-350,155),(2590,GY-440,120),(2880,GY-370,155),(3180,GY-440,120),(3470,GY-370,155),(3730,GY-300,165),(3900,GY,200)],
    "items":[(240,GY-135),(730,GY-205),(1230,GY-285),(1760,GY-345),(2320,GY-385)],
    "lb":7,"fi":4,"portal":(3920,GY-100)},
}

# ══════════════════════════════════════════════════════
#  BUILD LEVEL
# ══════════════════════════════════════════════════════
def build_level(lvl, lb_frames_r, lb_frames_l, fi_frames_r, fi_frames_l):
    d = LEVEL_DATA[lvl]
    cname,ccol = COLLECT_INFO[lvl]
    ground = pygame.Rect(0,GY,WORLD_W,65)
    platforms = [ground] + make_platforms(d["plats"])
    collectibles = [Collectible(x,y,ccol,cname) for x,y in d["items"]]
    enemies = []
    # spawn ladybugs at random x positions across level
    for i in range(d["lb"]):
        x = random.randint(300, WORLD_W-300)
        enemies.append(Enemy(x, GY, lb_frames_r, lb_frames_l, "walk"))
    # spawn fish at random positions in air
    for i in range(d["fi"]):
        x = random.randint(300, WORLD_W-300)
        y = random.randint(GY-280, GY-100)
        enemies.append(Enemy(x, y, fi_frames_r, fi_frames_l, "float"))
    portal = Portal(*d["portal"])
    return platforms, collectibles, enemies, portal, (80, GY-80)

# ══════════════════════════════════════════════════════
#  BACKGROUND
# ══════════════════════════════════════════════════════
def draw_bg(surf, lvl, cx, tick):
    th=THEMES[lvl]; tc,bc=th["sky"]
    for y in range(SCREEN_H):
        t=y/SCREEN_H
        c=tuple(int(tc[i]*(1-t)+bc[i]*t) for i in range(3))
        pygame.draw.line(surf,c,(0,y),(SCREEN_W,y))
    deco=th["deco"]
    if deco=="grass":
        for i in range(22):
            bx=(i*155-cx//3)%(SCREEN_W+60)-30
            s=int(math.sin(tick*0.025+i)*5)
            pygame.draw.polygon(surf,(45,170,45),[(bx+s,GY),(bx+10+s,GY),(bx+5,GY-65+i%3*12)])
    elif deco=="rocks":
        for i in range(10):
            rx=(i*330-cx//4)%(SCREEN_W+110)-55
            pygame.draw.polygon(surf,(95,85,70),[(rx,GY),(rx+90,GY),(rx+55,GY-170),(rx+35,GY-170)])
    elif deco=="river":
        pygame.draw.rect(surf,(60,120,190),(0,GY,SCREEN_W,65))
        for i in range(16):
            wx=(i*80+tick//2)%SCREEN_W
            pygame.draw.ellipse(surf,(100,170,230),(wx,GY+8,55,12))
    elif deco=="stalactite":
        for i in range(14):
            sx=(i*200-cx//5)%(SCREEN_W+60)-30
            h=40+i%3*25
            pygame.draw.polygon(surf,(50,40,65),[(sx,0),(sx+30,0),(sx+15,h)])
    elif deco=="flowers":
        for i in range(18):
            fx=(i*180-cx//3)%(SCREEN_W+60)-30
            col=[(255,80,80),(255,180,50),(200,100,255),(255,255,80)][i%4]
            pygame.draw.circle(surf,col,(fx,GY-20),10)
            pygame.draw.circle(surf,(255,255,150),(fx,GY-20),5)
    elif deco=="trees":
        for i in range(8):
            tx=(i*480-cx//5)%(SCREEN_W+140)-70
            pygame.draw.rect(surf,(45,28,12),(tx+38,GY-180,24,120))
            pygame.draw.circle(surf,(28,90,28),(tx+50,GY-200),70)
    elif deco=="webs":
        for i in range(6):
            wx=(i*550-cx//6)%(SCREEN_W+160)-80
            for j in range(5):
                pygame.draw.line(surf,(180,180,190),(wx+40,0),(wx+j*20,80+j*20),1)
    elif deco=="fireflies":
        for i in range(25):
            a=int(150+100*math.sin(tick*0.07+i*1.3))
            ffx=(i*130+int(math.sin(tick*0.02+i)*20)-cx//4)%(SCREEN_W+60)-30
            ffy=100+i%5*80+int(math.cos(tick*0.03+i)*15)
            s=pygame.Surface((10,10),pygame.SRCALPHA)
            pygame.draw.circle(s,(255,255,100,a),(5,5),4)
            surf.blit(s,(ffx,ffy))
    elif deco=="tunnels":
        for i in range(7):
            tx=(i*440-cx//5)%(SCREEN_W+120)-60
            pygame.draw.ellipse(surf,(100,65,35),(tx,GY-30,100,50))
    elif deco=="canyon":
        for i in range(8):
            rx=(i*430-cx//5)%(SCREEN_W+140)-70
            pygame.draw.polygon(surf,(140,80,30),[(rx,GY),(rx+60,GY),(rx+40,GY-200),(rx+20,GY-200)])
    elif deco=="crystals":
        for i in range(14):
            kx=(i*210-cx//6)%(SCREEN_W+70)-35
            h=50+i%3*25
            a=int(100+80*math.sin(tick*0.04+i))
            s=pygame.Surface((28,h),pygame.SRCALPHA)
            pygame.draw.polygon(s,(200,100,255,a),[(14,0),(28,h//2),(14,h),(0,h//2)])
            surf.blit(s,(kx,GY-h))
    elif deco=="snow":
        for i in range(20):
            sx=(i*160+int(math.sin(tick*0.01+i)*10)-cx//4)%(SCREEN_W+60)-30
            sy=int(50+i%5*100+math.cos(tick*0.02+i)*10)
            pygame.draw.circle(surf,(220,240,255),(sx,sy),3)
    elif deco=="lava":
        for i in range(12):
            lx=(i*250+tick)%SCREEN_W
            a=int(100+80*math.sin(tick*0.05+i))
            s=pygame.Surface((40,20),pygame.SRCALPHA)
            pygame.draw.ellipse(s,(255,80,0,a),s.get_rect())
            surf.blit(s,(lx,GY+5))
    elif deco=="clouds":
        for i in range(10):
            clx=(i*370-cx//2)%(SCREEN_W+120)-60
            cly=60+i%3*80
            pygame.draw.ellipse(surf,(255,255,255),(clx,cly,120,45))
            pygame.draw.ellipse(surf,(255,255,255),(clx+20,cly-20,80,45))
    elif deco=="mushrooms":
        for i in range(12):
            mx=(i*250-cx//4)%(SCREEN_W+80)-40
            col=[(200,60,60),(120,60,200),(60,160,60)][i%3]
            pygame.draw.ellipse(surf,col,(mx,GY-50,60,35))
            pygame.draw.rect(surf,(220,180,140),(mx+22,GY-30,16,30))
    elif deco=="dunes":
        for i in range(10):
            dx=(i*380-cx//5)%(SCREEN_W+120)-60
            pygame.draw.ellipse(surf,(195,165,90),(dx,GY-60,200,70))
    elif deco=="marsh":
        for i in range(16):
            gx=(i*200-cx//4)%(SCREEN_W+70)-35
            a=int(120+80*math.sin(tick*0.04+i))
            s=pygame.Surface((14,50),pygame.SRCALPHA)
            pygame.draw.rect(s,(60,180,60,a),(5,0,4,50))
            surf.blit(s,(gx,GY-50))
    elif deco=="storm":
        if tick%80<5:
            pygame.draw.line(surf,(255,255,180),(random.randint(0,SCREEN_W),0),(random.randint(0,SCREEN_W),SCREEN_H),2)
    elif deco=="royal":
        for i in range(8):
            px2=(i*430-cx//6)%(SCREEN_W+130)-65
            pygame.draw.rect(surf,(180,150,220),(px2,GY-120,20,120))
            pygame.draw.polygon(surf,(220,180,255),[(px2-8,GY-120),(px2+10,GY-155),(px2+28,GY-120)])
    elif deco=="kingdom":
        for i in range(6):
            kx=(i*560-cx//7)%(SCREEN_W+170)-85
            pygame.draw.rect(surf,(150,60,200),(kx,GY-200,40,200))
            pygame.draw.rect(surf,(200,100,255),(kx-15,GY-220,70,25))
            for j in range(3):
                pygame.draw.rect(surf,(220,150,255),(kx-15+j*25,GY-240,18,22))

def draw_platforms(surf, platforms, lvl, cx):
    th=THEMES[lvl]; gc,ec=th["gc"],th["ec"]
    for p in platforms:
        r=pygame.Rect(p.x-cx,p.y,p.width,p.height)
        pygame.draw.rect(surf,gc,r,border_radius=5)
        pygame.draw.rect(surf,ec,r,2,border_radius=5)
        pygame.draw.line(surf,tuple(min(255,c+45) for c in gc),(r.left+4,r.top+2),(r.right-4,r.top+2),2)

# ══════════════════════════════════════════════════════
#  HUD
# ══════════════════════════════════════════════════════
def draw_hud(surf,player,done,total,lvl,font,sf):
    pygame.draw.rect(surf,(0,0,0),(0,0,SCREEN_W,46))
    for i in range(3):
        c=(230,40,40) if i<player.hp else (50,50,50)
        hx,hy=22+i*34,14
        pygame.draw.polygon(surf,c,[(hx+8,hy+2),(hx+14,hy-4),(hx+20,hy+2),(hx+14,hy+12)])
        pygame.draw.circle(surf,c,(hx+5,hy),6)
        pygame.draw.circle(surf,c,(hx+11,hy),6)
    wn=THEMES[lvl]["name"]
    lt=font.render(f"Level {lvl}  –  {wn}",True,(255,240,120))
    surf.blit(lt,lt.get_rect(center=(SCREEN_W//2,22)))
    cname,ccol=COLLECT_INFO[lvl]
    it=sf.render(f"{cname}s: {done}/{total}",True,(200,240,255))
    surf.blit(it,(SCREEN_W-it.get_width()-12,10))
    bw=it.get_width()
    pygame.draw.rect(surf,(60,60,60),(SCREEN_W-bw-12,30,bw,7))
    if done>0:
        pygame.draw.rect(surf,ccol,(SCREEN_W-bw-12,30,int(bw*done/total),7))

# ══════════════════════════════════════════════════════
#  SCREENS
# ══════════════════════════════════════════════════════
def screen_title(surf,fb,fn,ant_walk,tick):
    surf.fill((10,45,10))
    for i in range(24):
        bx=i*52; s=int(math.sin(tick*0.03+i*.5)*6)
        pygame.draw.polygon(surf,(50,180,50),[(bx+s,GY),(bx+10+s,GY),(bx+5,GY-70+i%3*12)])
    t1=fb.render("🐜  SITHYPKON",True,(255,240,60))
    t2=fb.render("– 20 Levels",True,(255,200,40))
    surf.blit(t1,t1.get_rect(center=(SCREEN_W//2,140)))
    surf.blit(t2,t2.get_rect(center=(SCREEN_W//2,200)))
    lines=[
        fn.render("← → / A D   Move          ↑ / W / Space   Jump",True,(200,240,200)),
        fn.render("Collect 5 items per level to unlock the EXIT portal!",True,(200,240,200)),
        fn.render("Ladybug & Fish CHASE you when you get close!  ❤️❤️❤️",True,(255,180,180)),
        fn.render("R = Restart level          ESC = Quit",True,(180,220,180)),
        fn.render("▶  Press  ENTER  to Start",True,(255,255,80)),
    ]
    for i,l in enumerate(lines): surf.blit(l,l.get_rect(center=(SCREEN_W//2,312+i*44)))
    fi=tick//8 % len(ant_walk)
    surf.blit(ant_walk[fi],(SCREEN_W//2-ant_walk[fi].get_width()//2,48))

def screen_clear(surf,fb,fn,lvl,tick):
    ov=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA); ov.fill((0,0,0,160)); surf.blit(ov,(0,0))
    t=fb.render("✅  LEVEL CLEAR!",True,(80,255,120))
    surf.blit(t,t.get_rect(center=(SCREEN_W//2,SCREEN_H//2-80)))
    s=fn.render((f"Next: Level {lvl+1}  –  {THEMES[lvl+1]['name']}" if lvl<20 else "You completed ALL 20 levels!"),True,(200,255,200))
    surf.blit(s,s.get_rect(center=(SCREEN_W//2,SCREEN_H//2)))
    h=fn.render("Press ENTER to continue",True,(255,255,80))
    surf.blit(h,h.get_rect(center=(SCREEN_W//2,SCREEN_H//2+75)))

def screen_gameover(surf,fb,fn):
    ov=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA); ov.fill((0,0,0,190)); surf.blit(ov,(0,0))
    t=fb.render("💀  GAME OVER",True,(255,70,70))
    surf.blit(t,t.get_rect(center=(SCREEN_W//2,SCREEN_H//2-55)))
    r=fn.render("Press  R  to Restart  |  ESC  to Quit",True,(220,180,180))
    surf.blit(r,r.get_rect(center=(SCREEN_W//2,SCREEN_H//2+35)))

def screen_victory(surf,fb,fn,ant_walk,tick):
    surf.fill((20,5,40))
    rng=random.Random(tick//3)
    for _ in range(100):
        pygame.draw.circle(surf,(255,215,0),(rng.randint(0,SCREEN_W),rng.randint(0,SCREEN_H)),rng.randint(1,3))
    t=fb.render("🏆  YOU WIN!  ALL 20 LEVELS COMPLETE!",True,(255,215,0))
    s=fb.render("The Ant Kingdom is saved!  👑",True,(255,180,60))
    surf.blit(t,t.get_rect(center=(SCREEN_W//2,SCREEN_H//2-110)))
    surf.blit(s,s.get_rect(center=(SCREEN_W//2,SCREEN_H//2-50)))
    fi=tick//8 % len(ant_walk)
    surf.blit(ant_walk[fi],ant_walk[fi].get_rect(center=(SCREEN_W//2,SCREEN_H//2+40)))
    r=fn.render("Press  R  to Play Again  |  ESC  to Quit",True,(200,200,200))
    surf.blit(r,r.get_rect(center=(SCREEN_W//2,SCREEN_H//2+130)))

# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════
def main():
    pygame.init()
    screen=pygame.display.set_mode((SCREEN_W,SCREEN_H))
    pygame.display.set_caption("🐜 SITHYPKON – 20 Levels")
    clock=pygame.time.Clock()
    font_big=pygame.font.SysFont("Arial",44,bold=True)
    font    =pygame.font.SysFont("Arial",24)
    sfont   =pygame.font.SysFont("Arial",17)

    SD=os.path.dirname(os.path.abspath(__file__))

    # ── load base images ──
    ant_base = load_sprite(os.path.join(SD,"ant.png"),    (58,58),235)
    lb_base  = load_sprite(os.path.join(SD,"ladybug.png"),(52,52),220)
    fi_base  = load_sprite(os.path.join(SD,"fish.png"),   (60,44),210)

    # ── generate animation frames ──
    ant_walk_r = make_walk_frames(ant_base, 6)
    ant_walk_l = [pygame.transform.flip(f,True,False) for f in ant_walk_r]
    ant_jump_r = make_jump_frame(ant_base)
    ant_jump_l = pygame.transform.flip(ant_jump_r,True,False)
    ant_hurt   = make_hurt_frame(ant_base)

    lb_walk_r  = make_walk_frames(lb_base, 6)
    lb_walk_l  = [pygame.transform.flip(f,True,False) for f in lb_walk_r]

    fi_walk_r  = make_walk_frames(fi_base, 6)
    fi_walk_l  = [pygame.transform.flip(f,True,False) for f in fi_walk_r]

    MAX_LVL=20; TOTAL=5
    cur=1; state="title"; tick=0; cam_x=0; particles=[]

    def load_lvl(lvl):
        nonlocal particles,cam_x
        particles=[]; cam_x=0
        plats,colls,enems,portal,spawn=build_level(lvl,lb_walk_r,lb_walk_l,fi_walk_r,fi_walk_l)
        pl=Player(spawn[0],spawn[1],ant_walk_r,ant_walk_l,ant_jump_r,ant_jump_l,ant_hurt)
        return plats,colls,enems,portal,pl

    plats,colls,enems,portal,player=load_lvl(cur)

    while True:
        clock.tick(FPS); tick+=1
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if state=="title" and ev.key==pygame.K_RETURN:
                    state="playing"
                elif state=="level_clear" and ev.key==pygame.K_RETURN:
                    cur+=1
                    if cur>MAX_LVL: state="victory"
                    else: plats,colls,enems,portal,player=load_lvl(cur); state="playing"
                elif state in("game_over","victory") and ev.key==pygame.K_r:
                    cur=1; plats,colls,enems,portal,player=load_lvl(cur); state="playing"
                elif state=="playing" and ev.key==pygame.K_r:
                    plats,colls,enems,portal,player=load_lvl(cur)

        if state=="title":
            screen_title(screen,font_big,font,ant_walk_r,tick); pygame.display.flip(); continue
        if state=="victory":
            screen_victory(screen,font_big,font,ant_walk_r,tick); pygame.display.flip(); continue
        if state=="level_clear":
            draw_bg(screen,cur,cam_x,tick); draw_platforms(screen,plats,cur,cam_x)
            screen_clear(screen,font_big,font,cur,tick); pygame.display.flip(); continue
        if state=="game_over":
            draw_bg(screen,cur,cam_x,tick)
            screen_gameover(screen,font_big,font); pygame.display.flip(); continue

        # ── PLAYING ──
        keys=pygame.key.get_pressed()
        player.handle_input(keys)
        player.update(plats)
        cam_x=max(0,min(player.rect.centerx-SCREEN_W//2,WORLD_W-SCREEN_W))

        for e in enems: e.update(plats, player.rect)
        for c in colls: c.update()
        for p in particles[:]:
            p.update()
            if p.life<=0: particles.remove(p)

        for c in colls[:]:
            if player.rect.inflate(-4,-4).colliderect(c.rect):
                colls.remove(c)
                for _ in range(22): particles.append(Particle(c.x,c.rect.y,c.color))

        portal.active=len(colls)==0; portal.update()
        if portal.active and player.rect.colliderect(portal.rect):
            state="level_clear"

        if player.inv==0:
            for e in enems:
                if player.rect.inflate(-12,-12).colliderect(e.rect):
                    player.hp-=1; player.inv=90
                    player.vy=JUMP_FORCE*0.65
                    for _ in range(16):
                        particles.append(Particle(player.rect.centerx,player.rect.centery,(255,50,50)))
                    if player.hp<=0: state="game_over"
                    break

        if player.rect.top>SCREEN_H+100:
            player.hp-=1
            if player.hp<=0: state="game_over"
            else: player.rect.midbottom=(80,GY-80); player.vy=0; player.inv=90

        draw_bg(screen,cur,cam_x,tick)
        draw_platforms(screen,plats,cur,cam_x)
        for c in colls: c.draw(screen,cam_x)
        portal.draw(screen,cam_x)
        for e in enems: e.draw(screen,cam_x)
        player.draw(screen,cam_x)
        for p in particles: p.draw(screen,cam_x)
        draw_hud(screen,player,TOTAL-len(colls),TOTAL,cur,font,sfont)
        tip=sfont.render("← → Move   ↑/W/Space Jump   R Restart",True,(150,150,150))
        screen.blit(tip,tip.get_rect(center=(SCREEN_W//2,SCREEN_H-16)))
        pygame.display.flip()

if __name__=="__main__":
    main()
