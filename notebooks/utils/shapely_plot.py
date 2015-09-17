import matplotlib.pyplot as plt

# from numba import jit

# @jit
def draw_(g, fill, outline, lw, alpha):
    gType = g.geom_type
    if gType == 'Point':
        plt.plot(g.x, g.y, 'k,')
    elif gType == 'LineString':
        x, y = g.xy
        plt.plot(x, y, 'b-', color=outline, lw=lw)
    elif gType == 'Polygon':
        x, y = g.exterior.xy
        plt.fill(x, y, color=fill, aa=True, alpha=alpha) 
        plt.plot(x, y, color=outline, aa=True, lw=lw, alpha=alpha)
        for hole in g.interiors:
            x, y = hole.xy
            plt.fill(x, y, color='#ffffff', aa=True, alpha=alpha) 
            plt.plot(x, y, color='#999999', aa=True, lw=lw, alpha=alpha)

def draw(gs, fill='#cccccc', outline='#666666', lw=1.0, alpha=1.0):
    # Handle single and multiple geometries
    try:
        gs = iter(gs)
    except TypeError:
        gs = [gs]
    # For each shapelyGeometry,
    for g in gs:
        gType = g.geom_type
        if gType.startswith('Multi') or gType == 'GeometryCollection':
            draw(g.geoms)
        else:
            draw_(g, fill, outline, lw, alpha)

def plot(geoms):
    figure = plt.figure(num=None, figsize=(4, 4), dpi=180)
    axes = plt.axes()
    axes.set_aspect('equal', 'datalim')
    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)
    draw(geoms)
            
            
            
