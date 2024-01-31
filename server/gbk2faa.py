import sys
import os

from Bio import SeqIO


input_gbk = sys.argv[1]
output_fasta = os.path.join(os.path.dirname(input_gbk), 'sequence.fasta')

idx = 0
with open(output_fasta, 'w') as f:
    seq_record = SeqIO.read(input_gbk, 'genbank')
    for seq_feature in seq_record.features:
        if seq_feature.type == "CDS":
            idx += 1
            assert len(seq_feature.qualifiers['translation']) == 1
            annotation = {}
            if seq_feature.location.strand == 1:
                location = f'{seq_feature.location.start + 1}..{seq_feature.location.end}'
                strand = '(+)'
            else:
                location = f'{seq_feature.location.start + 1}..{seq_feature.location.end}'
                strand = '(-)'
                
            for key in ['gene', 'product', 'protein_id']:
                if key in seq_feature.qualifiers.keys():
                    annotation[key] = seq_feature.qualifiers[key][0]
            if 'locus_tag' in seq_feature.qualifiers.keys():
                locus_tag = seq_feature.qualifiers['locus_tag'][0]
            else:
                locus_tag= f'gp_{idx}'
            
            protein_sequence = seq_feature.qualifiers['translation'][0]
            f.write(f'>{seq_record.name}#{locus_tag}#{location}#{strand} {" ".join(["[" + key + "=" + value + "]" for key, value in annotation.items()])}\n {protein_sequence}\n')
