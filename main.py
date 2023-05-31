import pygame as py
import pymunk
import pymunk.pygame_util
import math as m

py.init()

# BG
BG = (50, 50, 50)
pocket_dia = 66
taking_shot= True
force = 0
powering_up = False
max_force = 10000
force_direction = 1
cue_ball_potted = False
lives = 3
game_running = True

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 678
BOTTOM = 60

screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT+BOTTOM))
py.display.set_caption("Pool")

font = py.font.SysFont("Lato", 30)
large_font = py.font.SysFont("Lato", 60)

#pymunk space
space = pymunk.Space()
static_body = space.static_body
# space.gravity = (0,981)
draw_options = pymunk.pygame_util.DrawOptions(screen)

#clock
clock = py.time.Clock()
FPS = 120

table_image = py.image.load("assets/images/table.png")
cue_image = py.image.load("assets/images/cue.png")
ball_images = []
for i in range(1,17):
    ball_image = py.image.load(f"assets/images/ball_{i}.png")
    ball_images.append(ball_image)

# fun for balls
def create_ball(radius, pos):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = 5
    shape.elasticity = 0.995
    # use pivot joint to create friction
    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_bias = 0
    pivot.max_force = 1000

    space.add(body, shape, pivot)
    return shape


#pool balls
balls = []
rows = 5
#potting balls
for col in range(5):
    for row in range(rows):
        pos = (250 + col*37, 267 + (row*37)+(col*18))
        new_ball = create_ball(18, pos)
        balls.append(new_ball)
    rows -= 1



cue_ball = create_ball(18, (888, SCREEN_HEIGHT/2))
balls.append(cue_ball)

#cushions coor
cushions = [
  [(88, 56), (109, 77), (555, 77), (564, 56)],
  [(621, 56), (630, 77), (1081, 77), (1102, 56)],
  [(89, 621), (110, 600),(556, 600), (564, 621)],
  [(622, 621), (630, 600), (1081, 600), (1102, 621)],
  [(56, 96), (77, 117), (77, 560), (56, 581)],
  [(1143, 96), (1122, 117), (1122, 560), (1143, 581)]
]
pockets = [
  (55, 63),
  (592, 48),
  (1134, 64),
  (55, 616),
  (592, 629),
  (1134, 616)
]
#cushions
def create_cushions(poly_coor):
    body = pymunk.Body(body_type = pymunk.Body.STATIC)
    body.pos = ((0, 0))
    shape = pymunk.Poly(body, poly_coor)
    shape.elasticity = 0.8
    space.add(body, shape)
    
for c in cushions:
    create_cushions(c)

#create cue
class Cue():
    def __init__(self, pos):
        self.original_image = cue_image
        self.angle = 0
        self.image = py.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self, angle):
        self.angle = angle
    def draw(self, surface):
        self.image = py.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image, (self.rect.centerx- self.image.get_width()/2, self.rect.centery - self.image.get_height()/2))

cue = Cue(balls[-1].body.position)

power_bar = py.Surface((10, 20))
power_bar.fill((255, 0, 0))

potted_balls = []

def text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

run = True
while(run):

    clock.tick(FPS)
    space.step(1 / FPS)

    screen.fill(BG)

    screen.blit(table_image, (0, 0))

    for i, ball in enumerate(balls):
        for p in pockets:
            ball_x_dist = abs(ball.body.position[0] - p[0])
            ball_y_dist = abs(ball.body.position[1] - p[1])
            ball_dist = m.sqrt((ball_x_dist*ball_x_dist)+(ball_y_dist*ball_y_dist))
            if ball_dist <= pocket_dia / 2:
                if (i==len(balls)-1):
                    cue_ball_potted = True
                    ball.body.posiyion = (-100, -100)
                    ball.body.velocity = (0.0, 0.0)
                    lives -= 1
                    
                else:
                    space.remove(ball.body)
                    balls.remove(ball)
                    potted_balls.append(ball_images[i])
                    ball_images.pop(i)
                
    for i, ball in enumerate(balls):
        screen.blit(ball_images[i], (ball.body.position[0] - 18, ball.body.position[1] - 18))

    taking_shot = True
    for ball in balls:
        if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0:
            taking_shot = False


    if taking_shot == True and game_running == True:
        if cue_ball_potted == True:
            
            balls[-1].body.position = (888, SCREEN_HEIGHT/2)
        mouse_pos = py.mouse.get_pos()
        cue.rect.center = balls[-1].body.position
        x_dist = balls[-1].body.position[0] - mouse_pos[0]
        y_dist = -(balls[-1].body.position[1] - mouse_pos[1])
        cue_angle = m.degrees(m.atan2(y_dist, x_dist))
        cue.update(cue_angle)
        cue.draw(screen)
    if powering_up:
        force += 100*force_direction
        if force >= max_force or force <= 0:
            force_direction *= -1
        for b in range(m.ceil(force / 2000)):
            screen.blit(power_bar, (balls[-1].body.position[0] + (b*15) - 25, balls[-1].body.position[1]+30))
    elif powering_up == False and taking_shot == True:
        x_impulse = m.cos(m.radians(cue_angle))
        y_impulse = m.sin(m.radians(cue_angle))
        balls[-1].body.apply_impulse_at_local_point((-(force*x_impulse), force*y_impulse), (0, 0))
        force = 0
        force_direction = 1

    for i, p in enumerate(potted_balls):
        screen.blit(p, (10 + i*50, SCREEN_HEIGHT + 10))

    text("LIVES: " + str(lives), font, (255, 255, 255), SCREEN_WIDTH - 200, SCREEN_HEIGHT + 10)

    if lives <= 0 or len(balls) == 1:
        text("GAME OVER", large_font, (255, 0, 0), SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT/2 - 50)
        game_running = False 

    for event in py.event.get():
        if event.type == py.MOUSEBUTTONDOWN and taking_shot == True:
            powering_up = True
        if event.type == py.MOUSEBUTTONUP and taking_shot == True:
            powering_up = False

        if event.type == py.QUIT:
            run = False
    # space.debug_draw(draw_options)
    py.display.update()


py.quit()

