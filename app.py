import pygame
import neat
import time
import random
import os

pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 0

FPS = 60

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
			 pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
			 pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

DRAW_LINES = True

STAT_FONT = pygame.font.SysFont("comicsans", 50)



class Bird:
	"""
	Bird class representing the flappy bird
	"""
	MAX_ROTATION = 25
	IMGS = BIRD_IMGS
	ROT_VEL = 20
	ANIMATION_TIME = 5

	def __init__(self, x, y):
		"""
		Initialize the object
		:param x: starting x pos (int)
		:param y: starting y pos (int)
		:return: None
		"""
		self.x = x
		self.y = y
		self.tilt = 0  # degrees to tilt
		self.tick_count = 0
		self.vel = 0
		self.height = self.y
		self.img_count = 0
		self.img = self.IMGS[0]

	def jump(self):
		"""
		make the bird jump
		:return: None
		"""
		self.vel = -10.5
		self.tick_count = 0
		self.height = self.y

	def move(self):
		"""
		make the bird move
		:return: None
		"""
		self.tick_count += 1

		# for downward acceleration
		displacement = self.vel * (self.tick_count) + 0.5 * (3) * (self.tick_count) ** 2  # calculate displacement

		# terminal velocity
		if displacement >= 16:
			displacement = (displacement / abs(displacement)) * 16

		if displacement < 0:
			displacement -= 2

		self.y = self.y + displacement

		if displacement < 0 or self.y < self.height + 50:  # tilt up
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:  # tilt down
			if self.tilt > -90:
				self.tilt -= self.ROT_VEL

	def draw(self, win):
		"""
		draw the bird
		:param win: pygame window or surface
		:return: None
		"""
		self.img_count += 1

		# For animation of bird, loop through three images
		if self.img_count <= self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count <= self.ANIMATION_TIME * 2:
			self.img = self.IMGS[1]
		elif self.img_count <= self.ANIMATION_TIME * 3:
			self.img = self.IMGS[2]
		elif self.img_count <= self.ANIMATION_TIME * 4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME * 4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0

		# so when bird is nose diving it isn't flapping
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME * 2

		# tilt the bird
		blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

	def get_mask(self):
		"""
		gets the mask for the current image of the bird
		:return: None
		"""
		return pygame.mask.from_surface(self.img)



class Pipe:
	GAP = 200  # space between gaps
	VEL = 5

	def __init__(self, x):
		self.x = x
		self.height = 0
		self.gap = 100
		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)  # pipe upside down
		self.PIPE_BOTTOM = PIPE_IMG
		self.passed = False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	def collide(self, bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		# point of collision between bird mask and the bottom pipe
		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)

		if t_point or b_point:
			return True

		return False


def blitRotateCenter(surf, image, topleft, angle):
	"""
		Rotate a surface and blit it to the window
		:param surf: the surface to blit to
		:param image: the image surface to rotate
		:param topLeft: the top left position of the image
		:param angle: a float value for angle
		:return: None
		"""
	rotated_image = pygame.transform.rotate(image, angle)
	new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)

	surf.blit(rotated_image, new_rect.topleft)


# base of the game
class Base:
	"""
		Represnts the moving floor of the game
		"""
	VEL = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		"""
		Initialize the object
		:param y: int
		:return: None
		"""
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		"""
		move floor so it looks like its scrolling
		:return: None
		"""
		self.x1 -= self.VEL
		self.x2 -= self.VEL
		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		"""
		Draw the floor. This is two images that move together.
		:param win: the pygame surface/window
		:return: None
		"""
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
	"""
	draws the windows for the main game loop
	:param win: pygame window surface
	:param bird: a Bird object
	:param pipes: List of pipes
	:param score: score of the game (int)
	:param gen: current generation
	:param pipe_ind: index of closest pipe
	:return: None
	"""
	if gen == 0:
		gen = 1
	win.blit(BG_IMG, (0, 0))

	for pipe in pipes:
		pipe.draw(win)

	base.draw(win)
	for bird in birds:
		# draw lines from bird to pipe
		if DRAW_LINES:
			try:
				pygame.draw.line(win, (255, 0, 0),
								 (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
								 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width() / 2, pipes[pipe_ind].height),
								 5)
				pygame.draw.line(win, (255, 0, 0),
								 (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2), (
									 pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width() / 2,
									 pipes[pipe_ind].bottom), 5)
			except:
				pass
		# draw bird
		bird.draw(win)

	# score
	score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
	win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

	# generations
	score_label = STAT_FONT.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
	win.blit(score_label, (10, 10))

	# alive
	score_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
	win.blit(score_label, (10, 50))

	pygame.display.update()


def eval_genomes(genomes, config):
	global GEN
	GEN += 1
	nets = []
	ge = []
	birds = []

	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(230, 350))
		g.fitness = 0
		ge.append(g)

	base = Base(730)
	pipes = [Pipe(600)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	clock = pygame.time.Clock()  # set the clock . Frame Rate
	score = 0

	run = True
	while run:
		clock.tick(FPS)
		for event in pygame.event.get():
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

			output = nets[x].activate(
				(bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

			if output[0] > 0.5:
				bird.jump()

		add_pipe = False
		rem = []
		for pipe in pipes:
			for x, bird in enumerate(birds):  # get position in the list
				if pipe.collide(bird):
					ge[x].fitness -= 1  # every time a bird hits a pipe his fitness decrease by 1
					birds.pop(x)  # removes and return the last value of a list
					nets.pop(x)
					ge.pop(x)

				if not pipe.passed and pipe.x < bird.x:  # check if it passed the pipe
					pipe.passed = True
					add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)

			pipe.move()

		if add_pipe:
			score += 1
			for g in ge:
				g.fitness += 5
			pipes.append(Pipe(600))

		for r in rem:
			pipes.remove(r)

		for x, bird in enumerate(birds):
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0:  # a bird hits the ground
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)

		base.move()
		draw_window(win, birds, pipes, base, score, GEN, pipe_ind)


def run(config_path):
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
						 neat.DefaultSpeciesSet, neat.DefaultStagnation,
						 config_path)
	p = neat.Population(config)

	p.add_reporter(neat.StdOutReporter(True))

	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(eval_genomes, 50)  # num --> how many gen we need to run calls the main fun 50 thimes


if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "neat-config.txt")
	run(config_path)
