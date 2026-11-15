import pygame
import random

# Pygame indítása
pygame.init()

# Képernyő teljes felbontásának lekérése (Androidon teljes képernyőre vált)
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Memóriajáték")

# Színek
BG_COLOR = (30, 30, 40)
CARD_BG = (70, 130, 180)
CARD_REVEALED = (240, 240, 240)
CARD_MATCHED = (100, 200, 100)
BTN_COLOR = (230, 140, 40)
TEXT_COLOR = (20, 20, 20)
WHITE = (255, 255, 255)

GRID_SIZE = 4

# Dinamikus méretezés a kijelzőhöz igazítva
MARGIN = int(WIDTH * 0.03)  # A képernyő szélességének 3%-a lesz a térköz
available_width = WIDTH - (GRID_SIZE + 1) * MARGIN
available_height = int(HEIGHT * 0.72) - (GRID_SIZE + 1) * MARGIN
CARD_SIZE = min(available_width // GRID_SIZE, available_height // GRID_SIZE)

# Rács középre igazítása
total_grid_w = GRID_SIZE * CARD_SIZE + (GRID_SIZE - 1) * MARGIN
total_grid_h = GRID_SIZE * CARD_SIZE + (GRID_SIZE - 1) * MARGIN
OFFSET_X = (WIDTH - total_grid_w) // 2
OFFSET_Y = (HEIGHT - total_grid_h) // 2 + int(HEIGHT * 0.03)

# Dinamikus betűméretek
card_font = pygame.font.SysFont(None, int(CARD_SIZE * 0.65))
ui_font = pygame.font.SysFont(None, int(WIDTH * 0.07))

def init_game():
    symbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] * 2
    random.shuffle(symbols)
    
    new_board = []
    idx = 0
    for r in range(GRID_SIZE):
        row = []
        for c in range(GRID_SIZE):
            row.append(symbols[idx])
            idx += 1
        new_board.append(row)
        
    new_revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    new_matched = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    return new_board, new_revealed, new_matched

board, revealed, matched = init_game()
first_selection = None
wait_time = 0
attempts = 0
matches_found = 0

# Új játék gomb pozíciója alul
btn_w, btn_h = int(WIDTH * 0.5), int(HEIGHT * 0.07)
restart_btn = pygame.Rect((WIDTH - btn_w) // 2, HEIGHT - btn_h - int(HEIGHT * 0.04), btn_w, btn_h)

running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BG_COLOR)
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and wait_time == 0:
            x, y = pygame.mouse.get_pos()
            
            # Új játék gomb ellenőrzése
            if restart_btn.collidepoint(x, y):
                board, revealed, matched = init_game()
                first_selection = None
                attempts = 0
                matches_found = 0
                continue

            # Kártyák érintésének ellenőrzése
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    card_x = OFFSET_X + c * (CARD_SIZE + MARGIN)
                    card_y = OFFSET_Y + r * (CARD_SIZE + MARGIN)
                    
                    if card_x <= x <= card_x + CARD_SIZE and card_y <= y <= card_y + CARD_SIZE:
                        if not revealed[r][c] and not matched[r][c]:
                            revealed[r][c] = True
                            
                            if first_selection is None:
                                first_selection = (r, c)
                            else:
                                r1, c1 = first_selection
                                attempts += 1
                                if board[r1][c1] == board[r][c]:
                                    matched[r1][c1] = True
                                    matched[r][c] = True
                                    matches_found += 1
                                    first_selection = None
                                else:
                                    wait_time = current_time

    # Rossz tipp visszafordítása
    if wait_time > 0 and current_time - wait_time > 800:
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if revealed[r][c] and not matched[r][c]:
                    revealed[r][c] = False
        first_selection = None
        wait_time = 0

    # Fejléc kiírása középre igazítva
    info_text = ui_font.render(f"Próba: {attempts}   |   Párok: {matches_found}/8", True, WHITE)
    screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, int(HEIGHT * 0.05)))

    # Kártyák kirajzolása
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            card_x = OFFSET_X + c * (CARD_SIZE + MARGIN)
            card_y = OFFSET_Y + r * (CARD_SIZE + MARGIN)
            rect = pygame.Rect(card_x, card_y, CARD_SIZE, CARD_SIZE)
            radius = int(CARD_SIZE * 0.15)
            
            if matched[r][c]:
                pygame.draw.rect(screen, CARD_MATCHED, rect, border_radius=radius)
                txt = card_font.render(board[r][c], True, TEXT_COLOR)
                screen.blit(txt, txt.get_rect(center=rect.center))
            elif revealed[r][c]:
                pygame.draw.rect(screen, CARD_REVEALED, rect, border_radius=radius)
                txt = card_font.render(board[r][c], True, TEXT_COLOR)
                screen.blit(txt, txt.get_rect(center=rect.center))
            else:
                pygame.draw.rect(screen, CARD_BG, rect, border_radius=radius)
                txt = card_font.render("?", True, WHITE)
                screen.blit(txt, txt.get_rect(center=rect.center))

    # Győzelmi felirat vagy Új játék gomb
    if matches_found == 8:
        win_text = ui_font.render("Szuper, nyertél!", True, (100, 255, 100))
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, OFFSET_Y - int(HEIGHT * 0.06)))

    pygame.draw.rect(screen, BTN_COLOR, restart_btn, border_radius=15)
    btn_txt = ui_font.render("Új játék", True, WHITE)
    screen.blit(btn_txt, btn_txt.get_rect(center=restart_btn.center))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()