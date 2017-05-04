GlowScript 2.4 VPython

# initialize instructions
scene.range = 4
scene.caption = """INSTRUCTIONS:
    1) Choose type of shot (Curve shots have less accuracy)
    2) Left-click where you want to shoot
    3) Each level the goalie gets faster and smarter!
    4) Clear all 5 levels to win! GOOD LUCK!"""
scene.append_to_caption('\n\n')

# display information
retry = label(pos=vec(0,0,0))
msg = label(pos=vec(0,1,0))
levelDisplay = label(pos=vec(0,2,0))

level = 1
levelDisplay.text = "LEVEL " + str(level)
madeGoal = False

# goal size
thk = 0.3
bH = 2.0
bW = bH*2
bZ = bH

# center of goal (right in the middle) / how far from origin
goalX = 0
goalY = 0
goalZ = -10

# create goal
wallR = box(pos=vector( goalX + bW, goalY, goalZ), size=vector( thk*2, bH*2, bZ*2), color=color.white)
wallL = box(pos=vector( goalX - bW, goalY, goalZ) , size=vector( thk*2, bH*2, bZ*2), color=color.white)
wallT = box(pos=vector( goalX, goalY + bH + thk, goalZ), size=vector( bW*2, thk*2, bZ*2), color=color.white)
wallBK = box(pos=vector( goalX, goalY, goalZ - bZ + thk), size=vector(bW*2, bH*2, thk*2), color=color.white)

# field dimensions
flrW = 20
flrH = thk*2
flrZ = 20 - bZ*2
flr = box(pos=vector(0, -bH - thk, 0), size=vector(flrW, flrH, flrZ), color=color.green)

# goal floor (diff color)
goalFlr = box(pos=vector(goalX, goalY - bH - thk, goalZ), size=vector( flrW, thk*2, bZ*2), color=color.blue)

# create soccer ball
ballRad = thk
ballStartPos = pos=vector(0, goalY - bH + ballRad, 0)
ball = sphere (pos=ballStartPos, color = color.red, radius = ballRad, retain=100)
ball.v = vector(0, 0, 0)

# goalie dimensions
goalieThk = .5
goalieW = goalieThk
goalieH = bH

# make goalie(s)
goalie = box(pos=vector(goalX, goalY -bH + goalieH, goalZ + bZ + goalieThk),
             size=vector(goalieW*2, goalieH*2, goalieThk*2), color = color.cyan)
goalie.v = vector(10, 0, 0)
goalieReactionTime = 50 # in frames

typeOfShot = 'LinearShot' # default shot
# determines type of shot user wants to shoot
def chooseShot(c):
    global typeOfShot
    typeOfShot = c.text
    for r in radButtons:
        r.checked = False
    c.checked = True

# option to shoots
linearShotButton = radio(bind=chooseShot, checked=True, text='LinearShot')
bananaShotButtonLeft = radio(bind=chooseShot, checked=False, text='BananaShotLeft')
bananaShotButtonRight = radio(bind=chooseShot, checked=False, text='BananaShotRight')
radButtons = []
radButtons.append(linearShotButton)
radButtons.append(bananaShotButtonLeft)
radButtons.append(bananaShotButtonRight)

deltaT = 0.01
# moves ball 1 frame
def moveBall():
    global deltaT
    ball.pos = ball.pos + ball.v*deltaT

# simulates a linear shot towards destination
def calculateLinearShot(dest):
    deltaX = dest.x - ballStartPos.x
    deltaY = (dest.y - ballStartPos.y) / 9
    hyp = sqrt(deltaX**2 + goalZ**2)
    magn = 10
    ball.v = vector(deltaX/hyp, deltaY, goalZ/hyp) * magn

# simulates a curve shot towards destination
# calculate parabola given start point and destination
# Arguments:
#   dest = where the ball should end up
#   dir = if the ball should curve right or left
def calculateBananaShot(dest, dir):
    ballCurrentPos = ball.pos
    deltaX = dest.x - ballStartPos.x
    turnPoint = vector(0,0,0)
    if dir == "left":
        turnPoint = vector(bW*3/4 + deltaX*3/8, ballStartPos.y, -flrZ/4 - deltaX * 3/8)
    elif dir == "right":
        turnPoint = vector(-bW*3/4 + deltaX*3/8, ballStartPos.y, -flrZ/4 + deltaX * 3/8)
    a = (ballStartPos.x - turnPoint.x) / (ballStartPos.z - turnPoint.z)**2
    inputZ = ball.pos.z - flrZ / 20 # reach goal in 20 steps
    outputX = a  * (inputZ - turnPoint.z)**2 + turnPoint.x
    outputY = ball.pos.y + (dest.y - ballStartPos.y) / 10
    ballEndingPos = vector(outputX, outputY, inputZ)
    magn = 15
    ball.v = (ballEndingPos - ballCurrentPos) * magn

