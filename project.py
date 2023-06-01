import pygame
import random
import pprint
import time
from queue import Queue

pygame.init()

WIDTH, HEIGHT = 400,500

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")
# Difficulty levels
difficulty_levels = {
    "easy": {"rows": 8, "cols": 8, "mines": 10},
    "medium": {"rows": 8, "cols": 16, "mines": 16},
    "hard": {"rows": 16, "cols": 16, "mines": 50}
}

# Khai bao bien
COLOR = "white"
rows, cols = 8 , 8
mines = 10
num_font = pygame.font.SysFont('comicsans', 20)
lost_font = pygame.font.SysFont('comicsans', 100)
time_font = pygame.font.SysFont('comicsans', 50)
num_color = {1: "black", 2: "green", 3: "red", 4: "orange",
             5: "yellow", 6: "purple", 7: "blue", 8: "pink"}
rect_color = (200, 200, 200)
clicked_rect_color = (140, 140, 140)
flag_rect_color = "green"
mine_color = "red"
size = WIDTH / rows
#Function choose level
def choose_difficulty():
    text = num_font.render("Choose difficulty:", 1, "black")
    win.blit(text, ((WIDTH - text.get_width()) // 2, (HEIGHT - text.get_height()) // 2 - 50))

    options = ["easy", "medium", "hard"]
    option_texts = [num_font.render(option, 1, "black") for option in options]
    option_rects = [option_text.get_rect(center=((WIDTH // 2), (HEIGHT // 2) + 50 * (i + 1)))]
    for i, option_text in enumerate(option_texts):

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(mouse_pos):
                        return options[i]

        win.fill(COLOR)
        win.blit(text, ((WIDTH - text.get_width()) // 2, (HEIGHT - text.get_height()) // 2 - 50))
        for option_text, option_rect in zip(option_texts, option_rects):
            win.blit(option_text, option_rect)
        pygame.display.update()


# Function do bom xung quanh
def get_neighbors(row, col, rows, cols):
    neighbors = []

    if row > 0:  # UP
        neighbors.append((row - 1, col))
    if row < rows - 1:  # DOWN
        neighbors.append((row + 1, col))
    if col > 0:  # LEFT
        neighbors.append((row, col - 1))
    if col < cols - 1:  # RIGHT
        neighbors.append((row, col + 1))

    if row > 0 and col > 0:
        neighbors.append((row - 1, col - 1))
    if row < rows - 1 and col < cols - 1:
        neighbors.append((row + 1, col + 1))
    if row < rows - 1 and col > 0:
        neighbors.append((row + 1, col - 1))
    if row > 0 and col < cols - 1:
        neighbors.append((row - 1, col + 1))

    return neighbors


# Function to create the mine field
def create_mine_field(rows, cols, mines):
    field = [[0 for _ in range(cols)] for _ in range(rows)]
    mine_positions = set()

    # Randomly place mines
    while len(mine_positions) < mines:
        row = random.randrange(0, rows)
        col = random.randrange(0, cols)
        pos = row, col

        if pos in mine_positions:
            continue

        mine_positions.add(pos)
        field[row][col] = -1

    # Calculate neighbor counts
    for mine in mine_positions:
        neighbors = get_neighbors(*mine, rows, cols)
        for r, c in neighbors:
            if field[r][c] != -1:
                field[r][c] += 1

    return field


# Function to draw the game board
def draw(board, win, cover_field, rows, cols,current_time):
    win.fill(COLOR)
    
    time_text = time_font.render(f"Time elapsed:{round(current_time)}",1,"black")
    win.blit(time_text,(10,HEIGHT - time_text.get_height()))

    for i, row in enumerate(board):
        y = size * i
        for j, vars in enumerate(row):
            x = size * j

            is_covered = cover_field[i][j] == 0
            is_flag = cover_field[i][j] == -2
            is_mines = vars == -1
            
            if is_flag:
                pygame.draw.rect(win, flag_rect_color, (x, y, size, size))
                pygame.draw.rect(win, "black", (x, y, size, size), 2)
                continue
            
            if vars == -2:
                pygame.draw.rect(win, flag_rect_color, (x, y, size, size))
                pygame.draw.rect(win, "black", (x, y, size, size), 2)
                continue

            if is_covered:
                pygame.draw.rect(win, rect_color, (x, y, size, size))
                pygame.draw.rect(win, "black", (x, y, size, size), 2)
            else:
                pygame.draw.rect(win, clicked_rect_color, (x, y, size, size))
                pygame.draw.rect(win, "black", (x, y, size, size), 2)
                if vars == -1:
                    pygame.draw.circle(win, mine_color, (x + size / 2, y + size / 2), size / 3 - 4)
                if vars > 0:
                    text = num_font.render(str(vars), 1, num_color[vars])
                    win.blit(text, (x + (size / 2 - text.get_width() / 2), y + (size / 2 - text.get_height() / 2)))

    pygame.display.update()


# Function reveal click
def get_grid_pos(mouse_pos):
    mx, my = mouse_pos
    rows = int(my // size)
    cols = int(mx // size)

    return rows, cols
#Function mở các ô không có bomb ở gần
def uncover_from_pos(row, col, cover_field, board):
    q = Queue()
    q.put((row, col))
    visited = set()

    while not q.empty():
        current = q.get()
        neighbors = get_neighbors(*current, rows, cols)

        for r, c in neighbors:
            if (r, c) in visited:
                continue

            vars = board[r][c]

            if vars == -1:
                # Stop uncovering if a square with mines nearby is encountered
                return

            if vars == 0 and cover_field[r][c] != -2:
                q.put((r, c))

            if cover_field[r][c] != -2:
                cover_field[r][c] = 1

            visited.add((r, c))

#Function thang thua
def draw_lost(win,text):
    text = lost_font.render(text,1,"black")
    win.blit(text, ((WIDTH - text.get_width()) // 2, (HEIGHT - text.get_height()) // 2))
    pygame.display.update()
      
# mainFunction
def main():
    run = True
    current_difficulty = choose_difficulty()
    difficulty = difficulty_levels[current_difficulty]
    rows, cols, mines = difficulty["rows"], difficulty["cols"], difficulty["mines"]
    board = create_mine_field(rows, cols, mines)
    cover_field = [[0 for _ in range(cols)] for _ in range(rows)]
    flag_positions = set()
    flag = mines
    clicks= 0
    lost = False
    pprint.pprint(board)
    
    start_time = 0

    while run:
        if start_time >0 :
            current_time = time.time() - start_time
        else:
            current_time = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_grid_pos(pygame.mouse.get_pos())
                if row >= rows or col >= cols:
                    continue
                
                mouse_pressed = pygame.mouse.get_pressed()
                if mouse_pressed[0] and cover_field[row][col] != -2 and cover_field[row][col] != 1:
                    cover_field[row][col] = 1
                    #when bomb clicked
                    if board[row][col] ==-1:
                        lost = True
                    if clicks == 0 or board[row][col] == 0 or board[row][col] == -1:
                        uncover_from_pos(row, col, cover_field, board)
                    if clicks == 0 :
                        start_time = time.time()
                    clicks +=1
                elif mouse_pressed[2]:
                    if cover_field[row][col] == -2:
                        cover_field[row][col] = 0
                        flag +=1
                    else:
                        flag -= 1
                        cover_field[row][col] = -2   
                # Rest of the code
        if lost:
            draw(board,win,cover_field, rows,cols,current_time)
            draw_lost(win,"BẠN ĐÃ THUA")
            pygame.time.delay(1000)
                        
            cover_field = [[0 for _ in range(cols)] for _ in range(rows)]
            flag_positions = set()
            flag = mines
            clicks= 0
            lost = False
        draw(board, win, cover_field, rows, cols,current_time)

    pygame.quit()


if __name__ == '__main__':
    main()