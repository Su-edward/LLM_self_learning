from turtle import color
import pygame
import random
import math

# 初始化 pygame
pygame.init()

# 設定 fps
fps = 60

# 設定視窗大小與格子數量
width, height = 800, 800
rows = 4
cols = 4

# 計算每個格子的高度和寬度
rect_height = height // rows
rect_width = width // cols

# 設定顏色與字體
outline_color = (187, 173, 160)  # 外框顏色
outline_thickness = 12          # 外框厚度
background_color = (205, 192, 180)  # 背景顏色
font_color = (119, 110, 101)     # 字體顏色

font = pygame.font.SysFont("comicsans", 60, bold=True)
move_vel = 20  # 每次移動的速度

# 設定視窗
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("2048")


class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    # 初始化
    def __init__(self,value,row,col):
        self.value =value
        self.row = row
        self.col = col
        self.x = col * rect_width
        self.y = row * rect_height

    # 取得顏色 -> 使用列表找出對應的顏色
    def get_color(self):
        # 2 的倍數,取log可得到順序
        color_index = int(math.log2(self.value)) -1
        color = self.COLORS[color_index]
        return color

    # 把方格上色、文字
    def draw(self,window):
        color = self.get_color()
        pygame.draw.rect(window,color,(self.x,self.y,rect_width,rect_height))

        text = font.render(str(self.value),1,font_color)
        # 把文字擺在方格中間
        window.blit(
            text,
            (self.x + (rect_width/2-text.get_width()/2),
             self.y + (rect_height/2-text.get_height()/2)
             )
       )
    # 位置設定
    def set_pos(self,ceil=False):
        if ceil:
            self.row = math.ceil(self.y/rect_height)
            self.col = math.ceil(self.x/rect_width)
        else:
            self.row = math.floor(self.y/rect_height)
            self.col = math.floor(self.x/rect_width)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]


# 進行外框顏色填充
def draw_gird(window):
    for row in range(rows):
        y = row * rect_height
        pygame.draw.line(window,outline_color,(0,y),(width,y),outline_thickness) # 橫線繪製
    
    for col in range(cols):
        x = col * rect_width
        pygame.draw.line(window,outline_color,(x,0),(x,height),outline_thickness) # 直線繪製
    
    pygame.draw.rect(window,outline_color,(0,0,width,height),outline_thickness) # 外框繪製

# 進行顏色的填充
def draw(window,tiles):
    window.fill(background_color)

    for tile in tiles.values():
        tile.draw(window)

    draw_gird(window)
    pygame.display.update()


# 隨機位置挑選，確保位置不要重複
def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0,rows)
        col = random.randrange(0,cols)

        # 確保位置沒有重複
        if f"{row}{col}" not in tiles:
            break

    return row,col




#方格的移動
def move_tile(window,tiles,clock,direction):
    updated = True
    blocks = set()

    if direction =="left":
        # ladbda 只需要回傳一個字, 但不需要建立fucntion x 回傳 x.col
        sort_function = lambda x:x.col
        reverse = False
        # 移動距離
        delta =(-move_vel,0)
        #邊界確定
        boundary_check = lambda tile:tile.col == 0
        # 獲取旁邊的方格
        get_next_tile = lambda tile:tiles.get(f"{tile.row}{tile.col-1}")
        #合併確認
        merge_check = lambda tile,next_tile: tile.x > next_tile.x + move_vel
        # 移動確認
        move_check = lambda tile,next_tile: tile.x > next_tile.x + rect_width +move_vel
        ceil = True

    elif direction =="right":
        # ladbda 只需要回傳一個字, 但不需要建立fucntion x 回傳 x.col
        sort_function = lambda x:x.col
        reverse = True
        # 移動距離
        delta =(move_vel,0)
        #邊界確定
        boundary_check = lambda tile:tile.col == cols-1
        # 獲取旁邊的方格
        get_next_tile = lambda tile:tiles.get(f"{tile.row}{tile.col+1}")
        #合併確認
        merge_check = lambda tile,next_tile: tile.x < next_tile.x - move_vel
        # 移動確認
        move_check = lambda tile,next_tile: tile.x +rect_width +move_vel< next_tile.x 
        ceil = False
    elif direction == "up":
        sort_function = lambda x: x.row
        reverse = False
        delta = (0, -move_vel)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + move_vel
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + rect_height + move_vel
        )
        ceil = True
    elif direction == "down":
        sort_function = lambda x: x.row
        reverse = True
        delta = (0, move_vel)
        boundary_check = lambda tile: tile.row == rows - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - move_vel
        move_check = (
            lambda tile, next_tile: tile.y + rect_height + move_vel < next_tile.y
        )
        ceil = False


    while updated:
        clock.tick(fps)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_function, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif (
                # 假設與兩個值相同
                tile.value == next_tile.value
                and tile not in blocks
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True
        update_tiles(window,tiles,sorted_tiles)

    return end_move(tiles)


def end_move(tiles):
    if len(tiles) == 16:
        return "lost"
    
    row,col = get_random_pos(tiles)
    tiles[f"{row}{col}"]= Tile(random.choice([2,4]),row,col)
    return "continue"



# 更新方塊，確保合併後所有方格的合併
def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile
    draw(window, tiles)
# 初始化方格
def generate_tiles():
    tiles ={}

    # _ 不在意變數的意思 , 初始皆為2
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2,row,col)

    return tiles



def main(window):
    # 主遊戲迴圈
    clock = pygame.time.Clock()
    run = True

    tiles =generate_tiles()

    while run:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            # 鍵盤輸入
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tile(window,tiles,clock,"left")
                if event.key == pygame.K_RIGHT:
                    move_tile(window,tiles,clock,"right")
                if event.key == pygame.K_UP:
                    move_tile(window,tiles,clock,"up")
                if event.key == pygame.K_DOWN:
                    move_tile(window,tiles,clock,"down")


        draw(window,tiles)


if __name__ == "__main__":
    main(window)
