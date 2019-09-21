#!/Users/xumingkuan/anaconda3/bin/python

import getopt,sys
import multiprocessing
import time

class Counter(object):
    def __init__(self, initval=0):
        self.val = multiprocessing.Value('i', initval)
        self.lock = multiprocessing.Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def add_k(self,k):
        with self.lock:
            self.val.value += k

    def value(self):
        with self.lock:
            return self.val.value

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


def catagorize_barcode(line):
    '''
    The following code is used to handle each barcode in the fragment file.
    '''

    (fragments, barcode) = extract_from_line(line.rstrip('\n'))

    print("Here!")
    if barcode in barcode_list:
        # A perfect match
        frag_0_mismatch.add_k(fragments)
        bar_0_mismatch.increment()
    else:
        mismatch = find_most_similar_barcode(barcode,barcode_list)
        if mismatch == 1:
            frag_1_mismatch.add_k(fragments)
            bar_1_mismatch.increment()
        else:
            frag_2_mismatch.add_k(fragments)
            bar_2_mismatch.increment()
    return


def find_barcode_info(barcode_list,fragmentsfilename):

    pool = multiprocessing.Pool(MAX_CORE)

    f = open(fragmentsfilename,"r")
    print('Catagorizing barcodes...')

    total_fragements = 0


    while(True):
        line = f.readline().rstrip('\n')
        if not line:
            break
        total_fragements+=1
        pool.apply_async(catagorize_barcode, (line,))
        # pool.apply_async(print_line,(line,))

    # time.sleep(3)
    # pool.wait()
    pool.close()
    pool.join()

    f.close()


    # Display results

    print()
    print('Number of Fragments in Total: %d' % (total_fragements))
    print('Number of Barcodes Provided: %d' % len(barcode_list))

    print("0  mismatch: %d fragments from %d barcodes" % (frag_0_mismatch.value(),bar_0_mismatch.value()))
    print("1  mismatch: %d fragments from %d barcodes" % (frag_1_mismatch.value(),bar_1_mismatch.value()))
    print("2+ mismatch: %d fragments from %d barcodes" % (frag_2_mismatch.value(),bar_2_mismatch.value()))

    return

# def print_line(line):
#     print("Here")
#     counter.increment()
#     print("Here")
#     return

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

unixOptions = "b:f:m:hc:"
gnuOptions = ["barcodes=", "fragments=", "max=","help","core="]


try:
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))
    sys.exit(2)

MISMATCH_LIMIT = 1 # Number of mismatch tolerated. Default 1.
MAX_CORE = 10

barcode_list = []

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
    elif currentArgument in ("-m", "--max"):
        print(currentValue)
        MAX_CORE = int(currentValue)
    elif currentArgument in ("-h", "--help"):
        print("-b --barcodes  : barcodes.txt")
        print("-f --fragments : fragments.txt")
        print("-m --max       : max-mismatch-tolerated (default 1)")
        print("-c --core      : max-core-usage (default 1)")
        exit()


frag_0_mismatch = Counter(0)
frag_1_mismatch = Counter(0)
frag_2_mismatch = Counter(0)

bar_0_mismatch = Counter(0)
bar_1_mismatch = Counter(0)
bar_2_mismatch = Counter(0)

find_barcode_info(barcode_list,fragement_filename)
