'''
Python script to generate STL files for 3D printing QR codes.

We will create a QR code using the qrcode library, then convert it to a numpy array.
'''

import qrcode
import sys
import numpy as np
import math

def make_qr_code(qr_data, stl_file="qrcode.stl", include_bottom=True, cirlce=True):


    # instantiate QRCode object
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    # add data to the QR code
    qr.add_data(qr_data)
    # compile the data into a QR code array
    qr.make()

    # get the matrix from the qr code
    qr.border = 0
    qr_matrix = qr.get_matrix()
    qr_shape = np.array(qr_matrix).shape
    print("The shape of the QR image:", qr_shape)


    # qr width
    qr_width = qr_shape[0]
    # qr radius
    qr_R = (qr_width-1)/2
    # circle radius
    circle_R = math.sqrt(2*(qr_R**2 ))+1
    # square centre
    grid_centre = math.ceil(circle_R)
    # grid width
    grid_width = int(grid_centre*2)

    # create a square array of zeros that has size 2*radius
    circle_matrix = np.zeros((grid_width+1, grid_width+1))

    # loop over the circle_matrix and add 1 for each position inside the circle
    for y in range(np.array(circle_matrix).shape[0]):
        for x in range(np.array(circle_matrix).shape[1]):
            if (x-grid_centre)**2 + (y-grid_centre)**2 < circle_R**2:
                # # determine if the position is outside the qr code
                # if x < qr_top_x+1 or x >= qr_bot_x-1 or y < qr_top_y+1 or y >= qr_bot_y-1:
                    
                    # 50% change of adding a block
                    if np.random.randint(0,2) == 1:
                        circle_matrix[x][y] = 1

    # determine the top left corner of the qr code
    qr_top_x = int(grid_centre - qr_R)

    # clear the top left square of the qr code, box size 9*9, offset by -1
    circle_matrix[qr_top_x-1:qr_top_x+9, qr_top_x-1:qr_top_x+9] = 0
    # same for top right    
    circle_matrix[qr_top_x-1:qr_top_x+9, qr_top_x+qr_width-9:qr_top_x+qr_width+1] = 0
    # same for bottom left
    circle_matrix[qr_top_x+qr_width-9:qr_top_x+qr_width+1, qr_top_x-1:qr_top_x+9] = 0


    # clear the qr code from the circle matrix
    circle_matrix[qr_top_x:qr_top_x+qr_width, qr_top_x:qr_top_x+qr_width] = 0

    # add the qr code to the circle matrix
    circle_matrix[qr_top_x:qr_top_x+qr_width, qr_top_x:qr_top_x+qr_width] = qr_matrix



    # print the qr code
    # loop over the 2d array
    with open(stl_file, "w") as stl_file:
        stl_file.write(stl_header())
        if cirlce:
            # add the circle blocks
            # itterate over the circle_matrix
            for y in range(np.array(circle_matrix).shape[0]):
                for x in range(np.array(circle_matrix).shape[1]):
                    if circle_matrix[x][y] == 1:
                        stl_file.write(stl_box([x, y, 0], 1, 1, 1))
                        # print 'x' without new line
                        print('x', end='')
                    else:
                        # print ' ' without new line
                        print('.', end='')
                # print new line
                print()
            if include_bottom:  
                L = np.array(circle_matrix).shape[0]+1
                W = np.array(circle_matrix).shape[1]+1
                H = 1
                P = [L/2-1, W/2-1, -1]
                # stl_box(P, L, W, H)

                cylinder = stl_cylinder([L/2-1, W/2-1, -1.5], L/2, 1)

                stl_file.write(cylinder)
        else:
            for y in range(np.array(qr_matrix).shape[0]):
                for x in range(np.array(qr_matrix).shape[1]):
                    if qr_matrix[x][y] == 1:
                        stl_file.write(stl_box([x, y, 0], 1, 1, 1))
                        # print 'x' without new line
                        print('x', end='')
                    else:
                        # print ' ' without new line
                        print('.', end='')
                # print new line
                print()
            if include_bottom:
                stl_file.write(stl_box([np.array(qr_matrix).shape[0]/2, np.array(qr_matrix).shape[1]/2, -1], np.array(qr_matrix).shape[0], np.array(qr_matrix).shape[1], 1))

        stl_file.write(stl_footer())









