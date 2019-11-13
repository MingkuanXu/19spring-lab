# Single-Cell RNA Data Analysis 


### Running on TACC cluster 

Start an interactive computing session on TACC cluster with normal queue, 1 nodes, 1 total tasks and 120 minitues. ([Stampede2 User Guide](https://portal.tacc.utexas.edu/user-guides/stampede2#running-idev))
```
idev -p skx-dev -N 1 -n 1 -m 120 
```

### Fastq Trimming

- Use modify_r2.py to trim the last 20 nucleotides from read2.fastq. 
  - Approximately 12 minutes for a 70GB unzipped fastq file.

  ```
  python modify_r2.py -r1 read2.fq -o read2_trimmed.fq
  ```
- Compress the resulting fastq using gzip/pigz.

  ```
  pigz read2_trimmed.fq
  ```
  


### Usage of Cellranger

- Download the lastest 10X cellranger from [10X Genomics Software](https://support.10xgenomics.com/single-cell-gene-expression/software/downloads/latest).
- (Optional) Download the Human (GRCh38) or Mouse Reference Genome .
  ```
  curl -O http://cf.10xgenomics.com/supp/cell-exp/refdata-cellranger-GRCh38-and-mm10-3.1.0.tar.gz 
  ```
- Unpack file & add to $PATH.
  ```
  tar -xzvf cellranger-3.1.0.tar.gz
  export PATH=/path/to/cellranger-3.1.0:$PATH
  
  tar -xzvf refdata-cellranger-GRCh38-3.0.0.tar.gz
  ```

- Specifying input FASTQ files for 10x pipelines.
  - https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/fastq-input
  - Rename the files in the following format, where READ TYPE is "R1" or "R2".
    <pre>mv read.fastq.gz [Sample Name]_S1_L00[Lane Number]_[Read Type]_001.fastq.gz</pre>
    
- Start Cellranger count
  ```
  cellranger count --id=sample1 \
                   --transcriptome=/scratch/06211/mx31/data/ref_genome/refdata-cellranger-GRCh38-and-mm10-3.1.0 \
                   --fastqs=/scratch/06211/mx31/data/scRNA_seq/wt-fastq \
                   --sample=sample1 \
                   --expect-cells=1000 \
                   --chemistry=SC3Pv3
  ```


### Seurat Implementation

### Label
