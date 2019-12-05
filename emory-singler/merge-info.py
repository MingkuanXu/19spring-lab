def update_info(info,filename,i):
    with open(filename,'r') as f:
        f.readline() # First row
        for line in f:
            gene_id = line.split()[0]
            fpkm = line.split()[1]
            gene_name = line.split()[2]


            if gene_name not in info:
                info[gene_name] = [0 for i in range(5)]
            info[gene_name][i]+=float(fpkm)


            '''
            if gene_id not in info:
                info[gene_id] = gene_name
                continue
            if not gene_name == info[gene_id]:
                print('Error: Different gene name!')
                print(gene_id,gene_name,info[gene_id])
            '''
    return

def output_info(info):
    with open('output.xls','w+') as f:
        for gene in info:
            f.write(gene+' '+' '.join([str(each) for each in info[gene]])+'\n')
    return

if __name__ == "__main__":
    info = {}
    filename_list = ['CP.fpkm.xls','EOM.fpkm.xls','Mas.fpkm.xls','TA.fpkm.xls','Zygo.fpkm.xls']
    for i in range(len(filename_list)):
        update_info(info,filename_list[i],i)

    output_info(info)
    print(len(info))
