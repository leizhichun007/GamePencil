import pygame
import math
import random
import os
import sys
from pygame import gfxdraw  # 用于绘制抗锯齿图形
from enum import Enum

# 设置 UTF-8 编码
pygame.init()
pygame.font.init()

# 尝试加载中文字体
def get_chinese_font(size):
    try:
        # Windows 系统字体路径
        font_paths = [
            "C:\\Windows\\Fonts\\msyh.ttc",  # 微软雅黑
            "C:\\Windows\\Fonts\\simhei.ttf",  # 黑体
            "C:\\Windows\\Fonts\\simsun.ttc",  # 宋体
        ]
        
        # 尝试加载系统字体
        for path in font_paths:
            if os.path.exists(path):
                return pygame.font.Font(path, size)
        
        # 如果找不到系统字体，尝试使用 pygame 默认中文字体
        return pygame.font.SysFont('microsoftyahei', size)
    except:
        # 如果都失败了，使用默认字体
        return pygame.font.Font(None, size)

# 设置窗口
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("球类对战游戏")

# 获取系统字体路径
def get_font_path():
    if sys.platform.startswith('win'):
        # Windows系统字体路径
        font_paths = [
            "C:\\Windows\\Fonts\\msyh.ttc",  # 微软雅黑
            "C:\\Windows\\Fonts\\simhei.ttf",  # 黑体
            "C:\\Windows\\Fonts\\simsun.ttc",  # 宋体
        ]
        for path in font_paths:
            if os.path.exists(path):
                return path
    return None

# 创建字体对象
def create_font(size):
    font_path = get_font_path()
    try:
        if font_path:
            return pygame.font.Font(font_path, size)
        else:
            # 如果找不到系统字体，尝试使用系统默认中文字体
            return pygame.font.SysFont('microsoftyahei', size)
    except:
        # 如果都失败了，使用默认字体
        return pygame.font.Font(None, size)

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

# 球的属性
BALL_RADIUS = 25
ARROW_LENGTH_MIN = 30
ARROW_LENGTH_MAX = 100
POWER_CHANGE_SPEED = 2
FRICTION = 0.98
ROTATION_SPEED = 3

# 添加更多颜色定义
COLORS = {
    'background': (240, 240, 245),  # 淡蓝灰色背景
    'grid': (230, 230, 235),        # 网格线颜色
    'panel': (255, 255, 255, 180),  # 半透明面板
    'title': (60, 60, 80),          # 标题文字颜色
    'accent': (65, 105, 225),       # 强调色
    'player': (30, 144, 255),       # 玩家球颜色
    'computer': (220, 20, 60),      # 电脑球颜色
    'power_bar': (46, 204, 113)     # 力量条颜色
}

# 定义道具类型
class PowerUpType(Enum):
    SPEED_UP = "加快旋转"     # 坏球 - 红色
    SPEED_DOWN = "减慢旋转"   # 好球 - 绿色
    POWER_UP = "增加强度"     # 好球 - 绿色
    POWER_DOWN = "减小强度"   # 坏球 - 红色
    SIZE_UP = "增大球体"      # 坏球 - 红色
    SIZE_DOWN = "缩小球体"    # 好球 - 绿色
    RESET_POSITION = "回到起点" # 中性 - 黑色
    RANDOM = "随机效果"       # 神秘 - 白色带黑边

