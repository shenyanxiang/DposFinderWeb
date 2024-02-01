import os
import pandas as pd

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
        
def parse_protein_prediction(job_dir):
    filename = os.path.join(job_dir,'outputs/result.tsv')
    df = pd.read_csv(filename, sep='\t')
    df.columns = ['protein_id', 'prediction_score', 'length', 'identity']
    result = df.to_json(orient='records')
    return result
        
def parse_genome_prediction(job_dir):
    filename = os.path.join(job_dir,'outputs/result.tsv')
    df = pd.read_csv(filename, sep='\t')
    df.columns = ['contig_id', 'locus_tag', 'location', 'prediction_score', 'length', 'identity']
    result = df.to_json(orient='records')
    return result

def parse_blast_result(dir):
    filename = os.path.join(dir, 'Blastp_summary.tsv')
    df = pd.read_csv(filename, sep='\t')
    df.columns = ['hit_id', 'identity', 'query_coverage', 'evalue', 'bit_score']
    result = df.to_json(orient='records')
    return result

def read_secondary_structure(file):
    with open(file, 'r') as f:
        lines = f.readlines()
    amino_acids = lines[1].strip()
    secondary_structure = lines[2].strip()
    
    results = [{'pos': i+1, 'aa': aa, 'ss': ss} for i, (aa, ss) in enumerate(zip(amino_acids, secondary_structure))]
    return results
