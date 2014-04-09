import math
import operator
import sys
import cairo as C
from math import pi
from parameters import *

# Available color codes
colors = [  [255, 12, 12], [12, 255, 12], [12, 12, 255], 
            [255, 255, 12], [12, 255, 255], [255, 12, 255],  
#            [102, 0, 0], [0, 102, 0], [0, 0, 102],
            [255, 128, 12], [12, 255, 128], [128, 12, 255], 
#            [102, 102, 0], [0, 102, 102], [102, 0, 102],
            [153, 76, 0], [153, 0, 76], [51, 102, 0],
            [178, 102, 255], [192, 192, 192], [255, 178, 102]]

# get color along with it's symbolic attribute
def get_color(idx):
    return [colors[idx % len(colors)], idx / len(colors)] 

# get dictionary of mapping between colors and motifs
def get_mapping(tr_list):
    res = {}
    idx = 0
    for tr in sorted(set(tr_list)):
        res[tr] = get_color(idx)
        idx += 1
    return res

# read the list of motifs composing the minisatelite
def get_TR_list(filename):
    res = []

    with open(filename) as f:
        for line in f:
            res.append(line[:-1])

    return res

# create dictionary containing list of all motifs and mapping motif to color
def get_TR_encoding(filename):

    tr_list = get_TR_list(filename)
    mapping = get_mapping(tr_list)
    
    return {'tr_list':tr_list, 'mapping':mapping}

# draw an attribute on one coding strip
def add_attr(ctx, attr_type,x1, y1):

    # diagonal line
    if attr_type == 1 :
        ctx.set_source_rgb(0,0,0)
        ctx.move_to(x1, y1)
        ctx.line_to(x1 + STRIPE_WIDTH, y1 + STRIPE_HEIGHT)
        ctx.set_line_width(3)
        ctx.stroke()
    # vertical line
    if attr_type == 2 :
        ctx.set_source_rgb(0,0,0)
        ctx.move_to(x1 + (STRIPE_WIDTH / 2), y1)
        ctx.line_to(x1 + (STRIPE_WIDTH / 2), y1 + STRIPE_HEIGHT)
        ctx.set_line_width(3)
        ctx.stroke()
    # horizontal line
    if attr_type == 3 :
        ctx.set_source_rgb(0,0,0)
        ctx.move_to(x1, y1 + (STRIPE_HEIGHT / 2))
        ctx.line_to(x1 + STRIPE_WIDTH, y1 + (STRIPE_HEIGHT / 2))
        ctx.set_line_width(3)
        ctx.stroke()
    # chessboard
    if attr_type == 4 :
        ctx.set_source_rgb(0,0,0)
        ctx.rectangle(x1,y1, STRIPE_WIDTH / 2, STRIPE_HEIGHT / 2)
        ctx.fill()
        ctx.rectangle(x1 + (STRIPE_WIDTH / 2), y1 + (STRIPE_HEIGHT / 2), STRIPE_WIDTH / 2, STRIPE_HEIGHT / 2)
        ctx.fill()
    # middle dot
    if attr_type == 5 :
        ctx.set_source_rgb(0,0,0)
        ctx.arc(x1 + (STRIPE_WIDTH / 2), y1 + (STRIPE_HEIGHT / 2), (STRIPE_WIDTH / 2) - 1, 0, 2 * math.pi);
        ctx.fill();

# paint one stripe box
def fill_rec(ctx, col, tr, x1,y1):
    bg = col[0]
    attr_type = col[1]
    ctx.set_source_rgb(bg[0]/255.0, bg[1]/255.0, bg[2]/255.0)
    ctx.rectangle(x1,y1, STRIPE_WIDTH, STRIPE_HEIGHT)
    ctx.fill()

    add_attr(ctx, attr_type,x1, y1)

def draw_border(ctx, x1, y1):
    ctx.rectangle(x1, y1, STRIPE_WIDTH, STRIPE_HEIGHT)
    ctx.set_line_width(1)
    ctx.set_source_rgb(0,0,0)
    ctx.stroke()

   


def main(argv):

    # filename 
    filename = argv[1]
    
    # get encodings for each motif
    encoding = get_TR_encoding(filename)
   
    # number of motifs in minisatelite
    no_repeats = len(encoding['tr_list']) 

#    STRIPE_WIDTH, STRIPE_HEIGHT = 10, 12
#    gap_size = 4
#    big_gap = 4 * gap_size
#    font_width = 7

    # calculate width
    width = no_repeats * STRIPE_WIDTH + 2 * MARGIN
    
    # calculate height
    # plan the legend size
    no_legend_entries = len(encoding['mapping'])
    longest_motif_size = max(map(len, encoding['mapping'].keys())) 
    entry_width = longest_motif_size * FONT_WIDTH + STRIPE_WIDTH + 3 * GAP
    entry_height = STRIPE_HEIGHT + GAP
    entries_in_row = ( width - 2 * MARGIN ) / entry_width
    columns_in_legend = no_legend_entries / entries_in_row + 1
    height =  columns_in_legend * entry_height + 2 * MARGIN + STRIPE_HEIGHT + BIG_GAP
    x1, y1 = MARGIN, MARGIN

    # create new sheet
    surf = C.ImageSurface(C.FORMAT_RGB24,width,height)
    ctx = C.Context(surf)

    # fill everyting with white
    ctx.new_path()
    ctx.set_source_rgb(0.99,0.99,0.99)
    ctx.rectangle(0, 0, width, height)
    ctx.fill()

    # draw stripes for each motif
    for tr in encoding['tr_list']:

        col = encoding['mapping'][tr]
        fill_rec(ctx, col, tr, x1,y1)
        draw_border(ctx, x1, y1)
        x1 = x1 + STRIPE_WIDTH 
 
    # create_legend 
    x1 = MARGIN
    y1 = height - columns_in_legend * entry_height

    sorted_by_color = sorted(encoding['mapping'].iteritems(), key=operator.itemgetter(1))

    for (key, val)  in sorted_by_color:
        
        fill_rec(ctx, val, key, x1, y1)
        
        ctx.set_source_rgb(0,0,0)  # black
        txt = " : " + key
        ctx.select_font_face("Ubuntu", C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(FONT_SIZE)
        ctx.move_to(x1 + STRIPE_WIDTH, y1 + STRIPE_HEIGHT)
        ctx.show_text(txt)
        
        if x1 + entry_width < width :
            x1 += entry_width
        else :
            x1 = MARGIN
            y1 += entry_height
    
    # save to PNG
    output = "human-encoding.png"
    surf.write_to_png(output)
    
    
if __name__ == "__main__":
    main(sys.argv)
