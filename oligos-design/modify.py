from argparse import ArgumentParser

POSITION_OF_SNP = 86

def check_if_ref(enhancer,ref):
    '''
    Check if the enhancer is a reference.
    '''
    return enhancer[POSITION_OF_SNP-1:POSITION_OF_SNP-1+len(ref)] == ref

def check_if_alt(enhancer,alt):
    '''
    Chekc if the enhancer is an alternative.
    '''
    if len(alt.split(','))==1:
        if(enhancer[POSITION_OF_SNP-1:POSITION_OF_SNP-1+len(alt)] == alt):
            return True
    else:
        for each_alt in alt.split(','):
            if(enhancer[POSITION_OF_SNP-1:POSITION_OF_SNP-1+len(each_alt)] == each_alt):
                return True
    return False

def build_oligo_snp_library(oligo_snps,filename):
    '''
    Load all snps in the oligo input file and stored into a set.
    '''
    with open(filename,'r') as f_oligo:
        for line in f_oligo:
            snp = line.split(',')[0].split('_')[0][1:]
            oligo_snps.add(snp)

def load_snp_info(snps,snp_filename,snp_dic):
    '''
    Extract info from the provided snp file.
    '''
    with open(snp_filename) as f_snp:
        for line in f_snp:
            line_info = line.split('	')
            rsid = line_info[2]
            if rsid not in snps:
                continue
            ref = line_info[3] # Reference base
            alt = line_info[4] # Alternative base
            snp_dic[rsid] = (ref,alt)

def categorize_oligo_snp(oligo_filename,output_filename,snp_dic,exceptions):
    '''
    For each oligo snp,
    (1) check if a corresponding rsid could be found.
    (2) check if it is a reference, alternative, neither, or both.
        - is ref(expected): put alt
        - is alt(abnormal): put ref & log
        - neither(abnormal): log
        - both(cannot determine): assume as ref, put alt & log
    '''
    f_oligo = open(oligo_filename,'r')
    f_output = open(output_filename,'w+')

    for line in f_oligo:
        rsid = line.split(',')[0].split('_')[0][1:]
        if rsid not in snp_dic:
            exceptions[4].append(line)
            continue
        else:
            enhancer = line.split(',')[1]
            is_ref = check_if_ref(enhancer,snp_dic[rsid][0])
            is_alt = check_if_alt(enhancer,snp_dic[rsid][1])

            if is_ref:
                for each_alt in snp_dic[rsid][1].split(','):
                    output_enhancer = enhancer[:POSITION_OF_SNP-1]+each_alt+enhancer[POSITION_OF_SNP-1+len(snp_dic[rsid][0]):]
                    if(output_enhancer==enhancer):
                        print("Error! Please report.")
                    f_output.write(line.split(',')[0]+','+output_enhancer)
            else:
                if not is_alt: # Neither
                    exceptions[2].append(line)
                else: # Alternative only
                    exceptions[1].append(line)

    f_oligo.close()
    f_output.close()

def report_result(exceptions,oligo_snps):
    '''
    Display result and edge case handling.
    '''
    print("\n\nResult Overview:")
    print("Examined %d snps in the oligo file." % (len(oligo_snps)))
    print("Reference only:   %2d" % (len(oligo_snps)-sum([len(exceptions[i]) for i in range(1,5)])))
    print("Alternative only: %2d" % len(exceptions[1]))
    print("Neither Ref/Alt:  %2d" % len(exceptions[2]))
    print("Cannot find rsid: %2d" % len(exceptions[4]))

def log_exceptions(exceptions,exception_filename):
    with open(exception_filename,'w+') as f_exp:
        f_exp.write('No rsid found:\n')
        for each in exceptions[4]:
            f_exp.write(each)

        f_exp.write('Alternative only:\n')
        for each in exceptions[1]:
            f_exp.write(each)

        f_exp.write('Neither Ref/Alt:\n')
        for each in exceptions[2]:
            f_exp.write(each)


def main():

    parser = ArgumentParser(description='provide oligo and snp files') ## add parser
    parser.add_argument('-s', help='snp file', required=True)
    parser.add_argument('-l', help='oligo file', required=True)
    parser.add_argument('-o', help='output file', required=False)
    parser.add_argument('-e', help='exception file', required=False)
    options = parser.parse_args()

    '''
    Debug use only


    snp_filename = 'sample_snps.txt'
    oligo_filename = 'sample_oligo.csv'
    output_filename = 'output.csv'
    exception_filename = 'excpetions.txt'
    '''


    # # Filename for enhancer, snp, and output files
    snp_filename = options.s
    oligo_filename = options.l
    if not options.o:
        output_filename = 'output.csv'
    else:
        output_filename = options.o
    if not options.e:
        exception_filename = 'excpetions.txt'
    else:
        exception_filename = options.e

    # Find all snps in the oligo input
    oligo_snps = set() # A list to record all snps in the snp input.
    build_oligo_snp_library(oligo_snps,oligo_filename)

    # Find all corresponding rsid in the snp file
    snp_dic = {}
    load_snp_info(oligo_snps,snp_filename,snp_dic)

    # Categorize oligo snps
    exceptions = {1:[],2:[],3:[],4:[]} # alt,neither,both,no_rs_id
    categorize_oligo_snp(oligo_filename,output_filename,snp_dic,exceptions)
    report_result(exceptions,oligo_snps)
    log_exceptions(exceptions,exception_filename)


if __name__== "__main__":
    main()
