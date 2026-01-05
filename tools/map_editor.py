import pygame
import csv
import os

# ----- CONFIG -----

TILE_SIZE = 32              # real tile size in tileset & game
GRID_W, GRID_H = 20, 15     # map size in tiles

ASSETS_DIR = "assets"
MAPS_DIR = os.path.join(ASSETS_DIR, "maps")
TILE_SHEET_PATH = os.path.join(ASSETS_DIR, "tiles", "tileset.png")
MAP_PATH = os.path.join(MAPS_DIR, "route1.csv")

FPS = 60

# Editor “zoom” sizes (display only, not saved)
EDITOR_TILE_SIZE = 48      # how big tiles look in the map area
PALETTE_TILE_SIZE = 48      # how big tiles look in the palette
PALETTE_COLS = 3            # number of columns in the palette panel

PALETTE_PANEL_PADDING_X = 20
PALETTE_PANEL_PADDING_Y = 40


# ---------- HELPERS ----------

def load_tilesheet(path):
    """Load tileset into a list indexed by tile ID (raw 32x32 surfaces)."""
    sheet = pygame.image.load(path).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()
    cols = sheet_w // TILE_SIZE
    rows = sheet_h // TILE_SIZE
    tiles = []
    for ty in range(rows):
        for tx in range(cols):
            rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile = sheet.subsurface(rect).copy()
            tiles.append(tile)
    return tiles


