#!/Users/xumingkuan/anaconda3/bin/python

import getopt,sys
import multiprocessing
import time

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
    return (int(fragments),barcode)


def find_one_mismatch(barcode_set,barcode):
    bp = ['A','G','T','C']

    for i in range(len(barcode)):
        bp.remove(barcode[i].upper())
        for each in bp:
            newbarcode = barcode[:i]+each+barcode[i+1:]
            if newbarcode in barcode_set:
                return 1
        bp.append(barcode[i].upper())
    return 2


def catagorize_barcode(line,barcode_set):
    '''
    The following code is used to handle each barcode in the fragment file.
    It will insert an info entry into the barcode_info list.
    An info entry has a form of (barcode, # of fragments, 0/1 mismatch).
    '''
    (fragments, barcode) = extract_from_line(line.rstrip('\n'))

    if barcode in barcode_set:
        match_type = 0
    else:
        match_type = find_one_mismatch(barcode_set,barcode)
    return (barcode, fragments, match_type)

def find_barcode_info(fragmentsfilename,barcodes):

    # Build barcode index
    barcode_set = set(barcodes) # A set structre makes the lookup faster.

    if len(barcodes) == len(barcode_set):
        print("%d barcodes are provided. All of them are unique." % len(barcodes))
    else:
        print("%d barcodes are provided. %d of them are unique." % (len(barcodes),len(barcode_set)))

    f = open(fragmentsfilename,"r")
    # f = open(outputfile,"w")
    print('Catagorizing barcodes...')

    frag_info = [0,0,0,0]
    barcode_info = [0,0,0,0]
    match_type = 0
    # 0 - perfect match
    # 1 - unique 1-mismatched
    # 2 - 2 or more misamtch
    # 3 - 1-mismatched to 2 or more barcodes.
    num_of_fragments = 0 # Number of fragments in this line.

    total_fragements = 0
    while(True):
        line = f.readline().rstrip('\n')
        if not line:
            break
        total_fragements+=1
        (barcode, num_of_fragments,match_type) = catagorize_barcode(line,barcode_set)
        frag_info[match_type]+=num_of_fragments
        barcode_info[match_type]+=1
    f.close()

    # Display results
    print('\n')
    print('Number of Lines in Total: %d' % (total_fragements))
    print('Number of Barcodes Provided: %d' % len(barcodes))

    print("0   mismatch: %d fragments from %d barcodes" % (frag_info[0],barcode_info[0]))
    print("1   mismatch: %d fragments from %d barcodes" % (frag_info[1],barcode_info[1]))
    print("2+  mismatch: %d fragments from %d barcodes" % (frag_info[2],barcode_info[2]))
    print("Match with 2: %d fragments from %d barcodes" % (frag_info[3],barcode_info[3]))

    print('')
    return

def write_output(barcode,fragments):
    '''
    This function writes line info into a file.
    Var fragments refers to the number of fragments matched with the given barcode.
    Var type: 0 refers to perfect match & 1 refers to 1 mismatch.
    '''
    f_out = open(OUTPUT_FILENAME,"w")

    f_out.close()

# read commandline arguments, first
fullCmdArguments = sys.argv

# - further arguments
argumentList = fullCmdArguments[1:]

unixOptions = "b:f:h0:"
gnuOptions = ["barcodes=", "fragments=","help","output="]


try:
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))
    sys.exit(2)

OUTPUT_FILENAME = "output.txt"

if(len(arguments)==0):
    barcodes = from_file_to_barcode_list('all-barcodes-test.txt')
    # barcodes = from_file_to_barcode_list('barcode-output.txt')

    fragement_filename = 'sorted-fragments-test.txt'

for currentArgument, currentValue in arguments:
    if currentArgument in ("-b", "--barcodes"):
        # print(currentValue)
        barcodes = from_file_to_barcode_list(currentValue)
    elif currentArgument in ("-f", "--fragments"):
        # print(currentValue)
        fragement_filename = currentValue
    elif currentArgument in ("-o", "--output"):
        OUTPUT_FILENAME = currentValue
    elif currentArgument in ("-h", "--help"):
        print("-b --barcodes  : barcodes.txt")
        print("-f --fragments : fragments.txt")
        print("-o --output    : output-filename (default output.txt)")
        exit()


find_barcode_info(fragement_filename,barcodes)
