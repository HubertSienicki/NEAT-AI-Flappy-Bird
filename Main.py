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
    GAP = 165
    VEL = 10

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




def draw_window(win, birds, pipes, base, score):
    #Function for drawing a game window
    win.blit((BG_IMG),(0,0))

    for pipe in pipes:
        pipe.draw(win)
    
    #Text score drawing 
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update()

    

#Main function will work as our neural network
def main(genomes, config):
    nets = []
    ge = []
    birds = []

    #Initializing neural network
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)


    #Creating first instances
    base = Base(730)
    pipes = [Pipe(600)]
    
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    #Game loop
    run = True
    while run:
        #A clock tick for managing the game speed
        clock.tick(144)
        #Event listener for a spacebar, when I want to play and for quitting the game
        for event in pygame.event.get():
            #if event.type == pygame.KEYDOWN:
            #    if event.key == pygame.K_SPACE:
            #        bird.jump()

            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                
        
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        #Logic for adding and removing pipes
        for pipe in pipes:
            for x, bird in enumerate(birds):
                #Once one of the birds collide,  they immedietly get a fitness score of
                #-1 and gets deleted from the neural network
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()
        if add_pipe:
            score += 1

            #If the bird actually passes through the pipe, the get added a fitness score
            #of 5 in order to encourage them to pass through the pipes
            #rather than try to get to the end
            for g in ge:
                g.fitness += 5

            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score)
        

  

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    print(config_path)
    run(config_path)
    
