import pgzrun
from pygame import Rect

# How big the game window is (like a TV screen!)
WIDTH = 800
HEIGHT = 600
# The ground is at y=500 (this is where the floor is)
GROUND = 500
# State of the game, starts in the menu. Other game states: menu, playing, win, or lose
game_state = "menu"
# Count number of coins collected
score = 0
# Turn sound on or off. Initially ON
sound_on = True

# Handles sound play (like a coin jingle or jump noise)
def play_sound(sound_name):
    if sound_on:
        try: getattr(sounds, sound_name).play()
        except Exception: pass

# Handles stopping sound (like stopping footstep noises)
def stop_sound(sound_name):
    try: getattr(sounds, sound_name).stop()
    except Exception: pass

def play_music():
    if sound_on:
        try:
            music.play("game_music")
            music.set_volume(0.8)
        except Exception:
            pass

def stop_music():
    try:
        music.stop()
    except Exception:
        pass


# This is the PLAYER class
class Player(Actor):
    def __init__(self):
        # Put the player picture on the screen at position (100, 420)
        super().__init__("player_idle", (100, 420))
        # Player speed
        self.speed = 5
        # How high the player jump (negative = up!)
        self.jump_power = -19
        # How fast the player falls (gravity pulls us down)
        self.gravity = 0.7
        # How fast the player falls right now
        self.velocity_y = 0
        # Which walk picture to show
        self.walk_frame = 0

    def update(self, platforms):
        # GRAVITY pulls me down (just like in real life!)
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # If I hit the GROUND, stop falling
        if self.y >= GROUND - 30:
            self.y, self.velocity_y = GROUND - 30, 0

        # Check if I landed on a PLATFORM (a floating floor)
        for platform in platforms:
            feet_y = self.y + 30  # Where the player's feet are
            if (feet_y >= platform.top and feet_y <= platform.top + 20 and
                self.x + 20 > platform.left and self.x - 20 < platform.right and self.velocity_y > 0):
                # I landed! Stop falling
                self.y, self.velocity_y = platform.top - 30, 0
                break

        # WALKING ANIMATION - swap between two walk pictures so it looks like I am walking
        if keyboard.left or keyboard.right:
            self.walk_frame += 1
            if self.walk_frame % 8 == 0:
                self.image = "player_walk1" if self.image == "player_walk2" else "player_walk2"
        elif not self.is_jumping():
            # I am standing still? Show the standing picture
            self.image = "player_idle"

        # If I am in the air, show the jump picture
        if self.is_jumping():
            self.image = "player_jump"

        # Play footstep sounds when I am walking on the ground
        if sound_on and game_state == "playing":
            if (keyboard.left or keyboard.right) and not self.is_jumping():
                try:
                    if not sounds.running_forest.get_num_channels():
                        sounds.running_forest.play(-1)
                except Exception: pass
            else:
                stop_sound("running_forest")

    # Am I in the air right now?
    def is_jumping(self):
        return self.velocity_y < -1 or self.y < GROUND - 35

    # JUMP! But only if I am on the ground or on a platform
    def jump(self):
        if self.y >= GROUND - 35 or (abs(self.velocity_y) < 0.5 and self.y < GROUND - 35):
            self.velocity_y = self.jump_power
            play_sound("jump")

# This is a ZOMBIE - the bad guy! He walks back and forth
class Zombie(Actor):
    def __init__(self, x, y, patrol_width=100):
        super().__init__("zombie_idle", (x, y))
        # The zombie walks between these two spots (like a guard)
        self.patrol_left, self.patrol_right = x - patrol_width // 2, x + patrol_width // 2
        # How fast the zombie walks
        self.speed = 1.5
        # Which way the zombie is going (1 = right, -1 = left)
        self.direction = 1
        # Which walk picture to show
        self.walk_frame = 0

    def update(self):
        # Move the zombie left or right
        self.x += self.speed * self.direction

        # If the zombie reaches the edge, turn around!
        if self.x <= self.patrol_left:
            self.x, self.direction = self.patrol_left, 1
        elif self.x >= self.patrol_right:
            self.x, self.direction = self.patrol_right, -1

        # Swap pictures to make it look like the zombie is walking
        self.walk_frame += 1
        if self.walk_frame % 10 == 0:
            self.image = "zombie_walk1" if self.image == "zombie_walk2" else "zombie_walk2"

# This is an ALIEN - another bad guy! He also patrols back and forth
class Alien(Actor):
    def __init__(self, x, y, patrol_width=100):
        super().__init__("aliengreen_stand", (x, y))
        # The alien walks between these two spots
        self.patrol_left, self.patrol_right = x - patrol_width // 2, x + patrol_width // 2
        # How fast the alien walks
        self.speed = 1.2
        # Which way the alien is going (1 = right, -1 = left)
        self.direction = 1
        # Which walk picture to show
        self.walk_frame = 0

    def update(self):
        # Move the alien left or right
        self.x += self.speed * self.direction

        # If the alien reaches the edge, turn around!
        if self.x <= self.patrol_left:
            self.x, self.direction = self.patrol_left, 1
        elif self.x >= self.patrol_right:
            self.x, self.direction = self.patrol_right, -1

        # Swap pictures to make it look like the alien is walking
        self.walk_frame += 1
        if self.walk_frame % 10 == 0:
            self.image = "aliengreen_walk1" if self.image == "aliengreen_walk2" else "aliengreen_walk2"

