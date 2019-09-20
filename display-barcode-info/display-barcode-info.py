#!/Users/xumingkuan/anaconda3/bin/python

import getopt,sys


def from_file_to_barcode_list(filename):
    '''
    Load the barcode file into the memory
    '''
    print("Loading barcode.txt ...")
    f = open(filename,"r")
    barcodes = []
    while(True):
        line = f.readline().rstrip('\n')
        if not line:
            break
        barcodes.append(line)
    f.close()
    print()
    return barcodes

def extract_from_line(line):
    '''
    This function is used to extract barcode info from a line.
    '''
    (fragments,barcode) = line.strip().split(" ")
    return (fragments,barcode)

def filter_barcodes(barcode_list,fragmentsfilename):

    d_info = {} # A dict to record number of fragments in different mismatch levels.
    d_barcodes = {} # A dict to record all barcodes of a mismatch level.
    previous_barcode = '' # Record the previous barcode scanned
    previous_result = '' # Record the previous mismatch results
    perfect_matched = []

    # Declare two dicts to record barcode info
    for i in range(MISMATCH_LIMIT+2):
        d_info[i] = 0
        d_barcodes[i] = 0


    f = open(fragmentsfilename,"r")
    print('Catagorizing barcodes...')

    total_fragements = 0

    while(True):
        line = f.readline().rstrip('\n')
        if not line:
            break
        total_fragements+=1

        (fragments, barcode) = extract_from_line(line)
        '''
        The following code is used to handle each barcode in the file.
        '''

        if barcode in barcode_list:
            # A perfect match
            mismatch = 0
        else:
            mismatch = find_most_similar_barcode(barcode,barcode_list)

        d_barcodes[mismatch]+=1
        d_info[mismatch]+=int(fragments)

    f.close()


    # Display results
    print()
    print('Number of Fragments in Total: %d' % (total_fragements))
    print('Number of Barcodes Provided: %d' % len(barcode_list))
    for i in range(0, MISMATCH_LIMIT+1):
        print("%d  mismatch: %d fragments from %d barcodes" % (i, d_info[i],d_barcodes[i]))
    print("%d+ mismatch: %d fragments from %d barcodes" % (MISMATCH_LIMIT, d_info[MISMATCH_LIMIT+1],d_barcodes[MISMATCH_LIMIT+1]))
    return


def find_most_similar_barcode(barcode,barcode_list):
    '''
    Find the most similar barcode from the barcode list and return its number of mismatch.
    '''
    smallest_mismatch = MISMATCH_LIMIT+1
    for each in barcode_list:
        current_mismatch = compare_barcodes(barcode,each)
        if current_mismatch ==1:
            return 1 # Already the smallest mismatch
        if current_mismatch<smallest_mismatch:
            smallest_mismatch =  current_mismatch
    if smallest_mismatch == MISMATCH_LIMIT+1:
        print("Mismatch Found: %s" % barcode)
    return smallest_mismatch

def compare_barcodes(barcode1, barcode2):
    '''
    Compare two barcodes one by one and return their number of mismatched nucleotides.
    '''
    if not(len(barcode1)==len(barcode2)):
        print("Error: two barcodes differ in length!")
        print(barcode1)
        print(barcode2)
        exit()
    mismatch = 0
    for i in range(len(barcode1)):
        if(barcode1[i]==barcode2[i]):
            continue
        mismatch+=1
        if mismatch==MISMATCH_LIMIT+1:
            return mismatch
    if mismatch == 0:
        print("Error: two barcodes are the same!")
        print(barcode1)
        print(barcode2)
        exit()
    if mismatch>(MISMATCH_LIMIT+1):
        print("Error: barcode out of mismatch limit!")
        exit()
    return mismatch


# read commandline arguments, first
fullCmdArguments = sys.argv

# - further arguments
argumentList = fullCmdArguments[1:]

unixOptions = "b:f:m:h"
gnuOptions = ["barcodes=", "fragments=", "max=","help"]


try:
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))
    sys.exit(2)

MISMATCH_LIMIT = 1 # Number of mismatch tolerated. Default 1.

if(len(arguments)==0):
    barcode_list = from_file_to_barcode_list('given-barcodes-test.txt')
    fragement_filename = 'sorted-fragments-test.txt'

for currentArgument, currentValue in arguments:
    if currentArgument in ("-b", "--barcodes"):
        print(currentValue)
        barcode_list = from_file_to_barcode_list(currentValue)
    elif currentArgument in ("-f", "--fragments"):
        print(currentValue)
        fragement_filename = currentValue
    elif currentArgument in ("-m", "--max"):
        print(currentValue)
        MISMATCH_LIMIT = int(currentValue)
    elif currentArgument in ("-h", "--help"):
        print("-b --barcodes  : barcodes.txt")
        print("-f --fragments : fragments.txt")
        print("-m --max       : max-mismatch-tolerated (default 1)")
        exit()



filter_barcodes(barcode_list,fragement_filename)
