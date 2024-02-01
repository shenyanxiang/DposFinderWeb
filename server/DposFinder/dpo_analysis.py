import argparse
import os
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import subprocess
import torch
import pandas as pd
import time
from packages.utils import draw_attn

base_dir = './dpos_db/valid_dpos'

# 遍历base_dir下的所有目录

for accession in os.listdir(base_dir):
    #判断sequence_result.tsv是否存在，如果存在则跳过
    if os.path.exists(os.path.join(base_dir, accession, 'sequence_result.tsv')):
        continue
    file = os.path.join(base_dir, accession, 'sequence.fasta')
    for record in SeqIO.parse(file, 'fasta'):
        annotation = record.description.split(' ', 1)[1].split(' [')[0] if len(record.description.split(' ', 1)) > 1 else 'None'
        protein = record.seq
        protein = protein.replace('X', 'A')
        X=ProteinAnalysis(str(protein))
        information = pd.DataFrame({'protein_name': [accession], 'length': [str(len(str(protein))) + ' a.a.'], 'annotation':[annotation], 'molecular_weight': [X.molecular_weight()], 'aromaticity': [X.aromaticity()], 'instability_index': [X.instability_index()],
                                    'isoelectric_point': [X.isoelectric_point()], 'flexibility': [sum(X.flexibility()) / len(X.flexibility())], 'protein_sequence': [str(protein)]})
        information['molecular_weight'] = information['molecular_weight'].round(2)
        information['aromaticity'] = information['aromaticity'].round(3)
        information['instability_index'] = information['instability_index'].round(2)
        information['isoelectric_point'] = information['isoelectric_point'].round(2)
        information['flexibility'] = information['flexibility'].round(3)
        information.to_csv(os.path.join(base_dir, accession, "information.tsv"), sep='\t', index=False)
        DposFinder_command = f"/public/yxshen/.conda/envs/DposFinder/bin/python DposFinder/main.py --mode predict --data_path {os.path.join(base_dir, accession)} --test_data sequence.fasta --return_attn"
        try:
            subprocess.run(DposFinder_command, shell=True, check=True)
        except subprocess.CalledProcessError:
            print(f"{accession} DposFinder failed")
        
        s4pred_command = f"/public/yxshen/.conda/envs/DposFinder/bin/python ./softwares/s4pred/run_model.py --outfmt fas {file} > {os.path.join(base_dir, accession, f'{accession}_ss.fasta')}"
        try:
            subprocess.run(s4pred_command, shell=True, check=True)
        except subprocess.CalledProcessError:
            print(f"{accession} s4pred failed")
        
        draw_attn(os.path.join(base_dir, accession), accession)

