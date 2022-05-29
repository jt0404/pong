import pygame as pg 
import random 
import pandas as pd
from time import sleep
from sklearn.neighbors import KNeighborsRegressor

from c import *


pg.init()


class Player:
    SCORE_FONT = pg.font.SysFont('Arial', 60)
    SCOREY = BORDER_HEIGHT + 5


    def __init__(self, paddle):
        self.paddle = paddle
        self.score = 0 
        self.key_pressed = 0
         

    def draw_score(self, screen):
        t = self.SCORE_FONT.render(str(self.score), True, SCORE_COLOR)
        if self.paddle.x == 20:
            scorex = SCR_WIDTH//2 - t.get_width() - 50
        else:
            scorex = LINEX + t.get_width() + 20
        screen.blit(t, (scorex, self.SCOREY))

    
    def update_score(self):
        self.score += 1


    def move_paddle(self):
        self.paddle.move()


class Paddle:
    def __init__(self, x):
        self.x = x 
        self.start_x = self.x
        self.y = SCR_HEIGHT//2 - PADDLE_HEIGHT//2
        self.start_y = self.y
        self.vy = 0
        

    def draw(self, screen):
        pg.draw.rect(screen, WHITE, (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT))


    def reset(self):
        self.x = self.start_x
        self.y = self.start_y


    def change_vel(self, dir):
        if dir == 'up' and self.vy != -6:
            self.vy = -6
        elif dir == 'down' and self.vy != 6:
            self.vy = 6


    def reset_vel(self):
        if self.vy:
            self.vy = 0


    def move(self):
        if self.y <= BORDER_HEIGHT:
            self.y = BORDER_HEIGHT
        if self.y >= SCR_HEIGHT - BORDER_HEIGHT - PADDLE_HEIGHT:
            self.y = SCR_HEIGHT - BORDER_HEIGHT - PADDLE_HEIGHT
        self.y += self.vy
        