def load_map(path):
    """Load CSV map, pad/crop to proper size."""
    if not os.path.exists(path):
        return [[0 for _ in range(GRID_W)] for _ in range(GRID_H)]

    grid = []
    with open(path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            grid.append([int(x) for x in row])

    # Ensure correct height
    grid = grid[:GRID_H]
    while len(grid) < GRID_H:
        grid.append([0] * GRID_W)

    # Ensure correct width
    for y in range(GRID_H):
        row = grid[y][:GRID_W]
        if len(row) < GRID_W:
            row += [0] * (GRID_W - len(row))
        grid[y] = row

    return grid


def save_map(grid, path):
    """Save grid back to CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        for row in grid:
            writer.writerow(row)
    print(f"Saved map to {path}")


def add_rotated_tile(tiles, tile_id):
    """Rotate a tile 90° clockwise and append it to tile list."""
    base = tiles[tile_id]
    rotated = pygame.transform.rotate(base, -90)  # -90 = clockwise
    tiles.append(rotated)
    new_id = len(tiles) - 1
    print(f"Rotated tile {tile_id} -> New tile ID {new_id}")
    return new_id


# ---------- MAIN EDITOR ----------

def main():
    pygame.init()

    # Fix: create a tiny display BEFORE loading images with convert_alpha()
    pygame.display.set_mode((1, 1))

    # Now safely load tiles
    tiles = load_tilesheet(TILE_SHEET_PATH)

    # Map area size
    map_pixel_w = GRID_W * EDITOR_TILE_SIZE
    map_pixel_h = GRID_H * EDITOR_TILE_SIZE

    # Palette panel width
    palette_panel_width = PALETTE_COLS * PALETTE_TILE_SIZE + PALETTE_PANEL_PADDING_X * 2

    # Full window
    win_w = map_pixel_w + palette_panel_width
    win_h = map_pixel_h

    # Replace tiny window with full editor window
    screen = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("Route 1 Map Editor (Laptop Friendly)")


    clock = pygame.time.Clock()

    # Load map
    grid = load_map(MAP_PATH)

    current_tile = 0
    font_small = pygame.font.SysFont(None, 20)
    font_mid = pygame.font.SysFont(None, 26)

    # Palette layout calculations
    total_tiles = len(tiles)
    total_rows = (total_tiles + PALETTE_COLS - 1) // PALETTE_COLS

    # How many rows can we show in the palette panel vertically?
    available_h = win_h - PALETTE_PANEL_PADDING_Y - 10  # 10px bottom margin
    visible_rows = max(1, available_h // PALETTE_TILE_SIZE)

    first_visible_row = 0  # topmost palette row currently shown

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Quit quickly
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Save / load
                elif event.key == pygame.K_s:
                    save_map(grid, MAP_PATH)
                elif event.key == pygame.K_l:
                    grid = load_map(MAP_PATH)

                # Quick-select tiles 0–9
                elif pygame.K_0 <= event.key <= pygame.K_9:
                    num = event.key - pygame.K_0
                    if num < len(tiles):
                        current_tile = num

                # Rotate current tile and create new one
                elif event.key == pygame.K_r:
                    current_tile = add_rotated_tile(tiles, current_tile)
                    total_tiles = len(tiles)
                    total_rows = (total_tiles + PALETTE_COLS - 1) // PALETTE_COLS

                # ----- Arrow-key palette navigation -----
                elif event.key in (pygame.K_LEFT, pygame.K_a,
                                   pygame.K_RIGHT, pygame.K_d,
                                   pygame.K_UP, pygame.K_w,
                                   pygame.K_DOWN, pygame.K_s):
                    row = current_tile // PALETTE_COLS
                    col = current_tile % PALETTE_COLS

                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        if col > 0:
                            col -= 1
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if col < PALETTE_COLS - 1 and current_tile + 1 < total_tiles:
                            col += 1
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        if row > 0:
                            row -= 1
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if (row + 1) * PALETTE_COLS + col < total_tiles:
                            row += 1

                    new_index = row * PALETTE_COLS + col
                    if 0 <= new_index < total_tiles:
                        current_tile = new_index

                    # Auto-scroll palette to keep selection visible
                    row = current_tile // PALETTE_COLS
                    if row < first_visible_row:
                        first_visible_row = row
                    elif row >= first_visible_row + visible_rows:
                        first_visible_row = row - visible_rows + 1

                    # Clamp scroll
                    max_first = max(0, total_rows - visible_rows)
                    first_visible_row = max(0, min(first_visible_row, max_first))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # --- Click inside map area ---
                if mx < map_pixel_w and 0 <= my < map_pixel_h:
                    gx = mx // EDITOR_TILE_SIZE
                    gy = my // EDITOR_TILE_SIZE

                    if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                        if event.button == 1:      # paint
                            grid[gy][gx] = current_tile
                        elif event.button == 3:    # erase
                            grid[gy][gx] = 0

                # --- Click inside palette panel ---
                elif mx >= map_pixel_w:
                    palette_x = map_pixel_w
                    local_x = mx - palette_x - PALETTE_PANEL_PADDING_X
                    local_y = my - PALETTE_PANEL_PADDING_Y

                    if local_x >= 0 and local_y >= 0:
                        col = local_x // PALETTE_TILE_SIZE
                        row = local_y // PALETTE_TILE_SIZE + first_visible_row

                        if 0 <= col < PALETTE_COLS and 0 <= row < total_rows:
                            tile_id = row * PALETTE_COLS + col
                            if 0 <= tile_id < total_tiles:
                                current_tile = tile_id

        # ---------- DRAW ----------

        screen.fill((30, 30, 30))

        # --- Draw map area (left) ---
        for y in range(GRID_H):
            for x in range(GRID_W):
                tid = grid[y][x]
                if 0 <= tid < len(tiles):
                    # Scale tile to editor display size
                    tile_img = pygame.transform.scale(
                        tiles[tid],
                        (EDITOR_TILE_SIZE, EDITOR_TILE_SIZE)
                    )
                    screen.blit(tile_img, (x * EDITOR_TILE_SIZE, y * EDITOR_TILE_SIZE))

                # grid lines
                pygame.draw.rect(
                    screen, (0, 0, 0),
                    (x * EDITOR_TILE_SIZE, y * EDITOR_TILE_SIZE,
                     EDITOR_TILE_SIZE, EDITOR_TILE_SIZE),
                    1
                )

        # --- Draw palette panel background (right) ---
        palette_x = map_pixel_w
        pygame.draw.rect(
            screen,
            (15, 15, 40),
            (palette_x, 0, palette_panel_width, win_h)
        )

        # Palette title
        title_text = font_mid.render("Palette", True, (255, 255, 255))
        screen.blit(title_text, (palette_x + PALETTE_PANEL_PADDING_X, 10))

        # --- Draw palette tiles (auto scrolled by first_visible_row) ---
        start_y = PALETTE_PANEL_PADDING_Y

        for idx, tile in enumerate(tiles):
            row = idx // PALETTE_COLS
            col = idx % PALETTE_COLS

            # Only draw rows that are currently visible
            if row < first_visible_row or row >= first_visible_row + visible_rows:
                continue

            draw_x = palette_x + PALETTE_PANEL_PADDING_X + col * PALETTE_TILE_SIZE
            draw_y = start_y + (row - first_visible_row) * PALETTE_TILE_SIZE

            scaled_tile = pygame.transform.scale(
                tile,
                (PALETTE_TILE_SIZE, PALETTE_TILE_SIZE)
            )
            screen.blit(scaled_tile, (draw_x, draw_y))

            # Tile ID label
            id_text = font_small.render(str(idx), True, (255, 255, 255))
            screen.blit(id_text, (draw_x + 4, draw_y + 4))

            # Highlight selected tile
            if idx == current_tile:
                pygame.draw.rect(
                    screen,
                    (255, 255, 0),
                    (draw_x, draw_y, PALETTE_TILE_SIZE, PALETTE_TILE_SIZE),
                    3
                )

        # Instructions at bottom-left
        instr = (
            "Left-click=paint | Right-click=erase | 0-9=select | R=rotate | "
            "Arrow keys=move palette selection | S=save | L=load | ESC=quit"
        )
        instr_surf = font_small.render(instr, True, (220, 220, 220))
        screen.blit(instr_surf, (10, win_h - instr_surf.get_height() - 5))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
