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

def filter_barcodes(barcode_list,all_barcodes):

    d_info = {} # A dict to record number of fragments in different mismatch levels.

    # Number of perfect matched barcodes
    perfect_matched = 0
    mismatched_barcodes = []

    for each in all_barcodes:
        if each in barcode_list:
            perfect_matched+=1
        else:
            mismatched_barcodes.append(each)
    print(len(all_barcodes))
    print('Number of Fragments in Total: %d' % len(all_barcodes))
    print('Fragments in Whitelist: %d' % perfect_matched)
    print('Mismatched Barcodes: %d' % len(mismatched_barcodes))

    d_info[0] = perfect_matched
    print()

    # Handle fragments with mismatched barcodes
    print('Catagorizing barcodes...')
    for each in mismatched_barcodes:
        mismatch_level = find_most_similar_barcode(each,barcode_list)
        if mismatch_level in d_info:
            d_info[mismatch_level]+=1
        else:
            d_info[mismatch_level]=1

    # Display results
    print()
    for key in d_info:
        if key == MISMATCH_LIMIT+1:
            print("%d+ mismatch: %d" % (key-1, d_info[key]))
        else:
            print("%d  mismatch: %d" % (key, d_info[key]))
    return


def find_most_similar_barcode(barcode,barcode_list):
    # Find the most similar barcode from the barcode list and return its number of mismatch.
    smallest_mismatch = MISMATCH_LIMIT+1
    for each in barcode_list:
        current_mismatch = compare_barcodes(barcode,each)
        if current_mismatch<smallest_mismatch:
            smallest_mismatch =  current_mismatch
    if smallest_mismatch == MISMATCH_LIMIT+1:
        print("Found Mismatch Barcode: %s" % barcode)
    return smallest_mismatch

def compare_barcodes(barcode1, barcode2):
    # Compare two barcodes one by one and return their number of mismatched nucleotides.
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
    all_barcodes = from_file_to_barcode_list("all-barcodes-test.txt")
    filter_barcodes(barcode_list,all_barcodes)
