import pygame
import random
import os

# 基本設定
FPS = 60
BLACK = (0,0,0)
WIDTH = 500
HEIGHT = 600
RED = (255,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)

pygame.init() #遊戲初始化
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT)) #視窗大小
pygame.display.set_caption("太空生存戰") #標題名稱
clock = pygame.time.Clock() #時間物件

# 載入圖片
background_img = pygame.image.load(os.path.join("img","background.png")).convert()
bullet_img = pygame.image.load(os.path.join("img","bullet.png")).convert()
player_img = pygame.image.load(os.path.join("img","player.png")).convert()
player_mini_img = pygame.transform.scale(player_img,(25,19))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
rock_imgs = [] #創建一個列表，依序把每個石頭圖片加入列表

for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img",f"rock{i}.png")).convert())

expl_anim = {}
expl_anim['lg'] = []
expl_anim['sm'] = []
expl_anim['player'] = []

for i in range(9):
    expl_img = pygame.image.load(os.path.join("img",f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img,(75,75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img,(30,30)))
    player_expl_img = pygame.image.load(os.path.join("img",f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(expl_img)
    
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img","shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img","gun.png")).convert()  

# 載入音效
shooot_sound = pygame.mixer.Sound(os.path.join("sound","shoot.wav"))
shooot_sound.set_volume(0.2)
gunup_sound = pygame.mixer.Sound(os.path.join("sound","pow1.wav"))
gunup_sound.set_volume(0.2)
shield_sound = pygame.mixer.Sound(os.path.join("sound","pow0.wav"))
shield_sound.set_volume(0.2)
expl_sounds = [    
    pygame.mixer.Sound(os.path.join("sound","expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound","expl1.wav"))
]

dead_sound = pygame.mixer.Sound(os.path.join("sound","rumble.ogg"))
dead_sound.set_volume(0.2)
for sound in expl_sounds:
    sound.set_volume(0.2)
pygame.mixer.music.load(os.path.join("sound","background.ogg"))
pygame.mixer.music.set_volume(0.2)

# 石頭生成
def new_rock(): 
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)

# 文字設定
font_name = os.path.join("font.ttf")
def draw_text(surf,text,size,x,y):
    font = pygame.font.Font(font_name,size)
    text_surface = font.render(text,True,WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface,text_rect)
    
# 初始畫面
def draw_init():
    screen.blit(background_img,(0,0)) 
    draw_text(screen,"太空生存戰",64,WIDTH/2,HEIGHT/4)
    draw_text(screen,"↑ ↓ ← → 移動飛船，空白鍵發射子彈 註:記得切英文輸入法",17,WIDTH/2,HEIGHT/2)
    draw_text(screen,"按任意鍵開始遊戲",18,WIDTH/2,HEIGHT * 3 / 4 )
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS) 
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False
# 生命條
def draw_health(surf,hp,x,y):
    if hp < 0:
        hp = 0
    BAR_LENTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENTH
    outline_rect = pygame.Rect(x,y,BAR_LENTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,GREEN,fill_rect)
    pygame.draw.rect(surf,WHITE,outline_rect,2)

# 復活次數
def draw_lives(surf,lives,img,x,y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i #間隔一個距離畫出飛船表示當前生命次數
        img_rect.y = y
        surf.blit(img,img_rect)
        
# 遊戲物件類別設定
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img,(50,38)) #設定物件圖片大小
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() #物件定位
        self.radius = 20 #設定物件圓形判定大小
        # pygame.draw.circle(self.image,RED,self.rect.center,self.radius) 測試物件HITBOX
        self.rect.centerx = WIDTH/2 #物件初始座標
        self.rect.bottom = HEIGHT - 10
        self.health = 100 
        self.shooting = False   # 是否正在射擊
        self.last_shot_time = 0 # 上次射擊時間
        self.shoot_delay = 200 # 射擊延遲時間，控制連射速度
        self.lives = 3 #復活次數
        self.hidden = False #判斷飛船當前是否為隱藏
        self.hide_time = 0 #隱藏時間
        self.gun = 1 #武器等級
        self.gun_time = 0
        
    def update(self):
        if self.gun > 1 and pygame.time.get_ticks() - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = pygame.time.get_ticks()
        if self.hidden and pygame.time.get_ticks() - self.hide_time > 2000: #若隱藏時間大於一秒則重新顯示
            self.hidden = False
            self.rect.centerx = WIDTH / 2 #物件初始座標
            self.rect.bottom = HEIGHT - 10   
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += 4
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= 4
        if key_pressed[pygame.K_UP]:
            self.rect.y -= 4
        if key_pressed[pygame.K_DOWN]:
            self.rect.y += 4
        # 判斷是否按下空白鍵，實現連續射擊 註:112行
        if key_pressed[pygame.K_SPACE]:
            self.shooting = True
        else:
            self.shooting = False
    
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            if not(self.hidden):
                self.rect.bottom = HEIGHT          
    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                current_time = pygame.time.get_ticks() # 獲取當前時間
                # 如果距離上次射擊的時間超過了射擊延遲時間
                if current_time - self.last_shot_time > self.shoot_delay:
                    bullet = Bullet(self.rect.centerx, self.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                    shooot_sound.play()
                    self.last_shot_time = current_time  # 更新上次射擊時間
            elif self.gun >= 2:
                current_time = pygame.time.get_ticks() # 獲取當前時間
                # 如果距離上次射擊的時間超過了射擊延遲時間
                if current_time - self.last_shot_time > self.shoot_delay:
                    bullet1 = Bullet(self.rect.left, self.rect.centery)
                    bullet2 = Bullet(self.rect.right, self.rect.centery)
                    all_sprites.add(bullet1)
                    all_sprites.add(bullet2)
                    bullets.add(bullet1)
                    bullets.add(bullet2)
                    shooot_sound.play()
                    self.last_shot_time = current_time  # 更新上次射擊時間
                    
    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2,HEIGHT + 500) #位置定位在視窗之外
    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()
            
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs) #隨機生成不同的石頭
        self.image_ori.set_colorkey(BLACK) #顏色
        self.image = self.image_ori.copy() #物件長寬度
        self.rect = self.image.get_rect() #定位
        self.radius = int(self.rect.width * 0.85 / 2)
        # pygame.draw.circle(self.image,RED,self.rect.center,self.radius) 測試物件hitbox
        self.rect.x = random.randrange(0,WIDTH - self.rect.width) #物件初始座標
        self.rect.y = random.randrange(-100,-40)
        self.speedy = random.randrange(2,10)
        self.speedx = random.randrange(-3,3)
        self.total_degree = 0
        self.rot_degree = 3
        
    # 使石頭物件能夠轉動
    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori,self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center
        
    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0,WIDTH - self.rect.width) #物件初始座標
            self.rect.y = random.randrange(-180,-100)
            self.speedy = random.randrange(2,10)
            self.speedx = random.randrange(-3,3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img #物件長寬度
        self.image.set_colorkey(BLACK) #顏色
        self.rect = self.image.get_rect() #定位
        self.rect.centerx = x #物件初始座標
        self.rect.bottom = y
        self.speedy = -10
        
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size 
        self.image = expl_anim[self.size][0] 
        self.rect = self.image.get_rect() 
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self,center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield","gun"])
        self.image = power_imgs[self.type] #物件長寬度
        self.image.set_colorkey(BLACK) #顏色
        self.rect = self.image.get_rect() #定位
        self.rect.center = center #物件初始座標
        self.speedy = 3
        
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()
                        

pygame.mixer.music.play(-1) # 無限次播放背景音樂

# 迴圈
show_init = True
running = True
while running:
    clock.tick(FPS) # 限制迴圈每秒執行次數
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        #創建sprites群組
        all_sprites = pygame.sprite.Group() 
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(10):
            new_rock()
        score = 0

    # 取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # 檢查事件的類型是否符合關閉遊戲的條件
            running = False # 若不符合，則跳脫迴圈，關閉遊戲
    
    # 更新遊戲
    all_sprites.update() # 執行update函式
    # 判斷子彈是否射中石頭
    hits = pygame.sprite.groupcollide(rocks,bullets,True,True) 
    for hit in hits:
        score += hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center,'lg')
        all_sprites.add(expl)
        if random.random() < 0.05: #掉寶機率調整
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()
        
    # 判斷玩家與石頭是否相撞
    hits = pygame.sprite.spritecollide(player,rocks,True,pygame.sprite.collide_circle) # 把碰撞判定設為圓形判定，使碰撞的判斷更加精確
    for hit in hits:
        player.health -= hit.radius * 1.5
        expl = Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)
        new_rock()
        
        if player.health <= 0:
            dead_expl = Explosion(player.rect.center,'player')
            all_sprites.add(dead_expl)
            dead_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
            
    #判斷寶物與玩家是否相撞
    hits = pygame.sprite.spritecollide(player,powers,True)
    for hit in hits:
          if hit.type == 'shield':
            player.health += 10
            if player.health > 100:
                player.health = 100
            shield_sound.play()
          elif hit.type == 'gun':
              player.gunup()
              gunup_sound.play()
              
    #當復活次數歸零且爆炸動畫結束就結束遊戲
    if player.lives == 0 and not(dead_expl.alive()):
        show_init = True
    
    # 畫面顯示
    screen.fill(BLACK)
    screen.blit(background_img,(0,0))
    all_sprites.draw(screen)
    draw_text(screen,str(score),18,WIDTH/2,10)
    draw_health(screen,player.health,5,15)
    draw_lives(screen,player.lives,player_mini_img,WIDTH - 100,15)
    
    #顯示更新內容
    pygame.display.update() 
    if player.shooting: #判斷是否按下空白鍵
        player.shoot()
    
pygame.quit() #關閉遊戲