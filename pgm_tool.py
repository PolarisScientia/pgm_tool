#!/usr/bin/python3

import sys, getopt

def crop_raster(raster, cropval=205):
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
    try:
        opts, args = getopt.getopt(argv,"hbci:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print(str(err))
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("pgm_reading.py [-b] [-c] -i <inputfile> -o <outputfile>")
            sys.ext()
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
    print("Input file is", inputfile)
    print("Output file is", outputfile)
    if inputfile:
        with open(inputfile, 'rb') as f:
            raster = read_pgm(f)
            if crop:
                raster = crop_raster(raster, 205)
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
                    o.write(bytes('P5' + '\n' + '# CREATOR: pgm_reading.py 0.01\n', encoding='utf8'))
                    o.write(bytes(str(width) + ' ' + str(height) + ' ' + str(255) + '\n', encoding='utf8'))
                    rasterbytes = bytes(flat_raster)
                    o.write(rasterbytes)
            
if __name__ == "__main__":
    main(sys.argv[1:])
