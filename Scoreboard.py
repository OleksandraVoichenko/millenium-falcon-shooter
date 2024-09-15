import pygame
from PIL.ImageChops import screen

FILE_PATH = './scores.txt'
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
BACKGROUND_COLOR = '#010210'
TEXT_COLOR = (240, 240, 240)

class Scoreboard:
    def __init__(self, num_last_scores=10):
        self.num_last_scores = num_last_scores
        self.leader_score, self.last_scores = self.load_scores()


    @staticmethod
    def time_to_seconds(time_str):
        """Convert a time string 'MM:SS' to total seconds."""
        minutes, seconds = map(int, time_str.split(':'))
        return minutes * 60 + seconds


    @staticmethod
    def seconds_to_time(seconds):
        """Convert total seconds to a 'MM:SS' string."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"


    def load_scores(self):
        """Loads scores from .txt file and organizes them into array for easy access"""
        scores = []
        try:
            with open(FILE_PATH, 'r') as file:
                for line in file:
                    line = line.strip()
                    try:
                        seconds = self.time_to_seconds(line)
                        scores.append((seconds, line))
                    except ValueError:
                        continue
            leader_score = max(scores, key=lambda x: x[0])[1] if scores else None
            last_scores = [score[1] for score in scores[-self.num_last_scores:]]
            return leader_score, last_scores
        except FileNotFoundError:
            return None, []


    def draw_scoreboard(self, screen, font):
        """Displays scores on screen in a form of list"""
        screen.fill(BACKGROUND_COLOR)

        if self.leader_score is not None:
            leader_text = font.render(f'Leader Score: {self.leader_score}', True, TEXT_COLOR)
            screen.blit(leader_text, (20, 20))

        y_offset = 120
        for index, score in enumerate(self.last_scores):
            score_text = font.render(f'{index + 1}. {score}', True, TEXT_COLOR)
            screen.blit(score_text, (20, y_offset))
            y_offset += 40
        back_button_rect = self.draw_back_button(screen, font)
        reset_button_rect = self.draw_reset_button(screen, font)
        pygame.display.flip()
        return back_button_rect, reset_button_rect


    @staticmethod
    def draw_back_button(screen, font):
        """Draws BACK button that sends player back to restart menu"""
        back_surf = font.render('BACK', True, TEXT_COLOR)
        back_rect = back_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 60))
        screen.blit(back_surf, back_rect)
        pygame.draw.rect(screen, TEXT_COLOR, back_rect.inflate(20, 20).move(0, -8), 5, 10)
        return back_rect

    @staticmethod
    def draw_reset_button(screen, font):
        """Draws RESET button that resets .txt file"""
        reset_surf = font.render('RESET', True, TEXT_COLOR)
        reset_rect = reset_surf.get_frect(center=(WINDOW_WIDTH / 2 + 120, WINDOW_HEIGHT - 60))
        screen.blit(reset_surf, reset_rect)
        pygame.draw.rect(screen, TEXT_COLOR, reset_rect.inflate(20, 20).move(0, -8), 5, 10)
        return reset_rect