class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (100, 100, 100)  # 障碍物颜色
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # 添加边缘效果
        pygame.draw.rect(screen, (80, 80, 80), self.rect, 2)

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(list(PowerUpType))  # 随机选择任意效果
        self.is_mystery = random.random() < 0.3  # 30%概率是问号球
        
        # 设置基础属性
        self.radius = 15
        self.color = (255, 255, 255)
        self.outline_color = (0, 0, 0)
        self.lifetime = 45000
        self.collected = False
        self.font = create_font(14)
        self.creation_time = pygame.time.get_ticks()
        
        # 根据效果类型设置特定属性
        if self.is_mystery:
            # 问号球：白色带黑边
            self.color = (255, 255, 255)
            self.outline_color = (0, 0, 0)
            self.radius = random.randint(15, 20)
            self.lifetime = random.randint(40000, 50000)
        else:
            if self.type in [PowerUpType.SPEED_UP, PowerUpType.POWER_DOWN, PowerUpType.SIZE_UP]:
                # 负面效果：红色，大球
                self.color = (255, 80, 80)
                self.outline_color = (255, 80, 80)
                self.radius = random.randint(20, 25)
                self.lifetime = random.randint(50000, 60000)
            elif self.type in [PowerUpType.SPEED_DOWN, PowerUpType.POWER_UP, PowerUpType.SIZE_DOWN]:
                # 正面效果：绿色，小球
                self.color = (80, 255, 80)
                self.outline_color = (80, 255, 80)
                self.radius = random.randint(12, 15)
                self.lifetime = random.randint(30000, 40000)
            elif self.type == PowerUpType.RESET_POSITION:
                # 重置位置：黑色，中等大小
                self.color = (50, 50, 50)
                self.outline_color = (50, 50, 50)
                self.radius = random.randint(15, 18)
                self.lifetime = random.randint(40000, 50000)

    def draw(self, screen):
        if self.collected:
            return
            
        # 脉动效果
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 2
        actual_radius = self.radius + pulse
        
        # 设置默认文字
        text = "?"
        
        if self.is_mystery:
            # 问号球：白色填充 + 黑色边框
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 
                             int(actual_radius))
            pygame.draw.circle(screen, self.outline_color, (int(self.x), int(self.y)), 
                             int(actual_radius), 2)
        else:
            # 其他球：实心填充
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 
                             int(actual_radius))
            # 根据效果类型设置文字
            if self.type == PowerUpType.SPEED_UP:
                text = "快"
            elif self.type == PowerUpType.SPEED_DOWN:
                text = "慢"
            elif self.type == PowerUpType.POWER_UP:
                text = "强"
            elif self.type == PowerUpType.POWER_DOWN:
                text = "弱"
            elif self.type == PowerUpType.SIZE_UP:
                text = "大"
            elif self.type == PowerUpType.SIZE_DOWN:
                text = "小"
            elif self.type == PowerUpType.RESET_POSITION:
                text = "回"
            elif self.type == PowerUpType.RANDOM:
                text = "?"
        
        # 绘制文字
        text_surface = self.font.render(text, True, 
                                      self.outline_color if self.is_mystery else (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)
        
        # 显示剩余时间
        current_time = pygame.time.get_ticks()
        remaining_time = (self.lifetime - (current_time - self.creation_time)) // 1000
        if remaining_time <= 5:
            time_text = self.font.render(str(remaining_time), True, 
                                       self.outline_color if self.is_mystery else (255, 255, 255))
            time_rect = time_text.get_rect(center=(self.x, self.y - self.radius - 15))
            screen.blit(time_text, time_rect)

class AI:
    def __init__(self):
        self.difficulty = "normal"  # easy, normal, hard
        self.accuracy = 0.8  # 命中率基准
        self.min_power = ARROW_LENGTH_MIN
        self.max_power = ARROW_LENGTH_MAX

    def calculate_shot(self, computer_ball, player_ball):
        """计算最佳射击角度和力量"""
        dx = player_ball.x - computer_ball.x
        dy = player_ball.y - computer_ball.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # 基础角度计算
        base_angle = math.degrees(math.atan2(dy, dx))
        
        # 根据难度添加随机偏移
        if self.difficulty == "easy":
            angle_offset = random.uniform(-20, 20)
            self.accuracy = 0.6
        elif self.difficulty == "normal":
            angle_offset = random.uniform(-10, 10)
            self.accuracy = 0.8
        else:  # hard
            angle_offset = random.uniform(-5, 5)
            self.accuracy = 0.95

        # 计算最终角度
        final_angle = base_angle + angle_offset
        
        # 计��力量
        ideal_power = min(distance / 5, self.max_power)
        power_variation = ideal_power * (1 - self.accuracy)
        final_power = ideal_power + random.uniform(-power_variation, power_variation)
        final_power = max(self.min_power, min(final_power, self.max_power))
        
        return final_angle, final_power

    def predict_collision(self, ball1_pos, ball2_pos, velocity, angle):
        """预测是否会发生碰撞"""
        future_x = ball1_pos[0] + math.cos(math.radians(angle)) * velocity
        future_y = ball1_pos[1] + math.sin(math.radians(angle)) * velocity
        
        distance = math.sqrt((future_x - ball2_pos[0])**2 + (future_y - ball2_pos[1])**2)
        return distance < BALL_RADIUS * 2

class Background:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid_size = 50
        
    def draw(self, screen):
        # 填充背景色
        screen.fill(COLORS['background'])
        
        # 绘制网格
        for x in range(0, self.width, self.grid_size):
            pygame.draw.line(screen, COLORS['grid'], (x, 0), (x, self.height))
        for y in range(0, self.height, self.grid_size):
            pygame.draw.line(screen, COLORS['grid'], (0, y), (self.width, y))
        
        # 绘制装饰性圆形
        for _ in range(20):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(5, 20)
            alpha = random.randint(20, 40)
            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*COLORS['grid'], alpha), (radius, radius), radius)
            screen.blit(s, (x-radius, y-radius))

