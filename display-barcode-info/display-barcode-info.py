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
# def catagorize_barcode(line):

    '''
    The following code is used to handle each barcode in the fragment file.
    It will insert an info entry into the barcode_info list.
    An info entry has a form of (barcode, # of fragments, 0/1 mismatch).
    '''

    (fragments, barcode) = extract_from_line(line.rstrip('\n'))

    if barcode in barcode_set:
        # A perfect match
        frag_0_mismatch.add_k(fragments)
        bar_0_mismatch.increment()
        # line_info.append((barcode,fragments,0))
        print(barcode,fragments,0)
        # all_involved_barcode.append(barcode)
    else:
        (mismatch,matched_barcode) = find_most_similar_barcode(barcode)
        if mismatch == 1:
            frag_1_mismatch.add_k(fragments)
            bar_1_mismatch.increment()
            # line_info.append((matched_barcode,fragments,1))
            print(matched_barcode,fragments,1)
            # all_involved_barcode.append(matched_barcode)
        elif mismatch == 0: # This means it has two 1-mismatched barcodes in the whitelist. Does not mean perfect match.
            frag_match_2.add_k(fragments)
            bar_match_2.increment()
        else:
            frag_2_mismatch.add_k(fragments)
            bar_2_mismatch.increment()

    return

def find_barcode_info(fragmentsfilename):

    pool = multiprocessing.Pool(MAX_CORE)


    # m = multiprocessing.Manager()
    # line_info = m.list()
    # all_involved_barcode = m.list()

    f = open(fragmentsfilename,"r")
    print('Catagorizing barcodes...')


    total_fragements = 0


    while(True):
        line = f.readline().rstrip('\n')
        if not line:
            break
        total_fragements+=1
        pool.apply_async(catagorize_barcode, (line,))
        # pool.apply_async(catagorize_barcode, (line,))

        # pool.apply_async(print_line,(line,))

    # time.sleep(3)
    # pool.wait()
    pool.close()
    pool.join()

    f.close()

    # Display results

    print('\n')
    print('Number of Lines in Total: %d' % (total_fragements))
    print('Number of Barcodes Provided: %d' % len(barcode_list))

    print("0   mismatch: %d fragments from %d barcodes" % (frag_0_mismatch.value(),bar_0_mismatch.value()))
    print("1   mismatch: %d fragments from %d barcodes" % (frag_1_mismatch.value(),bar_1_mismatch.value()))
    print("2+  mismatch: %d fragments from %d barcodes" % (frag_2_mismatch.value(),bar_2_mismatch.value()))

    print("Match with 2: %d fragments from %d barcodes" % (frag_match_2.value(),bar_match_2.value()))

    print('')

    '''
    print('Number of Involved Barcodes: %d' % len(all_involved_barcode))

    all_involved_barcode = set(all_involved_barcode)
    print('Number of Unique Involved Barcodes: %d' % len(all_involved_barcode))

    print('')

    for each in line_info:

    print('Writing into the output file')
    write_output(line_info)
    '''

    return

def load_potential_barcodes_from_index(barcode):
    '''
    Find all possible barcodes with at most 1-mismatch from the index.
    '''
    number_of_A = barcode.count("A")
    number_of_G = barcode.count("G")
    compare_list = []

    possible_match_A_G = [(number_of_A, number_of_G),
                          (number_of_A+1, number_of_G),
                          (number_of_A-1, number_of_G),
                          (number_of_A, number_of_G+1),
                          (number_of_A, number_of_G-1),
                          (number_of_A+1, number_of_G-1),
                          (number_of_A-1, number_of_G+1)]
    for each in possible_match_A_G:
        try:
            compare_list.extend(d_barcode_index[each[0]][each[1]])
        except KeyError:
            continue
            # print("Key not found in index: %d, %d" % (each[0],each[1]))
    return compare_list


    return d_barcode_index[number_of_A][number_of_G]
