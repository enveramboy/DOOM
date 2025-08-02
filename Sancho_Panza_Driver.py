import pigpio
from numpy import interp
import time
from picamera2 import Picamera2, Preview
from libcamera import Transform
import pygame

AI1 = 17
AI2 = 27
PWMA = 22
STBY = 5
BI1 = 6
BI2 = 13
PWMB = 19
SERVO = 26
	
class Controls:
	def __init__(self):
		self.pi = pigpio.pi()
		if not self.pi.connected: exit()
		for pin in [AI1, AI2, PWMA, STBY, BI1, BI2, PWMB, SERVO]: self.pi.set_mode(pin, pigpio.OUTPUT)
		
	def Rotate_Servo(self, angle):
		self.pi.set_servo_pulsewidth(SERVO, interp(angle, [0, 180], [500, 2500]))
		
	def __Drive(self, spd, ai1, ai2, bi1, bi2):
		self.pi.write(AI1, ai1)
		self.pi.write(AI2, ai2)
		self.pi.set_PWM_frequency(PWMA, 50)
		self.pi.set_PWM_dutycycle(PWMA, spd)
		self.pi.write(STBY, 1)
		self.pi.write(BI1, bi1)
		self.pi.write(BI2, bi2)
		self.pi.set_PWM_frequency(PWMB, 50)
		self.pi.set_PWM_dutycycle(PWMB, spd)
		
	def Forward(self, spd): self.__Drive(spd, 0, 1, 1, 0) 
		
	def Reverse(self, spd): self.__Drive(spd, 1, 0, 0, 1)
	
	def Turn_Right(self, spd): self.__Drive(spd, 1, 0, 1, 0)
	
	def Turn_Left(self, spd): self.__Drive(spd, 0, 1, 0, 1)
	
	def Brake(self): self.pi.write(STBY, 0)
	
		
controls = Controls()
camera = Picamera2()
camera_config = camera.create_preview_configuration(transform=Transform(hflip=True, vflip=True))
camera.configure(camera_config)
camera.start_preview(Preview.QTGL)
camera.start()

# Keyboard Input Initialization
WIDTH, HEIGHT = 210, 160
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
running = True
servo_angle = 90
pan_up = False
pan_down = False

while running:
	if pan_up: servo_angle += 0.1
	if pan_down: servo_angle -= 0.1
	controls.Rotate_Servo(servo_angle)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			controls.Brake()
			exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				controls.Brake()
				exit()
			if event.key == pygame.K_d:
				controls.Turn_Right(168)
			if event.key == pygame.K_a:
				controls.Turn_Left(168)
			if event.key == pygame.K_w:
				controls.Forward(168)
			if event.key == pygame.K_s:
				controls.Reverse(168)
			if event.key == pygame.K_UP:
				pan_up = True
			if event.key == pygame.K_DOWN:
				pan_down = True
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_d or event.key == pygame.K_a or event.key == pygame.K_w or event.key == pygame.K_s:
				controls.Brake()
			if event.key == pygame.K_UP:
				pan_up = False
			if event.key == pygame.K_DOWN:
				pan_down = False
					
	pygame.display.flip()

pygame.quit()