class Ball: 
    RADIUS = 7
    

    def __init__(self):
        self.x = SCR_WIDTH//2 + random.choice((-1, 1))
        self.y = 183
        self.velx = -8 if self.x > SCR_WIDTH//2 else 8 
        self.vely = -8

    
    def draw(self, screen):
        pg.draw.circle(screen, WHITE, (self.x, self.y), self.RADIUS)


    def change_vel(self, dir):
        if dir == 'x':
            self.velx *= -1 
        else:
            self.vely *= -1


    def collide_width_border(self):
        return self.y - self.RADIUS <= BORDER_HEIGHT or self.y + self.RADIUS >= SCR_HEIGHT - BORDER_HEIGHT


    def collide_with_paddle(self, paddle1, paddle2):
        return (self.x - self.RADIUS > paddle1.x + PADDLE_WIDTH//2 and self.x - self.RADIUS < paddle1.x + PADDLE_WIDTH) \
            and (self.y > paddle1.y and self.y < paddle1.y + PADDLE_HEIGHT) \
                or (self.x + self.RADIUS > paddle2.x and self.x + self.RADIUS < paddle2.x + PADDLE_WIDTH // 2) \
                    and (self.y > paddle2.y and self.y < paddle2.y + PADDLE_HEIGHT)  


    def out_of_bounds(self, paddle1, paddle2):
        return (self.x > paddle2.x + PADDLE_WIDTH) or (self.x < paddle1.x)


    def reset(self):
        self.x = SCR_WIDTH//2 + random.choice((-1, 1))
        self.velx = -8 if self.x > SCR_WIDTH//2 else 8 
        self.y = 183


    def move(self):
        self.x += self.velx
        self.y += self.vely


def draw_borders(screen):
    for i in range(2):
        pg.draw.rect(screen, WHITE, (0, i * SCR_HEIGHT - i * BORDER_HEIGHT, BORDER_WIDTH, BORDER_HEIGHT))


def draw_line(screen):
    for i in range(10):
        pg.draw.rect(screen, WHITE, (LINEX, BORDER_HEIGHT + i * LINE_HEIGHT + i * 10, LINE_WIDTH, LINE_HEIGHT))


def draw_paddles(screen, paddle1, paddle2):
    paddle1.draw(screen)
    paddle2.draw(screen)


def draw_scores(screen, player1, player2):
    player1.draw_score(screen)
    player2.draw_score(screen)


def draw_options_screen(screen):
    font = pg.font.SysFont('Arial', 32)
    for i in range(2):
        x = SCR_WIDTH//2 - OPTION_BUTTON_WIDTH//2
        y = 125 + i * (OPTION_BUTTON_HEIGHT + 10)
        pg.draw.rect(screen, WHITE, (x, y, OPTION_BUTTON_WIDTH, OPTION_BUTTON_HEIGHT), 1)
        text = font.render(f'{i + 1} PLAYER' + 'S' * i, False, WHITE)
        screen.blit(text, (x + OPTION_BUTTON_WIDTH//2 - text.get_width()//2, y + OPTION_BUTTON_HEIGHT//2 - text.get_height()//2))


def click_option_button(game_started, play_ai):
    mx, my = pg.mouse.get_pos()
    lowerx = SCR_WIDTH//2 - OPTION_BUTTON_WIDTH//2
    upperx = lowerx + OPTION_BUTTON_WIDTH
    lowery = 125 
    uppery = lowery + OPTION_BUTTON_HEIGHT
    if mx in range(lowerx, upperx) and my in range(lowery, uppery):
        return (True, True)
    elif mx in range(lowerx, upperx) and my in range(lowery + 10 + OPTION_BUTTON_HEIGHT, uppery + 10 + OPTION_BUTTON_HEIGHT):
        return (True, False) 
    return (False, False)


def draw(screen, paddle1, paddle2, player1, player2, ball, game_started):
    screen.fill(BLACK)
    if not game_started:
        draw_options_screen(screen)
    else:
        draw_borders(screen)
        draw_line(screen)
        draw_paddles(screen, paddle1, paddle2)
        draw_scores(screen, player1, player2)
        ball.draw(screen)
    pg.display.update()


def move(player1, player2, ball):
    player1.move_paddle()
    player2.move_paddle()
    ball.move()


def update_score(ball, player1, player2):
    if ball.velx < 0:
        player2.update_score()
    else:
        player1.update_score()


def handle_ball(ball, paddle1, paddle2, player1, player2, wall_sound, score_sound, paddle_sound):
    if ball.collide_with_paddle(paddle1, paddle2):
        paddle_sound.play()
        ball.change_vel('x')
    if ball.collide_width_border():
        wall_sound.play()
        ball.change_vel('y')
    if ball.out_of_bounds(paddle1, paddle2):
        score_sound.play()
        update_score(ball, player1, player2)
        ball.reset() 
        paddle1.reset()
        paddle2.reset()


def read_data():
    data = pd.read_csv('data.csv')
    data = data.drop_duplicates()
    x = data.drop(columns='paddley')
    y = data['paddley']
    return (x, y)


def initialize_regressor():
    clf = KNeighborsRegressor(n_neighbors=3)
    x, y = read_data()
    clf = clf.fit(x, y)
    return clf 


def ai(df, clf, ballx, bally, velx, vely, paddle1):
    to_predict = df.append({'ballx': ballx, 'bally': bally, 'velx': velx, 'vely': vely}, ignore_index=True)
    should_move = clf.predict(to_predict)
    if paddle1.y < should_move[0]:
        paddle1.change_vel('down')
    else:
        paddle1.change_vel('up')


def main():
    screen = pg.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
    game_started = False 
    play_ai = False 
    clock = pg.time.Clock()
    run = True 
    paddle1 = Paddle(20)
    paddle2 = Paddle(SCR_WIDTH - PADDLE_WIDTH - 20)
    player1 = Player(paddle1)
    player2 = Player(paddle2)
    ball = Ball()
    wall_sound = pg.mixer.Sound('sounds/wall.wav')
    score_sound = pg.mixer.Sound('sounds/score.wav')
    paddle_sound = pg.mixer.Sound('sounds/paddle.wav')
    ai_initialized = False

    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False 
                quit()
            if event.type == pg.MOUSEBUTTONDOWN and not game_started:
                if event.button == 1:
                    game_started, play_ai = click_option_button(game_started, play_ai)
            if event.type == pg.KEYDOWN and game_started:
                if not play_ai:
                    if event.key == pg.K_w:
                        player1.paddle.change_vel('up')
                        player1.key_pressed += 1
                    if event.key == pg.K_s:
                        player1.paddle.change_vel('down')
                        player1.key_pressed += 1
                if event.key == pg.K_UP:
                    player2.paddle.change_vel('up')
                    player2.key_pressed += 1
                if event.key == pg.K_DOWN:
                    player2.paddle.change_vel('down')
                    player2.key_pressed += 1
            if event.type == pg.KEYUP and game_started:
                if not play_ai:
                    if event.key == pg.K_w or event.key == pg.K_s:
                        if player1.key_pressed < 2:
                            player1.paddle.reset_vel()
                        player1.key_pressed -= 1
                if event.key == pg.K_UP or event.key == pg.K_DOWN:
                    if player2.key_pressed < 2:
                        player2.paddle.reset_vel()
                    player2.key_pressed -= 1

        if game_started:
            if play_ai:
                if not ai_initialized:
                    df = pd.DataFrame(columns=['ballx', 'bally', 'velx', 'vely'])
                    clf = initialize_regressor()
                ai(df, clf, ball.x, ball.y, ball.velx, ball.vely, paddle1)
            handle_ball(ball, paddle1, paddle2, player1, player2, wall_sound, score_sound, paddle_sound)
            move(player1, player2, ball)
            
        draw(screen, paddle1, paddle2, player1, player2, ball, game_started)
        clock.tick(FPS)


if __name__ == '__main__':
    main()