def stl_header():
    '''
    Create the header for the STL file.
    '''
    str = "solid ASCII\n"
    return str

def stl_footer():
    '''
    Create the footer for the STL file.
    '''
    str = "endsolid\n"
    return str


def stl_triangle(v1, v2, v3):
    '''
    Create a triangle for the STL file.
    input are vectors for the x, y, z coordinates and the normal vector.
    '''
    # calculate the normal vector
    v1 = np.array(v1)
    v2 = np.array(v2)
    v3 = np.array(v3)
    v21 = v2 - v1
    v31 = v3 - v1
    vn = np.cross(v21, v31)
    vn = vn / np.linalg.norm(vn)

    str = f"facet normal {vn[0]} {vn[1]} {vn[2]}\n"
    str += "  outer loop\n"
    str += f"    vertex {v1[0]} {v1[1]} {v1[2]}\n"
    str += f"    vertex {v2[0]} {v2[1]} {v2[2]}\n"
    str += f"    vertex {v3[0]} {v3[1]} {v3[2]}\n"
    str += "  endloop\n"
    str += "endfacet\n"

    return str

def stl_box(P, L, W, H):
    ''' 
    Create a box for the STL file.
    input p is a point at which the box is centered.
    input L is the length of the box.
    input W is the width of the box.
    input H is the height of the box.
    '''
    # calculate the bottom 4 corners
    A = [P[0]-L/2, P[1]-W/2, P[2]-H/2]
    B = [P[0]-L/2, P[1]+W/2, P[2]-H/2]
    C = [P[0]+L/2, P[1]+W/2, P[2]-H/2]  
    D = [P[0]+L/2, P[1]-W/2, P[2]-H/2]
    # calculate the top 4 corners
    E = [P[0]-L/2, P[1]-W/2, P[2]+H/2]
    F = [P[0]-L/2, P[1]+W/2, P[2]+H/2]
    G = [P[0]+L/2, P[1]+W/2, P[2]+H/2]
    H = [P[0]+L/2, P[1]-W/2, P[2]+H/2]

    # create the triangles
    str  = stl_triangle(A, B, C)
    str += stl_triangle(A, C, D)
    str += stl_triangle(E, F, G)
    str += stl_triangle(E, G, H)
    str += stl_triangle(A, B, F)
    str += stl_triangle(A, F, E)
    str += stl_triangle(D, C, G)

    str += stl_triangle(D, G, H)
    str += stl_triangle(A, D, H)
    str += stl_triangle(A, H, E)
    str += stl_triangle(B, C, G)
    str += stl_triangle(B, G, F)

    return str


def stl_cylinder(center, radius, height, resolution=100):
    '''
    Create a cylinder for the STL file.
    '''
    str = ""
    # loop over the resolution and make pie-slices and edges
    for i in range(resolution):
        # calculate the angle
        angle = i/resolution*2*math.pi
        # calculate the x and y coordinates
        x = center[0] + radius*math.cos(angle)
        y = center[1] + radius*math.sin(angle)
        # calculate the x and y coordinates of the next point
        x_next = center[0] + radius*math.cos((i+1)/resolution*2*math.pi)
        y_next = center[1] + radius*math.sin((i+1)/resolution*2*math.pi)
        # create the bottom pie-slice
        str += stl_triangle([center[0], center[1], center[2]], [x, y, center[2]], [x_next, y_next, center[2]])
        # create the top pie-slice
        str += stl_triangle([center[0], center[1], center[2]+height], [x_next, y_next, center[2]+height], [x, y, center[2]+height])

        # create the edges
        str += stl_triangle([x, y, center[2]], [x_next, y_next, center[2]], [x, y, center[2]+height])
        str += stl_triangle([x_next, y_next, center[2]], [x_next, y_next, center[2]+height], [x, y, center[2]+height])

    return str
    

# run this script if called from command
if __name__ == '__main__':

    # if no arguments are passed, print help text and exit
    if len(sys.argv) == 1:
        print("Usage: python qr_code.py <url>")
        qr_data = "https://rolandblok.net/ddddddddddddddddsdfgsdfgddddggggddhhdddggdddd"
        qr_data = "123"
        qr_data = "https://rolandblok.net"
    else:   
        # read the url from command line
        qr_data = sys.argv[1]    

    print("Creating QR code for:", qr_data)
    make_qr_code(qr_data, "qrcode.stl")

    pass