class Game:
    def __init__(self):
        # 初始化基本属性
        self.obstacles = []  # 添加障碍物列表
        self.power_ups = []  # 道具列表
        self.last_powerup_time = pygame.time.get_ticks()
        self.powerup_interval = random.randint(5000, 10000)
        self.max_power_ups = 10
        
        # 使用中文字体
        self.font = get_chinese_font(36)
        self.small_font = get_chinese_font(24)
        
        # 创建按钮时使用中文字体
        self.quit_button = Button(WINDOW_WIDTH - 120, 20, 100, 40, "退出", RED, self.small_font)
        
        # 创建AI
        self.ai = AI()
        
        # 创建背景
        self.background = Background(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # 重置游戏状态
        self.reset_game()

    def reset_game(self):
        """重置游戏状态"""
        # 创建玩家和电脑的球
        self.player_ball = Ball(WINDOW_WIDTH * 0.2, WINDOW_HEIGHT/2, BLUE)
        self.computer_ball = Ball(WINDOW_WIDTH * 0.8, WINDOW_HEIGHT/2, RED)
        
        # 重置游戏状态
        self.game_over = False
        self.winner = None
        self.current_turn = "player"
        self.computer_state = "waiting"
        self.computer_aiming_time = 0
        
        # 清空并重新生成道具和障碍物
        self.power_ups.clear()
        self.obstacles.clear()
        self.last_powerup_time = pygame.time.get_ticks()
        self.generate_obstacles()

    def generate_obstacles(self):
        """生成障碍物"""
        # 定义安全区域（不生成障碍物的区域）
        safe_zones = [
            pygame.Rect(0, WINDOW_HEIGHT/2 - 100, WINDOW_WIDTH * 0.3, 200),  # 左侧安全区
            pygame.Rect(WINDOW_WIDTH * 0.7, WINDOW_HEIGHT/2 - 100, WINDOW_WIDTH * 0.3, 200)  # 右侧安全区
        ]
        
        # 生成随机数量的障碍物
        num_obstacles = random.randint(5, 10)
        for _ in range(num_obstacles):
            attempts = 0
            max_attempts = 50  # 最大尝试次数
            
            while attempts < max_attempts:
                width = random.randint(30, 80)
                height = random.randint(30, 80)
                x = random.randint(0, WINDOW_WIDTH - width)
                y = random.randint(0, WINDOW_HEIGHT - height)
                new_obstacle = pygame.Rect(x, y, width, height)
                
                # 检查是否与安全区域重叠
                if not any(new_obstacle.colliderect(zone) for zone in safe_zones):
                    # 检查是否与其他障碍物重叠
                    if not any(new_obstacle.colliderect(obs.rect) for obs in self.obstacles):
                        self.obstacles.append(Obstacle(x, y, width, height))
                        break
                
                attempts += 1

    def generate_power_up(self):
        current_time = pygame.time.get_ticks()
        
        # 清理已收集或过期的道具
        active_power_ups = []
        for power_up in self.power_ups:
            if not power_up.collected and (current_time - power_up.creation_time) < power_up.lifetime:
                active_power_ups.append(power_up)
        self.power_ups = active_power_ups
        
        # 如果当前道具数量小于最大值，且达到生成间隔，尝试生成新道具
        if (len(self.power_ups) < self.max_power_ups and 
            current_time - self.last_powerup_time >= self.powerup_interval):
            
            # 随机决定是否生成新道具（50%概率）
            if random.random() < 0.5:
                self.try_generate_new_powerup(current_time)
            
            # 无论是否生成成功，都更新最后生成时间和下一个检查间隔
            self.last_powerup_time = current_time
            self.powerup_interval = random.randint(5000, 10000)

    def try_generate_new_powerup(self, current_time):
        """尝试在合适的位置生成新道具"""
        attempts = 0
        max_attempts = 10  # 最大尝试次数
        
        while attempts < max_attempts:
            x = random.randint(50, WINDOW_WIDTH - 50)
            y = random.randint(50, WINDOW_HEIGHT - 50)
            
            # 创建检测区域（比实际道具大一些）
            check_radius = 30
            
            # 检查是否与障碍物重叠
            valid_position = True
            for obstacle in self.obstacles:
                if obstacle.rect.collidepoint(x, y):
                    valid_position = False
                    break
            
            # 检查是否与其他道具太近
            if valid_position:
                for power_up in self.power_ups:
                    if math.hypot(x - power_up.x, y - power_up.y) < check_radius * 2:
                        valid_position = False
                        break
            
            # 检查是否在玩家或电脑球的范围内
            if valid_position:
                for ball in [self.player_ball, self.computer_ball]:
                    if math.hypot(x - ball.x, y - ball.y) < check_radius + ball.radius:
                        valid_position = False
                        break
            
            if valid_position:
                self.power_ups.append(PowerUp(x, y))
                return True
            
            attempts += 1
        
        return False

    def check_power_up_collisions(self, ball):
        """检查球与道具的碰撞并应用效果"""
        for power_up in self.power_ups:
            if not power_up.collected:
                distance = math.hypot(ball.x - power_up.x, ball.y - power_up.y)
                if distance < ball.radius + power_up.radius:
                    effect_type = power_up.type
                    if power_up.is_mystery:
                        effect_type = PowerUpType.RANDOM
                    ball.apply_effect(effect_type)
                    power_up.collected = True
                    print(f"收集道具: {'随机效果' if power_up.is_mystery else effect_type.value}")
                    
                    # 如果是重置位置效果，特殊处理回合
                    if effect_type == PowerUpType.RESET_POSITION:
                        if self.current_turn == "player":
                            self.current_turn = "computer"
                            self.computer_state = "waiting"
                            self.player_ball.turn_complete = True
                            self.computer_ball.turn_complete = False
                            print("玩家重置位置，回合切换到电脑")
                        else:
                            self.current_turn = "player"
                            self.computer_ball.turn_complete = True
                            self.player_ball.turn_complete = False
                            print("电脑重置位置，回合切换到玩家")

    def check_collision(self):
        dx = self.player_ball.x - self.computer_ball.x
        dy = self.player_ball.y - self.computer_ball.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < BALL_RADIUS * 2:
            if self.player_ball.is_moving:
                self.winner = "玩家"
            elif self.computer_ball.is_moving:
                self.winner = "电脑"
            self.game_over = True

    def computer_play(self):
        """改进的电脑AI逻辑"""
        if self.computer_state == "waiting":
            self.computer_state = "aiming"
            self.computer_ball.is_aiming = True
            self.computer_aiming_time = 0
            
            # 计算最佳射击角度和力量
            target_x = self.player_ball.x
            target_y = self.player_ball.y
            
            # 检查是否有障碍物阻挡
            dx = target_x - self.computer_ball.x
            dy = target_y - self.computer_ball.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # 如果有障碍物，尝试寻找替代路径
            has_obstacle = False
            for obstacle in self.obstacles:
                if self.check_line_obstacle_collision(
                    self.computer_ball.x, self.computer_ball.y,
                    target_x, target_y,
                    obstacle.rect
                ):
                    has_obstacle = True
                    break
            
            if has_obstacle:
                # 寻找替代目标点
                angles = [a for a in range(0, 360, 30)]  # 每30度检查一个方向
                random.shuffle(angles)  # 随机化方向
                for angle in angles:
                    rad = math.radians(angle)
                    test_x = self.computer_ball.x + math.cos(rad) * distance
                    test_y = self.computer_ball.y + math.sin(rad) * distance
                    if not any(self.check_line_obstacle_collision(
                        self.computer_ball.x, self.computer_ball.y,
                        test_x, test_y,
                        obstacle.rect
                    ) for obstacle in self.obstacles):
                        target_x = test_x
                        target_y = test_y
                        break
            
            # 计算最终角度和力量
            dx = target_x - self.computer_ball.x
            dy = target_y - self.computer_ball.y
            self.target_angle = math.degrees(math.atan2(dy, dx))
            self.target_power = min(
                distance * 0.5,  # 根据距离调整力量
                self.computer_ball.max_power
            )
            
        elif self.computer_state == "aiming":
            # 平滑转向目标角度
            angle_diff = (self.target_angle - self.computer_ball.angle) % 360
            if angle_diff > 180:
                angle_diff -= 360
            
            if abs(angle_diff) > self.computer_ball.rotation_speed:
                if angle_diff > 0:
                    self.computer_ball.angle += self.computer_ball.rotation_speed
                else:
                    self.computer_ball.angle -= self.computer_ball.rotation_speed
            else:
                self.computer_ball.angle = self.target_angle
                self.computer_aiming_time += 1
                
            if self.computer_aiming_time >= 30:
                self.computer_state = "power"
                self.computer_ball.is_aiming = False
                self.computer_ball.is_power_adjusting = True
                self.computer_aiming_time = 0
                
        elif self.computer_state == "power":
            # 调整到目标力量
            if abs(self.computer_ball.power - self.target_power) > POWER_CHANGE_SPEED:
                if self.computer_ball.power < self.target_power:
                    self.computer_ball.power += POWER_CHANGE_SPEED
                else:
                    self.computer_ball.power -= POWER_CHANGE_SPEED
            else:
                self.computer_ball.power = self.target_power
                self.computer_state = "shooting"
                self.computer_ball.shoot()

    def check_line_obstacle_collision(self, x1, y1, x2, y2, obstacle_rect):
        """检查线段是否与矩形障碍物相交"""
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        def intersect(A, B, C, D):
            return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

        # 检查线段是否与矩形的四条边相交
        rect_points = [
            (obstacle_rect.left, obstacle_rect.top),
            (obstacle_rect.right, obstacle_rect.top),
            (obstacle_rect.right, obstacle_rect.bottom),
            (obstacle_rect.left, obstacle_rect.bottom)
        ]
        
        line_start = (x1, y1)
        line_end = (x2, y2)
        
        for i in range(4):
            if intersect(
                line_start, line_end,
                rect_points[i], rect_points[(i + 1) % 4]
            ):
                return True
        return False

    def update(self):
        """更新游戏状态"""
        self.player_ball.update()
        self.computer_ball.update()
        self.check_collision()
        self.generate_power_up()
        
        if not self.game_over:
            # 处理回合转换
            if self.current_turn == "player":
                if self.player_ball.turn_complete:
                    self.current_turn = "computer"
                    self.computer_state = "waiting"
                    self.player_ball.turn_complete = False
                    # 确保电脑球准备好下一回合
                    self.computer_ball.is_moving = False
                    self.computer_ball.turn_complete = False
                    print("回合切换到电脑")
            elif self.current_turn == "computer":
                if not self.computer_ball.is_moving:
                    self.computer_play()
                if self.computer_ball.turn_complete:
                    self.current_turn = "player"
                    self.computer_ball.turn_complete = False
                    # 确保玩家球准备好下一回合
                    self.player_ball.is_moving = False
                    self.player_ball.turn_complete = False
                    print("回合切换到玩家")

        # 检查与障碍物和道具的碰撞
        for ball in [self.player_ball, self.computer_ball]:
            if ball.is_moving:
                self.check_obstacle_collisions(ball)
                self.check_power_up_collisions(ball)

        # 更新球的效果状态
        self.player_ball.update_effects()
        self.computer_ball.update_effects()

    def check_obstacle_collisions(self, ball):
        """检查球与障碍物的碰撞"""
        ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius,
                              ball.radius * 2, ball.radius * 2)
        for obstacle in self.obstacles:
            if ball_rect.colliderect(obstacle.rect):
                # 确定碰撞方向并反弹
                if ball.x < obstacle.rect.left or ball.x > obstacle.rect.right:
                    ball.dx *= -1
                if ball.y < obstacle.rect.top or ball.y > obstacle.rect.bottom:
                    ball.dy *= -1

    def draw(self, screen):
        # 绘制景
        self.background.draw(screen)
        
        # 绘制障碍物
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        
        # 绘制道具
        current_time = pygame.time.get_ticks()
        for power_up in self.power_ups:
            if not power_up.collected:
                power_up.draw(screen)
                
                # 计算并显示剩余时间
                remaining_time = (power_up.lifetime - 
                                (current_time - power_up.creation_time)) // 1000
                
                # 最后5秒显示计时
                if remaining_time <= 5:
                    time_text = self.font.render(str(remaining_time), True, power_up.color)
                    time_rect = time_text.get_rect(
                        center=(power_up.x, power_up.y - power_up.radius - 20)
                    )
                    screen.blit(time_text, time_rect)
        
        # 绘制信息面板
        panel_surface = pygame.Surface((300, 150), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, COLORS['panel'], panel_surface.get_rect())
        screen.blit(panel_surface, (20, 20))
        
        # 显示当前回合
        turn_text = f"当前回合: {'玩家' if self.current_turn == 'player' else '电脑'}"
        text_surface = self.font.render(turn_text, True, BLACK)
        screen.blit(text_surface, (20, 20))
        
        # 绘制力量条
        if self.current_turn == "player" and self.player_ball.is_power_adjusting:
            power_percentage = (self.player_ball.power - ARROW_LENGTH_MIN) / (ARROW_LENGTH_MAX - ARROW_LENGTH_MIN)
            power_width = 200 * power_percentage
            pygame.draw.rect(screen, COLORS['power_bar'], (40, 80, power_width, 20))
            pygame.draw.rect(screen, COLORS['title'], (40, 80, 200, 20), 2)
        
        # 绘制球
        self.player_ball.draw(screen)
        self.computer_ball.draw(screen)
        
        # 绘制退出按钮
        self.quit_button.draw(screen)
        
        # 游戏结束显示
        if self.game_over:
            # 创建半透明遮罩
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 128), overlay.get_rect())
            screen.blit(overlay, (0, 0))
            
            # 显示获胜信息
            win_text = f"{self.winner}获胜！按空格键重新开始"
            text_surface = self.font.render(win_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            screen.blit(text_surface, text_rect)

class Button:
    def __init__(self, x, y, width, height, text, color, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False
        self.font = font or get_chinese_font(28)  # 使用传入的字体或默认中文字体

    def draw(self, screen):
        # 绘制按钮背景
        color = (min(self.color[0] + 30, 255),
                min(self.color[1] + 30, 255),
                min(self.color[2] + 30, 255)) if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        
        # 绘制文字
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Ball:
    def __init__(self, x, y, color):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.color = color
        self.dx = 0
        self.dy = 0
        self.angle = 0
        self.power = ARROW_LENGTH_MIN
        self.base_power_max = ARROW_LENGTH_MAX
        self.max_power = self.base_power_max
        self.base_radius = BALL_RADIUS
        self.radius = self.base_radius
        self.is_aiming = False
        self.is_power_adjusting = False
        self.is_moving = False
        self.power_increasing = True
        self.turn_complete = False
        self.base_rotation_speed = ROTATION_SPEED
        self.rotation_speed = self.base_rotation_speed
        
        # 效果状态跟踪
        self.effects = {
            PowerUpType.SPEED_UP: {'active': False, 'end_time': 0},
            PowerUpType.SPEED_DOWN: {'active': False, 'end_time': 0},
            PowerUpType.POWER_UP: {'active': False, 'end_time': 0},
            PowerUpType.POWER_DOWN: {'active': False, 'end_time': 0},
            PowerUpType.SIZE_UP: {'active': False, 'end_time': 0},
            PowerUpType.SIZE_DOWN: {'active': False, 'end_time': 0},
            PowerUpType.RESET_POSITION: {'active': False, 'end_time': 0}
        }

    def shoot(self):
        """发射球"""
        # 根据角度和力量设置速度
        self.dx = math.cos(math.radians(self.angle)) * (self.power / 10)
        self.dy = math.sin(math.radians(self.angle)) * (self.power / 10)
        self.is_moving = True
        self.is_aiming = False
        self.is_power_adjusting = False
        self.power = ARROW_LENGTH_MIN  # 重置力量
        print(f"球被发射: 速度({self.dx}, {self.dy}), 角度{self.angle}, 力量{self.power}")

    def update(self):
        """更新球的状态"""
        # 更新效果状态
        current_time = pygame.time.get_ticks()
        for effect_type, effect_data in self.effects.items():
            if effect_data['active']:
                if current_time >= effect_data['end_time']:
                    # 效果结束，重置相关属性
                    effect_data['active'] = False
                    if effect_type in [PowerUpType.SPEED_UP, PowerUpType.SPEED_DOWN]:
                        self.rotation_speed = self.base_rotation_speed
                        print(f"旋转速度效果结束，恢复为: {self.rotation_speed}")
                    elif effect_type in [PowerUpType.POWER_UP, PowerUpType.POWER_DOWN]:
                        self.max_power = self.base_power_max
                        print(f"力量效果结束，恢复为: {self.max_power}")
                    elif effect_type in [PowerUpType.SIZE_UP, PowerUpType.SIZE_DOWN]:
                        self.radius = self.base_radius
                        print(f"大小效果结束，恢复为: {self.radius}")
        
        # 更新移动状态
        if self.is_moving:
            self.x += self.dx
            self.y += self.dy
            self.dx *= FRICTION
            self.dy *= FRICTION
            
            if abs(self.dx) < 0.1 and abs(self.dy) < 0.1:
                self.dx = 0
                self.dy = 0
                self.is_moving = False
                self.turn_complete = True
            
            # 边界碰撞检测
            if self.x - self.radius <= 0 or self.x + self.radius >= WINDOW_WIDTH:
                self.dx *= -1
            if self.y - self.radius <= 0 or self.y + self.radius >= WINDOW_HEIGHT:
                self.dy *= -1
            
            self.x = max(self.radius, min(self.x, WINDOW_WIDTH - self.radius))
            self.y = max(self.radius, min(self.y, WINDOW_HEIGHT - self.radius))

    def update_effects(self):
        """更新效果状态"""
        current_time = pygame.time.get_ticks()
        
        for effect_type, effect_data in self.effects.items():
            if effect_data['active'] and current_time >= effect_data['end_time']:
                # 效果结束，重置相关属性
                effect_data['active'] = False
                if effect_type in [PowerUpType.SPEED_UP, PowerUpType.SPEED_DOWN, PowerUpType.POWER_UP, PowerUpType.POWER_DOWN, PowerUpType.SIZE_UP, PowerUpType.SIZE_DOWN]:
                    self.radius = self.base_radius
                    print(f"球体半径恢复到 {self.radius}")

    def reset_position(self):
        """重置到初始位置"""
        self.x = self.original_x
        self.y = self.original_y
        self.dx = 0
        self.dy = 0
        self.is_moving = False
        self.is_aiming = False
        self.is_power_adjusting = False
        self.power = ARROW_LENGTH_MIN
        self.angle = 0
        print(f"球体重置到初始位置: ({self.x}, {self.y})")

    def apply_effect(self, effect_type):
        """应用道具效果"""
        current_time = pygame.time.get_ticks()
        duration = random.randint(30000, 60000)  # 30-60秒的效果持续时间
        
        # 处理随机效果
        if effect_type == PowerUpType.RANDOM:
            available_effects = [e for e in PowerUpType if e != PowerUpType.RANDOM]
            effect_type = random.choice(available_effects)
            print(f"随机效果转化为: {effect_type.value}")
        
        # 重置位置是即时效果
        if effect_type == PowerUpType.RESET_POSITION:
            self.reset_position()
            self.turn_complete = True  # 标记回合结束
            print("位置已重置，回合结束")
            return
        
        # 设置效果持续时间
        self.effects[effect_type]['active'] = True
        self.effects[effect_type]['end_time'] = current_time + duration
        
        # 应用效果
        if effect_type == PowerUpType.SPEED_UP:
            self.rotation_speed = self.base_rotation_speed * 2.0
        elif effect_type == PowerUpType.SPEED_DOWN:
            self.rotation_speed = self.base_rotation_speed * 0.5
        elif effect_type == PowerUpType.POWER_UP:
            self.max_power = self.base_power_max * 1.5
        elif effect_type == PowerUpType.POWER_DOWN:
            self.max_power = self.base_power_max * 0.7
        elif effect_type == PowerUpType.SIZE_UP:
            self.radius = self.base_radius * 2.0
        elif effect_type == PowerUpType.SIZE_DOWN:
            self.radius = self.base_radius * 0.5
        
        print(f"应用效果: {effect_type.value}")
        print(f"当前状态 - 旋转速度: {self.rotation_speed}, 最大力量: {self.max_power}, 半径: {self.radius}")
        print(f"效果持续时间: {duration/1000}秒")

    def draw(self, screen):
        # 绘制球体
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))
        
        # 如果在瞄准或调整力量，绘制方向箭头
        if self.is_aiming or self.is_power_adjusting:
            self.draw_direction_arrow(screen)
        
        # 绘制活跃效果
        self.draw_active_effects(screen)

    def draw_direction_arrow(self, screen):
        """绘制美化后的方向箭头"""
        # 计算箭头终点
        end_x = self.x + math.cos(math.radians(self.angle)) * self.power
        end_y = self.y + math.sin(math.radians(self.angle)) * self.power
        
        # 箭头参数
        arrow_width = 3
        head_length = 20
        head_width = 15
        
        # 确定箭头颜色
        if self.is_power_adjusting:
            # 根据力量大小渐变颜色
            power_ratio = (self.power - ARROW_LENGTH_MIN) / (ARROW_LENGTH_MAX - ARROW_LENGTH_MIN)
            arrow_color = (
                int(255 * power_ratio),  # R
                int(255 * (1 - power_ratio)),  # G
                0  # B
            )
        else:
            # 瞄准时使用固定颜色
            arrow_color = (100, 200, 255)
        
        # 计算箭头主体的方向向量
        dx = end_x - self.x
        dy = end_y - self.y
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return
        
        # 单位向量
        unit_x = dx / length
        unit_y = dy / length
        
        # 绘制箭头主体（渐变效果）
        segments = 10
        for i in range(segments):
            start_ratio = i / segments
            end_ratio = (i + 1) / segments
            start_x = self.x + dx * start_ratio
            start_y = self.y + dy * start_ratio
            segment_end_x = self.x + dx * end_ratio
            segment_end_y = self.y + dy * end_ratio
            
            # 渐变透明度
            alpha = 255 - int(200 * (i / segments))
            # 确保颜色值在有效范围内
            r = min(255, max(0, arrow_color[0]))
            g = min(255, max(0, arrow_color[1]))
            b = min(255, max(0, arrow_color[2]))
            segment_color = (r, g, b, alpha)
            
            # 创建surface来支持透明度
            line_surface = pygame.Surface((int(length), arrow_width * 2), pygame.SRCALPHA)
            pygame.draw.line(
                line_surface,
                segment_color,
                (int(length * start_ratio), arrow_width),
                (int(length * end_ratio), arrow_width),
                arrow_width
            )
            
            # 旋转surface
            angle = math.degrees(math.atan2(dy, dx))
            rotated_surface = pygame.transform.rotate(line_surface, -angle)
            
            # 计算绘制位置
            draw_pos = (
                int(start_x - rotated_surface.get_width()/2),
                int(start_y - rotated_surface.get_height()/2)
            )
            screen.blit(rotated_surface, draw_pos)
        
        # 绘制箭头头部
        head_surface = pygame.Surface((head_length * 2, head_width * 2), pygame.SRCALPHA)
        # 确保箭头头部颜色有效
        head_color = (
            min(255, max(0, arrow_color[0])),
            min(255, max(0, arrow_color[1])),
            min(255, max(0, arrow_color[2])),
            200
        )
        pygame.draw.polygon(
            head_surface,
            head_color,
            [
                (head_length * 2, head_width),
                (head_length, head_width - head_width/2),
                (head_length, head_width + head_width/2)
            ]
        )
        
        # 旋转箭头头部
        rotated_head = pygame.transform.rotate(head_surface, -angle)
        head_pos = (
            int(end_x - rotated_head.get_width()/2),
            int(end_y - rotated_head.get_height()/2)
        )
        screen.blit(rotated_head, head_pos)
        
        # 如果在调整力量，添加力量指示器
        if self.is_power_adjusting:
            power_ratio = (self.power - ARROW_LENGTH_MIN) / (ARROW_LENGTH_MAX - ARROW_LENGTH_MIN)
            bar_width = 50
            bar_height = 6
            bar_x = self.x - bar_width/2
            bar_y = self.y - self.radius - 20
            
            # 确保使用RGB颜色值（不包含alpha通道）
            bar_color = (
                min(255, max(0, arrow_color[0])),
                min(255, max(0, arrow_color[1])),
                min(255, max(0, arrow_color[2]))
            )
            
            # 绘制背景条
            pygame.draw.rect(screen, (50, 50, 50),
                            (int(bar_x), int(bar_y), int(bar_width), int(bar_height)))
            # 绘制力量条
            pygame.draw.rect(screen, bar_color,
                            (int(bar_x), int(bar_y), 
                             int(bar_width * power_ratio), int(bar_height)))
            # 绘制边框
            pygame.draw.rect(screen, (200, 200, 200),
                            (int(bar_x), int(bar_y), int(bar_width), int(bar_height)), 1)

    def draw_active_effects(self, screen):
        """绘制当前活跃的效果图标"""
        current_time = pygame.time.get_ticks()
        active_effects = [(effect, data) for effect, data in self.effects.items() 
                         if data['active']]
        
        if not active_effects:
            return
            
        icon_size = 20
        spacing = 25
        start_x = self.x - (len(active_effects) * spacing) / 2
        
        for i, (effect_type, effect_data) in enumerate(active_effects):
            remaining_time = (effect_data['end_time'] - current_time) / 1000
            
            # 绘制效果图标
            icon_x = start_x + i * spacing
            icon_y = self.y - self.radius - 25
            
            # 绘制图标背景
            bg_color = (255, 100, 100) if effect_type in [PowerUpType.SPEED_UP, 
                                                        PowerUpType.POWER_DOWN, 
                                                        PowerUpType.SIZE_UP] else (100, 255, 100)
            pygame.draw.circle(screen, bg_color, (int(icon_x), int(icon_y)), icon_size//2)
            
            # 绘制效果文字
            font = pygame.font.Font(None, 20)
            text = self.get_effect_symbol(effect_type)
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(icon_x, icon_y))
            screen.blit(text_surface, text_rect)
            
            # 显示剩余时间
            if remaining_time <= 5:
                time_text = font.render(f"{int(remaining_time)}", True, (255, 255, 255))
                time_rect = time_text.get_rect(center=(icon_x, icon_y - 20))
                screen.blit(time_text, time_rect)

    def get_effect_symbol(self, effect_type):
        """获取效果的符号表示"""
        symbols = {
            PowerUpType.SPEED_UP: "快",
            PowerUpType.SPEED_DOWN: "慢",
            PowerUpType.POWER_UP: "强",
            PowerUpType.POWER_DOWN: "弱",
            PowerUpType.SIZE_UP: "大",
            PowerUpType.SIZE_DOWN: "小",
            PowerUpType.RESET_POSITION: "回"
        }
        return symbols.get(effect_type, "?")

def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.quit_button.handle_event(event):
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                game.quit_button.handle_event(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.game_over:
                        game.reset_game()
                    elif game.current_turn == "player" and not game.player_ball.is_moving:
                        if not game.player_ball.is_aiming and not game.player_ball.is_power_adjusting:
                            game.player_ball.is_aiming = True
                        elif game.player_ball.is_aiming:
                            game.player_ball.is_aiming = False
                            game.player_ball.is_power_adjusting = True
                        elif game.player_ball.is_power_adjusting:
                            game.player_ball.shoot()

        # 更新玩家的箭头旋转和力量
        if game.player_ball.is_aiming:
            game.player_ball.angle = (game.player_ball.angle + ROTATION_SPEED) % 360
        
        if game.player_ball.is_power_adjusting:
            if game.player_ball.power_increasing:
                game.player_ball.power += POWER_CHANGE_SPEED
                if game.player_ball.power >= ARROW_LENGTH_MAX:
                    game.player_ball.power_increasing = False
            else:
                game.player_ball.power -= POWER_CHANGE_SPEED
                if game.player_ball.power <= ARROW_LENGTH_MIN:
                    game.player_ball.power_increasing = True

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()