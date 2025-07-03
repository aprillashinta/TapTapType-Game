import pygame, random, sys, os

pygame.init()
lebar, tinggi = 360, 640
layar = pygame.display.set_mode((lebar, tinggi))
pygame.display.set_caption("ZType - Mobile Edition")
clock = pygame.time.Clock()

font_kecil = pygame.font.Font(None, 28)
font_sedang = pygame.font.Font(None, 36)
font_besar = pygame.font.Font(None, 64)

PUTIH, MERAH, BIRU, KUNING, ABU = (255,255,255), (255,70,70), (100,200,255), (255,255,100), (30,30,40)

load_img = lambda path, size: pygame.transform.scale(pygame.image.load(path), size)
start_icon = load_img("icon/start_icon.png", (100, 100))
restart_icon = load_img("icon/restart_icon.png", (60, 60))

pygame.mixer.init()
load_sfx = lambda path: pygame.mixer.Sound(path)
sound_start = load_sfx("sound/start.wav")
sound_success = load_sfx("sound/success.wav")
sound_gameover = load_sfx("sound/gameover.wav")
sound_type = load_sfx("sound/tik.mp3")

kata_list = ['python','java','kotlin','dart','swift','go','ruby','rust','php','html','css','sql','bash','c','csharp','perl']

load_highscore = lambda: int(open("highscore.txt").read()) if os.path.exists("highscore.txt") else 0

def simpan_highscore(skor):
    if skor > load_highscore():
        with open("highscore.txt", "w") as f:
            f.write(str(skor))

class Bintang:
    def __init__(self):
        self.x, self.y = random.randint(0, lebar), random.randint(0, tinggi)
        self.radius, self.speed = random.randint(1,2), random.uniform(0.3, 1)

    def update(self):
        self.y += self.speed
        if self.y > tinggi:
            self.y, self.x = 0, random.randint(0, lebar)

    def draw(self):
        pygame.draw.circle(layar, PUTIH, (int(self.x), int(self.y)), self.radius)

bintang_list = [Bintang() for _ in range(60)]

class Musuh:
    def __init__(self, skor):
        self.kata = random.choice(kata_list)
        self.x, self.y = random.randint(40, lebar - 100), -50
        self.kecepatan, self.aktif = 0.6 + skor * 0.05, True

    def update(self): self.y += self.kecepatan

    def draw(self):
        warna = KUNING if self.aktif else BIRU
        teks = font_sedang.render(self.kata, True, warna)
        pygame.draw.rect(layar, ABU, (self.x - 5, self.y - 3, teks.get_width()+10, teks.get_height()+6), border_radius=6)
        layar.blit(teks, (self.x, self.y))

def draw_background():
    layar.fill((10, 10, 25))
    for bintang in bintang_list: bintang.update(); bintang.draw()

def tampilkan_teks(teks, font, warna, y_offset=0, alpha=255):
    surf = font.render(teks, True, warna); surf.set_alpha(alpha)
    layar.blit(surf, surf.get_rect(center=(lebar//2, tinggi//2 + y_offset)))

def animate_icon_click(icon, pos):
    for scale in [0.9, 1.0]:
        ikon = pygame.transform.scale(icon, (int(icon.get_width()*scale), int(icon.get_height()*scale)))
        draw_background(); layar.blit(ikon, ikon.get_rect(center=pos))
        pygame.display.update(); pygame.time.delay(80)

def tampil_layar_awal():
    while True:
        clock.tick(60); draw_background()
        tampilkan_teks("ZTYPE", font_besar, KUNING, -150)
        tampilkan_teks("Programming Edition", font_kecil, BIRU, -100)
        tampilkan_teks("Tap icon to start", font_kecil, PUTIH, -50)
        rect = start_icon.get_rect(center=(lebar//2, tinggi//2 + 40)); layar.blit(start_icon, rect)
        if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            animate_icon_click(start_icon, rect.center); sound_start.play(); pygame.time.wait(200); break
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.update()

def tampil_game_over(skor, high):
    sound_gameover.play(); alpha = 0
    while True:
        clock.tick(60); draw_background(); alpha = min(255, alpha + 5)
        tampilkan_teks("GAME OVER", font_besar, MERAH, -120, alpha)
        tampilkan_teks(f"Your Score: {skor}", font_sedang, KUNING, -60, alpha)
        tampilkan_teks(f"Best Score: {high}", font_kecil, PUTIH, -20, alpha)
        tampilkan_teks("Tap to restart", font_kecil, BIRU, 30, alpha)
        rect = restart_icon.get_rect(center=(lebar//2, tinggi//2 + 100)); restart_icon.set_alpha(alpha)
        layar.blit(restart_icon, rect)
        if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and alpha >= 255:
            animate_icon_click(restart_icon, rect.center); pygame.time.wait(200); return
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.update()

# MAIN LOOP
tampil_layar_awal()

while True:
    musuh_list, input_user, skor = [], '', 0
    game_over, freeze_aktif, freeze_timer, spawn_timer = False, False, 0, 0
    spawn_delay, highscore = 1200, load_highscore()

    while not game_over:
        clock.tick(60); draw_background()
        now = pygame.time.get_ticks()

        if skor and skor % 10 == 0 and not freeze_aktif:
            freeze_aktif, freeze_timer = True, now

        if freeze_aktif:
            tampilkan_teks("FREEZE BONUS!", font_sedang, BIRU, 150)
            if now - freeze_timer > 3000: freeze_aktif = False
        elif now - spawn_timer > spawn_delay:
            musuh_list.append(Musuh(skor)); spawn_timer = now

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE: input_user = input_user[:-1]; sound_type.play()
                elif e.key == pygame.K_RETURN: input_user = ''
                else: input_user += e.unicode.lower(); sound_type.play()

        if not freeze_aktif:
            for musuh in musuh_list:
                if musuh.aktif:
                    musuh.update()
                    if input_user == musuh.kata:
                        musuh.aktif = False; skor += 1; input_user = ''
                        sound_success.play()
                    elif musuh.y > tinggi:
                        game_over = True

        for musuh in musuh_list: musuh.draw()
        pygame.draw.rect(layar, (0,0,0,80), (0, tinggi - 60, lebar, 60))
        tampilkan_teks(f"Input: {input_user}", font_kecil, BIRU, 220)
        tampilkan_teks(f"Score: {skor}", font_kecil, KUNING, -280)
        tampilkan_teks(f"Best: {highscore}", font_kecil, PUTIH, -250)
        pygame.display.update()

    simpan_highscore(skor)
    tampil_game_over(skor, max(skor, highscore))