# CREATE all the things in my game world
player = Player()
zombies = [Zombie(280, 395, 60)]
alien = Alien(480, 322, 40)
# All enemies in one list so I can check them all
enemies = [zombies[0], alien]
coins = [Actor("coin", (150, 420)), Actor("coin", (400, 340)), Actor("coin", (650, 260))]
# These are the floating platforms I can stand on
platforms = [Rect(100, 450, 200, 20), Rect(350, 370, 150, 20),
             Rect(600, 290, 150, 20), Rect(200, 210, 100, 20)]

# This runs every frame (like a flipbook - super fast!)
def update():
    global game_state, score

    # Only do stuff if I am actually playing
    if game_state != "playing":
        stop_sound("running_forest")
        stop_music()
        return

    player.update(platforms)

    # LEFT and RIGHT arrow keys move the player
    if keyboard.left:  player.x = max(60, player.x - player.speed)
    if keyboard.right: player.x = min(WIDTH - 60, player.x + player.speed)

    # Check each enemy (zombies and aliens!)
    for enemy in enemies:
        enemy.update()
        # Game over when I get touched by an enemy
        if player.colliderect(enemy):
            game_state = "lose"
            stop_sound("running_forest")
            stop_music()
            play_sound("lose")
            return

    # Check if I touched a coin - if yes collect coin and play coin sound
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1
            play_sound("coin")

    # Got all 3 coins? I WIN!
    if score >= 3:
        game_state = "win"
        stop_sound("running_forest")
        stop_music()
        play_sound("win")

# This DRAWS everything on the screen (like painting a picture)
def draw():
    screen.clear()
    # Blue sky
    screen.fill((135, 206, 235))
    # Green grass
    screen.draw.filled_rect(Rect(0, GROUND, WIDTH, HEIGHT - GROUND), (34, 139, 34))

    # Draw the platforms (tile beams across the full width, clipped to fit)
    beam_width = 48
    for platform in platforms:
        screen.surface.set_clip(platform)
        x = platform.left
        while x < platform.right:
            screen.blit("beam.png", (x, platform.top))
            x += beam_width
        screen.surface.set_clip(None)

    # If I am on the menu game state, then draw the menu and return
    if game_state == "menu":
        draw_menu()
        return

    # Draw all the coins, the player, and the zombies
    for coin in coins: coin.draw()
    player.draw()
    for enemy in enemies: enemy.draw()

    # Show how many coins I have
    screen.draw.text(f"COINS: {score}/3", (10, 10), fontsize=30, color="white")
    screen.draw.text("ESC: Menu", (WIDTH - 120, 10), fontsize=20, color="white")

    # Show a message if I've won or lost
    if game_state in ("win", "lose"):
        screen.draw.filled_rect(Rect(100, 200, 600, 200), (0, 0, 0, 180))
        message, color = ("YOU WIN!", "gold") if game_state == "win" else ("GAME OVER", "red")
        screen.draw.text(message, center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color=color)
        screen.draw.text("Press R to restart", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30)

# This draws the MENU screen (the first thing I see)
def draw_menu():
    screen.draw.text("ZOMBIE PLATFORMER", center=(WIDTH // 2, 100), fontsize=50, color="darkgreen")
    button_color = (0, 100, 255) if sound_on else (100, 100, 100)
    # Draw 3 buttons: Start, Sound, and Exit
    for y, color, label in [(200, "green", "PLAY"), (280, button_color, f"SOUND: {'ON' if sound_on else 'OFF'}"),
                             (360, "red", "EXIT")]:
        screen.draw.filled_rect(Rect(300, y, 200, 50), color)
        screen.draw.text(label, center=(WIDTH // 2, y + 25), fontsize=30)
    screen.draw.text("Collect 3 coins to win!", center=(WIDTH // 2, 450), fontsize=25)
    screen.draw.text("Arrow keys to move, SPACE to jump", center=(WIDTH // 2, 480), fontsize=20)
    screen.draw.text("GAME TYPE: PLATFORMER", center=(WIDTH // 2, 550), fontsize=25, color="darkred")

# When I CLICK the mouse
def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == "menu" and 300 <= pos[0] <= 500:
        if 200 <= pos[1] <= 250: 
            game_state = "playing"      # Clicked START
            play_music()
        elif 280 <= pos[1] <= 330: sound_on = not sound_on    # Clicked SOUND
        elif 360 <= pos[1] <= 410: exit()                     # Clicked EXIT

# When I press a KEY on the keyboard
def on_key_down(key):
    global game_state, score
    # SPACE or UP arrow = JUMP!
    if key in (keys.SPACE, keys.UP) and game_state == "playing":
        player.jump()
    # Press R to play again after winning or losing
    if key == keys.R and game_state in ("win", "lose"):
        game_state = "playing"
        score = 0
        player.x = 100
        player.y = 420
        player.image = "player_idle"
        player.velocity_y = 0
        zombies[0].x, zombies[0].y = 280, 395
        alien.x, alien.y = 480, 322
        coins[:] = [Actor("coin", (150, 420)), Actor("coin", (400, 340)), Actor("coin", (650, 260))]
        play_music()
    # Press ESCAPE to go back to the menu
    if key == keys.ESCAPE:
        game_state = "menu"
        stop_sound("running_forest")
        stop_music()

# START THE GAME!
pgzrun.go()


