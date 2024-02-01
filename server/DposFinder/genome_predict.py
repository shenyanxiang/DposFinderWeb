
import argparse
import os
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import subprocess
import torch
import pandas as pd
import time
from packages.utils import draw_attn


parser = argparse.ArgumentParser(
    description='Phage-encode depolymerase prediction, input: pre-assembled contigs')
parser.add_argument('-f', default='', type=str)
parser.add_argument('--fasta_path', type=str, default='data/',
                    help='path to fasta files')
parser.add_argument('--file_type', type=str, default='fasta', help='file type of input files')
parser.add_argument('--no_cuda', action='store_true', help='do not use cuda')

args = parser.parse_args()


def genome2protein(args):
    output_dir = os.path.join(args.fasta_path, 'outputs')
    file = 'sequence.fasta'
    filename = 'sequence'
    file_path = os.path.join(args.fasta_path, file)
    prodigal_command = f"/public/software/miniconda3/bin/prodigal -i {file_path} -a {output_dir}/{file} -o {output_dir}/{file}.gff -c -p meta -q -m"
    try:
        subprocess.run(prodigal_command, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"{file} Prodigal failed")
    with open(os.path.join(output_dir, f"{file}"), 'r') as f:
        for record in SeqIO.parse(f, 'fasta'):
            strand = '+' if record.description.split()[6]=='1' else '-'
            record.id = record.id.rsplit('_', 1)[0]+'#gp'+record.id.split('_')[-1]
            record.id = f"{record.id}#{record.description.split()[2]}..{record.description.split()[4]}#({strand})"
            with open(os.path.join(output_dir, f"{filename}_screened.fasta"), 'a') as f:
                if len(record.seq) >= 100:
                    if record.seq[-1] == '*':
                        f.write(f">{record.id}\n{record.seq[:-1]}\n")
                    else:
                        f.write(f">{record.id}\n{record.seq}\n")
    os.remove(os.path.join(output_dir, f"{file}"))
    os.remove(os.path.join(output_dir, f"{file}.gff"))
    return

def gbk2protein(args):
    output_dir = os.path.join(args.fasta_path, 'outputs')
    filename = 'sequence'
    file = 'sequence.fasta'
    file_path = os.path.join(args.fasta_path, file)
    with open(file_path, 'r') as f:
        for record in SeqIO.parse(f, 'fasta'):
            with open(os.path.join(output_dir, f"{filename}_screened.fasta"), 'a') as f:
                if len(record.seq) >= 100:
                    if record.seq[-1] == '*':
                        f.write(f">{record.id}\n{record.seq[:-1]}\n")
                    else:
                        f.write(f">{record.id}\n{record.seq}\n")

def DepoF(args):
    dir = os.path.join(args.fasta_path, 'outputs')
    for file in os.listdir(dir):
        filename = os.path.splitext(file)[0]
        if filename.split('_')[-1] == 'screened':
            DposFinder_command = f"/public/yxshen/.conda/envs/DposFinder/bin/python DposFinder/main.py --mode predict --data_path {dir} --test_data {file} {'--no_cuda' if args.no_cuda else ''}"
            try:
                subprocess.run(DposFinder_command, shell=True, check=True)
            except subprocess.CalledProcessError:
                print(f"{file} DposFinder failed")
            df = pd.read_csv(os.path.join(dir, f"{filename}_result.tsv"), sep='\t')
            df = df[df['pred'] == 1]
            id = df['label'].values
            prob = df['prob'].values
            prob = [round(p, 3) for p in prob]
            protein = []
            with open(os.path.join(dir, f"{file}"), 'r') as f:
                for record in SeqIO.parse(f, 'fasta'):
                    if record.id in id:
                        protein.append(record.seq)
            with open(os.path.join(dir, f"{filename}_Dpos.fasta"), 'a') as f:
                for i in range(len(id)):
                    f.write(f">{id[i]}#score:{prob[i]:.3f}\n{protein[i]}\n")

        result = pd.DataFrame({'contig_id': [i.split('#')[0] for i in id], 'locus_tag': [i.split('#')[1] for i in id], 
                               'location': [i.split('#')[2] + ' ' + i.split('#')[3] for i in id], 'prediction_score': prob, 'length': [len(i) for i in protein], 'identity': ['-' for i in protein]})
        result.to_csv(os.path.join(dir, "result.tsv"), sep='\t', index=False)

    print("Depolymerase prediction finished")
    return