ballShot = False
dest = vector(0, 0, 0)
# take a shot at the goal
def shoot():
    if ball.v.x == 0 and ball.v.y == 0 and ball.v.z == 0:
        global dest, ballShot
        dest = scene.mouse.pos
        # project click position to goal destination
        if dest.x > 0:
            dest.x = min(dest.x, 3) / 1.72 * bW
        else :
            dest.x = max(dest.x, -3) / 1.72 * bW
        dest.y = max(dest.y, -0.85) * (wallT.pos.y - thk)
        ballShot = True

# left-click = shoot ball
scene.bind('click', shoot)

# after a delay, goalie attempts to catch ball
def goalieFollowsBall():
    if not abs(goalie.pos.x - ball.pos.x) < 1:
        if goalie.pos.x > ball.pos.x:
            goalie.v.x = -abs(goalie.v.x)
        else:
            goalie.v.x = abs(goalie.v.x)

# restart game
def reset():
    global ballShot, frameAfterBallShot, goalieReactionTime
    ballShot = False
    ball.pos = ballStartPos
    ball.v = vector(0, 0, 0)
    frameAfterBallShot = 0
    msg.text = ""
    retry.text = ""
    # speed up goalie after every point
    if madeGoal:
        dir = goalie.v.x / abs(goalie.v.x)
        goalie.v.x = dir * (abs(goalie.v.x) + 2)
        goalieReactionTime -= 3

frameAfterBallShot = 0

# start game
while True:
    # start round
    while True:
        rate(100) # 0.01 second between each frame
        global deltaT, ballRad, thk
        
        # goalie movements
        if not (wallL.pos.x < goalie.pos.x < wallR.pos.x):
            dirBackToGoal = -(goalie.pos.x / abs(goalie.pos.x))
            goalie.v.x = dirBackToGoal * abs(goalie.v.x)
        goalie.pos = goalie.pos + goalie.v*deltaT
        
        # handle ball movements
        if ballShot:
            global dest, frameAfterBallShot
            if typeOfShot == "LinearShot":
                calculateLinearShot(dest)
            elif typeOfShot == "BananaShotLeft":
                calculateBananaShot(dest, "left")
            elif typeOfShot == "BananaShotRight":
                calculateBananaShot(dest, "right")
            moveBall()
            if frameAfterBallShot > goalieReactionTime:
                goalieFollowsBall()
            frameAfterBallShot += 1
    
        # goalie caught ball
        if abs(ball.pos.x - goalie.pos.x) < thk + ballRad and abs(ball.pos.z - goalie.pos.z) < thk + ballRad \
            and ball.pos.y < wallT.pos.y:
            msg.text = "THE GOALIE CAUGHT IT"
            madeGoal = False
            break
        
        # check if ball went inside goal
        if ball.pos.z < goalZ + bZ:
            if not (wallL.pos.x + thk < ball.pos.x < wallR.pos.x - thk) or (ball.pos.y > wallT.pos.y - thk):
                msg.text = "YOU MISSED"
                madeGoal = False
            else:
                msg.text = "GOALLLLLL"
                level += 1
                levelDisplay.text = "LEVEL " + str(level)
                madeGoal = True
            break

# gg
if level > 5:
    levelDisplay.text = "ALL LEVEL COMPLETED!"
        msg.text = "YOU WIN!"
        break
    
    # Ask if user wants to retry
    retry.text = "Want to try again? (y)es or (n)o?"
    ev = scene.waitfor('keydown')
    while ev.key != 'y' and ev.key != 'n':
        msg.text = "Invalid key. Try again. (y)es or (n)o?"
        ev = scene.waitfor("keydown")
if ev.key == 'y':
    reset()
    elif ev.key == 'n':
        msg.text = "BETTER LUCK NEXT TIME!"
        retry.text = ""
        break
