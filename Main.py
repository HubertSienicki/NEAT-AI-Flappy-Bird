import pygame
import neat
import time
import os
import random

from pygame.transform import rotate
#Initialization of constants
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]

PIPE_IMG =  pygame.transform.scale2x(pygame.image.load(
            os.path.join("imgs", "pipe.png")))

BASE_IMG =  pygame.transform.scale2x(pygame.image.load(
            os.path.join("imgs", "base.png")))

BG_IMG =    pygame.transform.scale2x(pygame.image.load(
            os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    #Bird class for the flappy bird instance
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        #pretty straightforward
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        #Method for moving the flappy bird
        self.tick_count += 1

        #Calculates the downward acceleration of a bird
        displacement = self.vel * self.tick_count + 1.5*self.tick_count**2
        
        if displacement >= 16:
            displacement = 16
        
        if displacement < 0 :
            displacement -= 2
        
        self.y = self.y + displacement
        
        #Upward tilt
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION

        #Downward tilt                  
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VELOCITY
    
    def draw(self,win):
        self.img_count += 1

        #This loops through three animations when the bird is suspended so that it looks like its flying
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        #No flapping when the bird is accelerating downwards
        if self.tilt<= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        #Image rotation method courtesy of STACKOVERFLOW <3
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        #Returning mask for collision detection
        return pygame.mask.from_surface(self.img)

class Pipe:
    #Class representing and instance of P I P E
    GAP = 200
    VEL = 5

    def __init__(self, x):
        #INITIALIZATOR
        self.x = x
        self.height = 0
        
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()
    
    def set_height(self):
        #Here, top of the screen is used to deremine the height of the pipe
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        #Straighforward
        self.x -= self.VEL

    def draw(self, win):
        #Also straighforward
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        #Returns False whether the instance of bird is not overlaping with a pipe
        #Returns True whether the instance of bird is overlaping with a pipe
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False

class Base:
    #Class for representing an instance of floor
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        #INITIALIZATION
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        #"Scrolling" of the floor
        #This works by creating two instances of floor that move at the same time
        #When floor one dissapeares of the screen, it is transferred to the back
        #This sort of works like moving and instance from List[0] to List[List.length()]
        #If you get what I mean
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        #Straightforward
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))




def draw_window(win, bird, pipes, base, score):
    #Function for drawing a game window
    win.blit((BG_IMG),(0,0))

    for pipe in pipes:
        pipe.draw(win)
    
    #Text score drawing 
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    bird.draw(win)
    pygame.display.update()

    


def main():
    #Main function for running the game logic

    #Creating first instances
    bird = Bird(230,350)
    base = Base(730)
    pipes = [Pipe(600)]
    
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    #Game loop
    run = True
    while run:
        #A clock tick for managing the game speed
        clock.tick(30)
        #Event listener for a spacebar, when I want to play and for quitting the game
        for event in pygame.event.get():
            #if event.type == pygame.KEYDOWN:
            #    if event.key == pygame.K_SPACE:
            #        bird.jump()

            if event.type == pygame.QUIT:
                run = False
                
        #bird.move()
        add_pipe = False
        rem = []
        #Logic for adding and removing pipes
        for pipe in pipes:
            if pipe.collide(bird):
                pass

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= 730:
            pass

        base.move()
        draw_window(win,bird, pipes, base, score)
        

    pygame.quit()
    quit()

main()