def downstreamAnalysis(args):
    dir = os.path.join(args.fasta_path, 'outputs')
    protein_list = []
    for record in SeqIO.parse(os.path.join(dir, 'sequence_screened_Dpos.fasta'), 'fasta'):
        id = record.id.split('#')[0]+'_'+record.id.split('#')[1]
        protein_list.append(id)
        protein = record.seq
        os.makedirs(os.path.join(dir, id), exist_ok=True)
        with open(os.path.join(dir, id, f"{id}.fasta"), 'a') as f:
            f.write(f">{id}\n{protein}\n")
        blastp_command = f"/public/software/ncbi-blast-2.10.0+/bin/blastp -query {os.path.join(dir, id, f'{id}.fasta')} -db ./dpos_blast_db/dpos_blast_db -outfmt 6 -out {os.path.join(dir, id, 'Blastp.tsv')} -num_alignments 5"
        try:
            subprocess.run(blastp_command, shell=True, check=True)
        except subprocess.CalledProcessError:
            print(f"{id} Blastp failed")
        blast_result = pd.read_csv(os.path.join(dir, id, "Blastp.tsv"), sep='\t', header=None)
        blast_result.columns = ['query_id', 'subject_id', 'identity', 'alignment_length', 'mismatches', 'gap_opens', 'q_start', 'q_end', 's_start', 's_end', 'evalue', 'bit_score']
        blast_result_summary = pd.DataFrame(columns = ['hit_id', 'identity', 'query_coverage', 'evalue', 'bit_score'])

        for i in range(len(blast_result)):
            hit_id = blast_result['subject_id'][i]
            identity = blast_result['identity'][i]
            identity = round(identity, 1)
            query_coverage = (blast_result['q_end'][i]-blast_result['q_start'][i]+1) / len(protein)
            query_coverage = round(query_coverage*100, 1)
            evalue = blast_result['evalue'][i]
            bit_score = blast_result['bit_score'][i]
            blast_result_summary.loc[i] = [hit_id, identity, query_coverage, evalue, bit_score]
        
        blast_result_summary.to_csv(os.path.join(dir, id, "Blastp_summary.tsv"), sep='\t', index=False)

        protein_id = record.id.split('#')[0]
        identity = blast_result_summary[blast_result_summary['bit_score'] == blast_result_summary['bit_score'].max()]['identity'].values[0]
        result = pd.read_csv(os.path.join(dir, "result.tsv"), sep='\t')
        result.loc[result['contig_id'] == protein_id, 'identity'] = identity
        result.to_csv(os.path.join(dir, "result.tsv"), sep='\t', index=False)


        X=ProteinAnalysis(str(protein))
        information = pd.DataFrame({'protein_name': [id], 'length': [str(len(str(protein))) + ' a.a.'], 'molecular_weight': [X.molecular_weight()], 'aromaticity': [X.aromaticity()], 'instability_index': [X.instability_index()],
                                    'isoelectric_point': [X.isoelectric_point()], 'flexibility': [sum(X.flexibility()) / len(X.flexibility())], 'protein_sequence': [str(protein)], 'coordinate': [record.id.split('#')[2]+' '+record.id.split('#')[3]]})
        information['molecular_weight'] = information['molecular_weight'].round(2)
        information['aromaticity'] = information['aromaticity'].round(3)
        information['instability_index'] = information['instability_index'].round(2)
        information['isoelectric_point'] = information['isoelectric_point'].round(2)
        information['flexibility'] = information['flexibility'].round(3)
        information.to_csv(os.path.join(dir, id, "information.tsv"), sep='\t', index=False)
    for protein in protein_list:
        protein_dir = os.path.join(dir, protein)
        filename = f"{protein}.fasta"
        DposFinder_command = f"/public/yxshen/.conda/envs/DposFinder/bin/python DposFinder/main.py --mode predict --data_path {protein_dir} --test_data {filename} {'--no_cuda' if args.no_cuda else ''} --return_attn"
        try:
            subprocess.run(DposFinder_command, shell=True, check=True)
        except subprocess.CalledProcessError:
            print(f"{filename} get attention failed")
            continue
        s4pred_command = f"/public/yxshen/.conda/envs/DposFinder/bin/python ./softwares/s4pred/run_model.py --outfmt fas {os.path.join(protein_dir, filename)} > {os.path.join(protein_dir, protein +'_ss.fasta')}"
        try:
            subprocess.run(s4pred_command, shell=True, check=True)
        except subprocess.CalledProcessError:
            print(f"{filename} s4pred failed")
            continue
        draw_attn(protein_dir, protein)
        


if __name__ == '__main__':
    if torch.cuda.is_available():
        if args.no_cuda:
            print(
                "WARNING: You have a CUDA device, so you should probably run without --no_cuda")
        else:
            torch.set_default_tensor_type('torch.cuda.FloatTensor')
    os.makedirs(os.path.join(args.fasta_path, 'outputs'), exist_ok=True)
    print("*"*20+"Start predicting"+"*"*20)
    if args.file_type == 'fasta':
        print("1. Extract proteins from genomes, Prodigal is running...")
        genome2protein(args)
    else:
        print("1. Extract proteins from genbank files...")
        gbk2protein(args)
    print("*"*50)
    print("2. Predicting depolymerase...")
    start_time = time.time()
    DepoF(args)
    end_time = time.time()
    print("*"*50)
    print(f"Depolymerase prediction finished, time cost: {end_time-start_time:.2f}s")
    downstreamAnalysis(args)