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

def catagorize_barcode(line,barcode_set,full_barcode_table,one_mismatch_to_two_barcodes,one_mismatch):
    '''
    The following code is used to handle each barcode in the fragment file.
    It will insert an info entry into the barcode_info list.
    An info entry has a form of (barcode, # of fragments, 0/1 mismatch).
    '''
    (fragments, barcode) = extract_from_line(line.rstrip('\n'))

    if barcode in barcode_set:
        match_type = 0
    elif barcode in one_mismatch_to_two_barcodes:
        match_type = 3
    elif barcode in full_barcode_table:
        match_type = 1
        one_mismatch.append(barcode)
    else:
        match_type = 2
    print(barcode,fragments,match_type)
    return (barcode, fragments, match_type)

def find_barcode_info(fragmentsfilename,barcodes):

    # Build barcode index
    (unique_one_mismatch_barcodes,one_mismatch_to_two_barcodes) = build_full_barcode_table(barcodes)
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
    one_mismatch = []
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
        (barcode, num_of_fragments,match_type) = catagorize_barcode(line,barcode_set,unique_one_mismatch_barcodes,one_mismatch_to_two_barcodes,one_mismatch)
        frag_info[match_type]+=num_of_fragments
        barcode_info[match_type]+=1
    f.close()

    # Display results
    print(one_mismatch)
    print('\n')
    print('Number of Lines in Total: %d' % (total_fragements))
    print('Number of Barcodes Provided: %d' % len(barcodes))

    print("0   mismatch: %d fragments from %d barcodes" % (frag_info[0],barcode_info[0]))
    print("1   mismatch: %d fragments from %d barcodes" % (frag_info[1],barcode_info[1]))
    print("2+  mismatch: %d fragments from %d barcodes" % (frag_info[2],barcode_info[2]))
    print("Match with 2: %d fragments from %d barcodes" % (frag_info[3],barcode_info[3]))

    print('')
    return

def build_full_barcode_table(barcodes):
    '''
    This function is used to generate all the possible barcodes having one mistmatch
    to a barcode in the white list. We will use this list as index to check if a barcode
    can be catagorized.
    '''
    print("Building barcode index...")


    # This is a list that containts all the possible barcodes having one mistmatch
    # to at least two barcodes in the whitelist (and therefore cannot be catagorized).
    one_mismatch_to_two_barcodes = set()

    # This is a set that containts all the possible barcodes having one mistmatch
    # to one or more barcode in the whitelist (and therefore can be catagorized).
    full_barcode_table  = set()

    bp = ['A','G','T','C']
    barcode_set = set(barcodes)
    # In the following loop, we will store all the possible 1-mismatch barcodes
    # to unique_one_mismatch_barcodes at first, and do a set difference to remove
    # all the duplicates.
    for barcode in barcodes:
        for i in range(len(barcode)):
            bp.remove(barcode[i])
            for each in bp:
                newbarcode = barcode[:i]+each+barcode[i+1:]
                # if newbarcode in barcode_set:
                #     # Meaning this is a perfect match instead of a 1-mismatch.
                #     continue
                if newbarcode in full_barcode_table:
                #     # Meaning it has one mismatch to 2+ barcodes in the whitelist
                     one_mismatch_to_two_barcodes.add(newbarcode)
                else:
                    full_barcode_table.add(newbarcode)
            bp.append(barcode[i])
        print(len(full_barcode_table))

    # unique_one_mismatch_barcodes.difference(one_mismatch_to_two_barcodes)

    return (full_barcode_table,one_mismatch_to_two_barcodes)

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
