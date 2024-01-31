
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
        filename = file.split('.')[0]
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
                               'location': [i.split('#')[2] + ' ' + i.split('#')[3] for i in id], 'prediction_score': prob, 'length': [len(i) for i in protein]})
        result.to_csv(os.path.join(dir, "result.tsv"), sep='\t', index=False)

    print("Depolymerase prediction finished")
    return

def Blastp(args):
    dir = os.path.join(args.fasta_path, 'outputs')
    for file in os.listdir(dir):
        filename = file.split('.')[0]
        if filename.split('_')[-1] == 'Dpos':
            Blastp_command = f"blastp -query {os.path.join(dir, file)} -db /public/yxshen/Depolymerase/DepolymeraseDB/DepolymeraseDB -outfmt 6 -out {os.path.join(dir, filename)}_Blastp.tsv"
            try:
                subprocess.run(Blastp_command, shell=True, check=True)
            except subprocess.CalledProcessError:
                print(f"{file} Blastp failed")
                continue
            df = pd.read_csv(os.path.join(dir, f"{filename}_Blastp.tsv"), sep='\t', header=None)
            df = df[df[2] >= 30]
            df = df[df[3] >= 100]
            df = df[df[10] <= 1e-5]
            df = df[df[11] >= 50]
            id = df[1].values
            protein = []
            with open(os.path.join(dir, f"{file}"), 'r') as f:
                for record in SeqIO.parse(f, 'fasta'):
                    if record.id in id:
                        protein.append(record.seq)
            with open(os.path.join(dir, f"{filename}_Dpos.fasta"), 'a') as f:
                for i in range(len(id)):
                    f.write(f">{id[i]}\n{protein[i]}\n")

            os.remove(os.path.join(dir, f"{file}"))
            os.remove(os.path.join(dir, f"{filename}_Blastp.tsv"))

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
        X=ProteinAnalysis(str(protein))
        information = pd.DataFrame({'protein_name': [id], 'length': [str(len(str(protein))) + ' a.a.'], 'molecular_weight': [X.molecular_weight()], 'aromaticity': [X.aromaticity()], 'instability_index': [X.instability_index()],
                                    'isoelectric_point': [X.isoelectric_point()], 'flexibility': [sum(X.flexibility()) / len(X.flexibility())], 'protein_sequence': [str(protein)], 'coordinate': [record.id.split('#')[1]]})
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