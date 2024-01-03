import os


def dump_datetime(value):
    if value is None:
        return None
    return value.strftime('%Y-%m-%d %H:%M:%S')

def check_protein_fasta_file(fasta_file):
    out = os.path.join(os.path.dirname(fasta_file), 'info.txt')
    os.system(f'/public/yxshen/.conda/envs/DposFinder/bin/seqkit stats {fasta_file} > {out}')
    with open(out) as f:
        lines = f.readlines()
        if len(lines) == 0:
            return False
        format_, type_ = lines[1].split()[1:3]
        if format_.strip() == 'FASTA' and type_.strip() == 'Protein':
            return True
        else:
            return False
        
def check_genome_fasta_file(fasta_file):
    out = os.path.join(os.path.dirname(fasta_file), 'info.txt')
    os.system(
        f'/public/yxshen/.conda/envs/DposFinder/bin/seqkit stats {fasta_file} > {out}')
    with open(out) as f:
        lines = f.readlines()
        if len(lines) == 0:
            return False
        format_, type_, num_seqs = lines[1].split()[1:4]
        if format_.strip() == 'FASTA' and type_.strip() == 'DNA' and int(num_seqs.strip()) >= 1:
            return True
        else:
            return False
        
