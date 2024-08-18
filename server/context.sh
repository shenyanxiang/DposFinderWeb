#!/bin/bash

# 读取TSV文件中的accession号，并逐行处理
while IFS=$'\t' read -r accession
do
  # 运行命令
  sudo Rscript /public/yxshen/DposFinderWeb/server/plot_context.R -f "./dpos_db/valid_dpos/$accession/genes.csv" -o "/public/yxshen/DposFinderWeb/server/dpos_db/valid_dpos/$accession/context.png"
done < accessions.tsv