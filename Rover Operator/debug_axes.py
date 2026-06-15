import pygame, time
pygame.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()
print(f"Controller: {js.get_name()}, {js.get_numaxes()} axes\n")
while True:
    pygame.event.pump()
    axes = [round(js.get_axis(i), 2) for i in range(js.get_numaxes())]
    for i, v in enumerate(axes):
        if abs(v) > 0.1:
            print(f"axis {i} = {v}")
    print("---")
    time.sleep(0.3)