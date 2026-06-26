import pygame, json, sys

# constants
WIDTH = 512
HEIGHT = 400
SCALE_X = WIDTH / 256
SCALE_Y = HEIGHT / 200


# initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# region read and writes
class js:
    data = {}
    verts = []
    polys = []
    colors = []

    # opens and populates the json data thingy
    def open_data(filename):
        with open(filename, 'r') as f:
            js.data = json.loads(f.read())
            f.close()
        
    # reads a 
    def read_frame(frame):
        # self explanatory
        js.polys = js.data['frames'][frame]['p']
        js.colors = js.data['frames'][frame]['c']

        # for some reason theres some absolute vertex frames so this is optional
        if ('v' in js.data['frames'][frame]):
            js.verts = js.data['frames'][frame]['v']
        else:
            js.verts = []
            
# endregion

# region draws
class rendering:
    def draw_poly(tri):
        indexDat = []
        triDat = []

        if ('vi' in tri):
            indexDat = tri['vi']
        
        if ('v' in tri):
            triDat = tri['v']

        # index portion
        for index in range(len(indexDat)-2):
            # verts
            v1 = js.verts[indexDat[0]['i']]
            v2 = js.verts[indexDat[index+1]['i']]
            v3 = js.verts[indexDat[index+2]['i']]

            # color
            clrStr = js.colors[tri['ci']]
            clr = pygame.Color(clrStr)
            
            pygame.draw.polygon(screen, clr,  [[v1['x'] * SCALE_X, v1['y'] * SCALE_Y],
                                                [v2['x'] * SCALE_X, v2['y'] * SCALE_Y],
                                                [v3['x'] * SCALE_X, v3['y'] * SCALE_Y]])


        # vertex portion
        for index in range(len(triDat)-2):
            # verts
            v1 = triDat[0]
            v2 = triDat[index+1]
            v3 = triDat[index+2]

            # color
            clrStr = js.colors[tri['ci']]
            clr = pygame.Color(clrStr)
            
            pygame.draw.polygon(screen, clr,  [[v1['x'] * SCALE_X, v1['y'] * SCALE_Y],
                                                [v2['x'] * SCALE_X, v2['y'] * SCALE_Y],
                                                [v3['x'] * SCALE_X, v3['y'] * SCALE_Y]])

# endregion

    # renders frame from tris
    def render_frame(frame):
        # read frame and clean screen
        js.read_frame(frame)
        screen.fill((0,0,0))

        
        # loop through polygons and draw accordingly
        for poly in js.polys:
            rendering.draw_poly(poly)


# niccc init
frame = 0
js.open_data('niccc.json')



# persistence
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # loop through scene
    frame %= 1799
    frame += 1

    rendering.render_frame(frame)
    pygame.display.flip()
    