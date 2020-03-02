#!/usr/bin/python3

import sys, getopt

def cropRaster(raster, cropval=205):
    right = bottom = 0
    top = left = sys.maxsize
    row = col = 0
    frow = fcol = 0
    for line in raster: #top-down, left-right scan
        col = 0
        frow_last = frow
        frow = 0 #flagged row (with data in it, for detecting tail end)
        for value in line:
            fcol_last = fcol
            fcol = 0
            if value != cropval: # real data
                frow = fcol = 1
                if top > row: #if top thresh is lower than current line
                    top = max(0, row)
                if left > col:
                    left = max(0, col)
            if (fcol_last) and not fcol and (right < col):
                right = col
            col = col+1
        if (frow_last) and not frow and (bottom < row):
            bottom = row
        row = row+1
    print("\nVertexes of crop:\n")
    print("Left:", left, " Right:", right)
    print("\nTop:", top, "Bottom:", bottom)
    crop1 = raster[top:bottom]
    crop2 = []
    for row in crop1:
        crop2.append(row[left:right])
    return crop2

def dilateRaster(raster, size=5, occupied=0):
    """Dilate the raster by convolution of size x size matrix of 1's
        size parameter should be an odd value."""
    i = int((size-1)/2)
    row = 0
    max_row = len(raster)-1
    max_col = len(raster[1])-1
    toDilate = []
    for line in raster: #collect pixels to dilate first
        col = 0
        for value in line:
            if value == occupied:
                for rowmod in range(-i, i+1):
                    for colmod in range(-i, i+1):
                        if row+rowmod > 0 and col+colmod > 0 and row+rowmod <= max_row and col+colmod <= max_col:
                            cVal = raster[row+rowmod][col+colmod]
                            if cVal != occupied:
                                toDilate.append((row+rowmod, col+colmod))
            col = col+1
        row = row+1
    for tup in toDilate: #iterate through collected pixel tuples to set values
        raster[tup[0]][tup[1]] = occupied
    return raster

def read_pgm(pgmf):
    """Return a raster of integers from a PGM as a list of lists."""
    assert pgmf.readline() == b'P5\n'
    pgmf.readline() #trash line, remove if there is no padding line
    (width, height) = [int(i) for i in pgmf.readline().split()]
    depth = int(pgmf.readline())
    assert depth <= 255

    raster = []
    for y in range(height):
        row = []
        for y in range(width):
            row.append(ord(pgmf.read(1)))
        raster.append(row)
    return raster

def main(argv):
    inputfile = ''
    outputfile = ''
    crop = 0
    pgm = 0
    dilate = 0
    try:
        opts, args = getopt.getopt(argv,"hbcd:i:o:",["dilate=","ifile=","ofile="])
    except getopt.GetoptError:
        print(str(getopt.err))
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("pgm_tool.py [-b] [-c] [-d <size>] -i <inputfile> -o <outputfile>")
            sys.exit(2)
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt == '-b':
            print("Outputting as PGM.")
            pgm = 1
        elif opt == '-c':
            print("Cropping margins.")
            crop = 1
        elif opt in ("-d", "--dilate"):
            print("Dilating raster with size " + str(int(arg)) + ".")
            dilate = int(arg)
    print("Input file is", inputfile)
    print("Output file is", outputfile)
    if inputfile:
        with open(inputfile, 'rb') as f:
            raster = read_pgm(f)
            if crop:
                raster = cropRaster(raster, 205)
            if dilate:
                raster = dilateRaster(raster, dilate, 0)
            if outputfile and not pgm:
                with open(outputfile, 'w+') as o:
                    for line in raster:
                        for val in line:
                            o.write(str(val) + ',')
                        o.write('\n')
            if outputfile and pgm:
                with open(outputfile, 'w+b') as o:
                    flat_raster = [item for sublist in raster for item in sublist]
                    #pythonic unpacking of list of lists above
                    height = len(raster)
                    width = len(raster[1])
                    o.write(bytes('P5' + '\n' + '# CREATOR: pgm_tool.py 0.02\n', encoding='utf8'))
                    o.write(bytes(str(width) + ' ' + str(height) + '\n' + str(255) + '\n', encoding='utf8'))
                    rasterbytes = bytes(flat_raster)
                    o.write(rasterbytes)
            
if __name__ == "__main__":
    main(sys.argv[1:])
