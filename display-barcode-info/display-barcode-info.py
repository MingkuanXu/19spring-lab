MISMATCH_LIMIT = 2 # Number of mismatch tolerated

def from_file_to_barcode_list(filename):
    f = open(filename,"r")
    barcodes = []
    while(True):
        line = f.readline().rstrip('\n')
        if not line:
            break
        barcodes.append(line)
    f.close()
    return barcodes

def extract_barcode_from_line(line):
    '''
    This function is used to extract barcode info from a line.
    '''
    return line

def filter_barcodes(barcode_list,fragmentsfilename):

    d_info = {} # A dict to record number of fragments in different mismatch levels.
    d_info[0] = 0

    # Number of perfect matched barcodes
    perfect_matched = 0
    others = 0
    mismatched_barcodes = []

    f = open(fragmentsfilename,"r")
    while(True):
        line = f.readline().rstrip('\n')
        if not line:
            break
        barcode = extract_barcode_from_line(line)

        '''
        The following code is used to handle each barcode in the file.
        '''
        print('Catagorizing barcodes...')
        if barcode in barcode_list:
            d_info[0] +=1
        else:
            '''
            Handle fragments with mismatched barcodes
            '''
            others+=1
            mismatch_level = find_most_similar_barcode(barcode,barcode_list)
            if mismatch_level in d_info:
                d_info[mismatch_level]+=1
            else:
                d_info[mismatch_level]=1
    f.close()
    # Display results

    print('Number of Fragments in Total: %d' % (d_info[0]+others))
    print('Fragments in Whitelist: %d' % d_info[0])
    print('Mismatched Barcodes: %d' % others)
    print()
    for key in d_info:
        if key == MISMATCH_LIMIT+1:
            print("%d+ mismatch: %d" % (key-1, d_info[key]))
        else:
            print("%d  mismatch: %d" % (key, d_info[key]))
    return


def find_most_similar_barcode(barcode,barcode_list):
    '''
    Find the most similar barcode from the barcode list and return its number of mismatch.
    '''
    smallest_mismatch = MISMATCH_LIMIT+1
    for each in barcode_list:
        current_mismatch = compare_barcodes(barcode,each)
        if current_mismatch<smallest_mismatch:
            smallest_mismatch =  current_mismatch
    if smallest_mismatch == MISMATCH_LIMIT+1:
        print("Found Mismatch Barcode: %s" % barcode)
    return smallest_mismatch

def compare_barcodes(barcode1, barcode2):
    '''
    Compare two barcodes one by one and return their number of mismatched nucleotides.
    '''
    if not(len(barcode1)==len(barcode2)):
        print("Error: two barcodes differ in length!")
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

if __name__ == "__main__":
    barcode_list = from_file_to_barcode_list("given-barcodes-test.txt")
    filter_barcodes(barcode_list,"all-barcodes-test.txt")
