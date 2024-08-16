import os

base_dir = './dpos_db/valid_dpos'

for accession in os.listdir(base_dir):
    file = os.path.join(base_dir, accession, 'sequence.fasta')
    command = f'python ./softwares/iupred3/iupred3.py {file} long > ./dpos_db/valid_dpos/{accession}/disorders.txt'
    os.system(command)
