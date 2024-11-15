import pygame
import random
import cv2
import numpy as np

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze with Learning Agents")

# Set up video writer (OpenCV)
fps = 10  # Frames per second for recording
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('maze_with_agents.avi', fourcc, fps, (WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WALL_COLOR = (50, 50, 50)
AGENT_COLOR = (0, 150, 255)
START_COLOR = (0, 255, 0)
END_COLOR = (255, 0, 0)

# Agent settings
NUM_AGENTS = 5
AGENT_SIZE = 8

# Maze generation settings
START_POS = (0, 0)
END_POS = (GRID_WIDTH - 1, GRID_HEIGHT - 1)

# Maze generation function using recursive division
def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]

    def divide(x, y, w, h):
        if w <= 2 or h <= 2:
            return

        if w > h:
            # Vertical division
            wx = x + random.randint(1, w - 2)
            for i in range(h):
                maze[y + i][wx] = 0
            divide(x, y, wx - x, h)
            divide(wx + 1, y, x + w - wx - 1, h)
        else:
            # Horizontal division
            wy = y + random.randint(1, h - 2)
            for i in range(w):
                maze[wy][x + i] = 0
            divide(x, y, w, wy - y)
            divide(x, wy + 1, w, y + h - wy - 1)

    # Create outer walls and divide maze
    for i in range(width):
        maze[0][i] = maze[height - 1][i] = 0
    for i in range(height):
        maze[i][0] = maze[i][width - 1] = 0
    divide(1, 1, width - 2, height - 2)

    # Set start and end
    maze[START_POS[1]][START_POS[0]] = 0
    maze[END_POS[1]][END_POS[0]] = 0
    return maze

# Agent class
class Agent:
    def __init__(self, maze):
        self.x, self.y = START_POS
        self.maze = maze
        self.color = AGENT_COLOR
        self.path = []  # Path to keep track of the moves
        self.last_position = None  # To store the penultimate position

    def move(self):
        # Randomly move up, down, left, or right if there's no wall
        moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(moves)
        for dx, dy in moves:
            new_x, new_y = self.x + dx, self.y + dy
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                if self.maze[new_y][new_x] == 0 and (new_x, new_y) != self.last_position:
                    # Move to the new position
                    self.last_position = (self.x, self.y)  # Update last position
                    self.x, self.y = new_x, new_y
                    self.path.append((self.x, self.y))  # Track path
                    break

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), AGENT_SIZE)

    def at_end(self):
        return (self.x, self.y) == END_POS

# Create maze and agents
maze = generate_maze(GRID_WIDTH, GRID_HEIGHT)
agents = [Agent(maze) for _ in range(NUM_AGENTS)]

# Main loop
running = True
clock = pygame.time.Clock()
speed = 10  # Initial speed

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # '+' key
                speed += 1  # Increase speed
            elif event.key == pygame.K_MINUS:
                speed = max(1, speed - 1)  # Decrease speed, minimum 1

    # Clear screen
    screen.fill(BLACK)

    # Draw maze
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = WALL_COLOR if maze[y][x] == 1 else WHITE
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw start and end
    pygame.draw.rect(screen, START_COLOR, (START_POS[0] * CELL_SIZE, START_POS[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, END_COLOR, (END_POS[0] * CELL_SIZE, END_POS[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Update and draw each agent
    for agent in agents[:]:  # Loop over a copy to allow removal
        agent.move()
        agent.draw(screen)
        if agent.at_end():
            agents.remove(agent)  # Remove agent once it reaches the goal

    # Update display
    pygame.display.flip()

    # Capture frame and save it to video
    frame = pygame.surfarray.array3d(screen)  # Get the RGB frame from pygame screen
    frame = np.rot90(frame)  # Rotate frame if needed
    frame = np.flipud(frame)  # Flip frame vertically
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR format for OpenCV
    out.write(frame)  # Write frame to video file

    # Cap the frame rate
    clock.tick(speed)

# Release video writer and quit pygame
out.release()
pygame.quit()