def find_most_similar_barcode(barcode):
    '''
    Find the most similar barcode from the barcode list and return its number of mismatch.
    '''
    smallest_mismatch = MISMATCH_LIMIT+1
    smallest_mismatch_barcode = ''

    compare_list = load_potential_barcodes_from_index(barcode)
    number_of_1_mismatch = 0
    for each in compare_list:
        current_mismatch = compare_barcodes(barcode,each)
        if current_mismatch ==1:
            number_of_1_mismatch +=1
            smallest_mismatch_barcode = each
            if number_of_1_mismatch ==2:
                print("Identify barcode w/ two 1-mismatch candidates!")
                return (0,smallest_mismatch_barcode)
            # return 1 # Already the smallest mismatch
        if current_mismatch<smallest_mismatch:
            smallest_mismatch =  current_mismatch
    # if smallest_mismatch == MISMATCH_LIMIT+1:
        # print("Mismatch Found: %s" % barcode)
    return (smallest_mismatch, smallest_mismatch_barcode)

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

def write_output(line_info):
    '''
    This function writes line info into a file.
    Var fragments refers to the number of fragments matched with the given barcode.
    Var type: 0 refers to perfect match & 1 refers to 1 mismatch.
    '''
    f_out = open(OUTPUT_FILENAME,"w")

    f_out.close()


def build_barcode_index():
    '''
    Build a simple barcode index based on the number of As & Gs.

    dic = { 0: {0:["TTTTT","CCCCC"], ...}
            1: {0:["ATTTT","ACCCC"], ...}
          }

    '''
    print('Building barcode index...')
    for each in barcode_list:
        number_of_A = each.count('A')
        number_of_G = each.count('G')
        if number_of_A not in d_barcode_index:
            d_barcode_index[number_of_A] = {}
        if number_of_G not in d_barcode_index[number_of_A]:
            d_barcode_index[number_of_A][number_of_G] = []
        d_barcode_index[number_of_A][number_of_G].append(each)


# read commandline arguments, first
fullCmdArguments = sys.argv

# - further arguments
argumentList = fullCmdArguments[1:]

unixOptions = "b:f:m:hc:0:"
gnuOptions = ["barcodes=", "fragments=", "max=","help","core=","output="]


try:
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))
    sys.exit(2)

MISMATCH_LIMIT = 1 # Number of mismatch tolerated. Default 1.
MAX_CORE = 1
OUTPUT_FILENAME = "output.txt"

barcode_list = []
barcode_set = set([])

if(len(arguments)==0):
    # barcode_list = from_file_to_barcode_list('given-barcodes-test.txt')
    barcode_list = from_file_to_barcode_list('barcode-output.txt')
    barcode_set = set(barcode_list)
    fragement_filename = 'sorted-fragments-test.txt'
for currentArgument, currentValue in arguments:
    if currentArgument in ("-b", "--barcodes"):
        # print(currentValue)
        barcode_list = from_file_to_barcode_list(currentValue)
        if len(barcode_list) == len(set(barcode_list)):
            print("%d barcodes are provided. All of them are unique." % len(barcode_list))
        else:
            print("%d barcodes are provided. %d of them are unique." % (len(barcode_list),len(set(barcode_list))))
        barcode_set = set(barcode_list)
    elif currentArgument in ("-f", "--fragments"):
        # print(currentValue)
        fragement_filename = currentValue
    elif currentArgument in ("-m", "--max"):
        # print(currentValue)
        MISMATCH_LIMIT = int(currentValue)
    elif currentArgument in ("-c", "--core"):
        # print(currentValue)
        MAX_CORE = int(currentValue)
    elif currentArgument in ("-o", "--output"):
        OUTPUT_FILENAME = currentValue
    elif currentArgument in ("-h", "--help"):
        print("-b --barcodes  : barcodes.txt")
        print("-f --fragments : fragments.txt")
        print("-m --max       : max-mismatch-tolerated (default 1)")
        print("-c --core      : max-core-usage (default 1)")
        print("-o --output    : output-filename (default output.txt)")
        exit()


frag_0_mismatch = Counter(0)
frag_1_mismatch = Counter(0)
frag_2_mismatch = Counter(0)
frag_match_2 = Counter(0)

bar_0_mismatch = Counter(0)
bar_1_mismatch = Counter(0)
bar_2_mismatch = Counter(0)
bar_match_2 = Counter(0)


d_barcode_index = {}
build_barcode_index()

find_barcode_info(fragement_filename)
