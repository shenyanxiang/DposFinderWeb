import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, average_precision_score
import os
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import math
import logomaker as lm
import matplotlib as mpl
import matplotlib.patches as mpl_patches

def label2index(label):
    label_dict = {'neg': 0, 'pos': 1}
    index = label_dict[label]
    return index


def metrics(score, y):
    pred = (score > 0.5).float()
    score = score.view(-1).cpu().detach().numpy()
    pred = pred.view(-1).cpu().detach().numpy()
    y = y.view(-1).cpu().detach().numpy()
    accuracy = accuracy_score(y, pred)
    f1 = f1_score(y, pred)
    precision = precision_score(y, pred)
    recall = recall_score(y, pred)
    roc_auc = roc_auc_score(y, score)
    average_precision = average_precision_score(
        y, score)

    metrics_dict = {"Accuracy": accuracy, "Precision": precision,
                    "Recall": recall, "F1-score": f1, "AUC": roc_auc, "AUPRC": average_precision}
    return metrics_dict


def save_load_name(args, name=''):
    return name + '_' + args.model


def save_model(args, model, name=''):
    name = save_load_name(args, name)
    os.makedirs('./model/', exist_ok=True)
    torch.save(model, f'./model/{name}.pt')


def load_model(args, name=''):
    name = save_load_name(args, name)
    device = torch.device('cuda' if args.use_cuda else 'cpu')
    model = torch.load(f'./model/{name}.pt', map_location=device)
    return model

def draw_attn(output_dir, protein):
    
    mpl.rcParams['font.family'] = 'Arial'
    mpl.rcParams['axes.labelsize'] = 12
    mpl.rcParams['axes.titlesize'] = 14
    mpl.rcParams['legend.title_fontsize'] = 11
    mpl.rcParams['legend.fontsize'] = 11
    mpl.rcParams['xtick.labelsize'] = 11
    mpl.rcParams['ytick.labelsize'] = 11

    attn_dir = os.path.join(output_dir, 'attn')
    file = protein + '_ss.fasta'
    with open(os.path.join(output_dir, file), 'r') as f:
        lines = f.readlines()
        secondary_structure = lines[2].strip()

    ss_dict = {'H': 'H', 'E': 'E', 'C': 'T'}

    ss_block=[]
    prev_ss=None

    for idx, ss_type in enumerate(secondary_structure):
        idx +=1
        reduced_elem = ss_dict.get(ss_type, 'T')
        if idx != 0 and idx % 100 != 0:
            if reduced_elem != prev_ss:
                ss_block.append([reduced_elem, idx, idx])
                prev_ss = reduced_elem
            ss_block[-1][-1] = idx
        elif idx == 0:
            if reduced_elem != prev_ss:
                ss_block.append([reduced_elem, idx, idx])
                prev_ss = reduced_elem
            ss_block[-1][-1] = idx
        else:
            ss_block.append([reduced_elem, idx, (idx % 100 + 1) * 100])
            prev_ss = reduced_elem
            ss_block[-1][-1] = idx

    attn_dict = np.load(os.path.join(attn_dir, f"attn_npz/{protein}.npz"), allow_pickle=True)
    
    if not os.path.exists(os.path.join(attn_dir, 'img')):
        os.mkdir(os.path.join(attn_dir, 'img'))
    if not os.path.exists(os.path.join(attn_dir, 'pdf')):
        os.mkdir(os.path.join(attn_dir, 'pdf'))
    offset = .01
    for key, value in attn_dict.items():
        seq = list(value[0])
        attn = value[1]
        attn = np.log(attn)
        max_attn = max(attn)
        min_attn = min(attn)

        attn = (attn-min_attn) / (max_attn-min_attn)
        df = pd.DataFrame({'character': seq, 'value': attn})
        saliency_df = lm.saliency_to_matrix(
            seq=df['character'], values=df['value']+offset)

        rows = math.ceil(len(saliency_df) / 100)
        labels = [0.00, 0.25, 0.50, 0.75, 1.00]

        fig, axes = plt.subplots(rows, 1, figsize=(12, 2*rows))

        for i in range(rows):
            tempdf = saliency_df[i*100:(i+1)*100]
            tempdf.set_index(
                [pd.Index(np.array(tempdf.index)-100*i)], inplace=True)
            logo = lm.Logo(tempdf,
                        color_scheme='skylign_protein',
                        vpad=0,
                        width=0.8,
                        font_weight='normal',
                        ax=axes if rows == 1 else axes[i])
            
            start_idx = i * 100 + 1
            end_idx = min((i + 1) * 100, max(ss_block[-1][-1], len(secondary_structure)))

            sub_ss_block = []
            for ss_elem in ss_block:
                if ss_elem[1] <= end_idx and ss_elem[2] >= start_idx:
                    sub_ss_block.append([ss_elem[0], max(ss_elem[1], start_idx), min(ss_elem[2], end_idx)])
            
            for m,n in enumerate(sub_ss_block):
                ss_type,start,end=n
                if i == rows-1:
                    start-=1
                    end-=1
                if ss_type=="T":
                    logo.ax.add_patch(mpl_patches.Rectangle((start%100-0.4,-0.1),(end-start+1),0.003,color="#c8c9cc")) 
                elif ss_type=="H":
                    n_turns=np.ceil((end-start+1)/1.5)
                    x_val=np.linspace(start%100-0.3,end%100+0.5,100)
                    y_val=-0.13+0.1*(-0.4*np.sin(np.linspace(0,n_turns*2*np.pi,100))+1)/4
                    logo.ax.plot(x_val,y_val,linewidth=2.4,color="#FC8D62",scalex=False, scaley=False)
                elif ss_type=="E":
                    logo.ax.add_patch(mpl_patches.FancyArrowPatch((start%100-0.4, -0.1), (end%100+0.8, -0.1), mutation_scale=20, color="#66C2A5"))

            logo.ax.set_ylim([-0.2, 1])
            logo.ax.set_yticks(np.array(labels) + offset)
            logo.ax.set_yticklabels(labels)
            logo.ax.set_xlim([-1, 100])
            logo.ax.set_xticks([19, 39, 59, 79, 99])
            logo.ax.set_xticklabels(np.array([20, 40, 60, 80, 100]) + 100*i)
            logo.style_spines(visible=False)
            logo.style_spines(spines=['left'], visible=True)
            logo.ax.axhline(0.5, color='gray', linewidth=1, linestyle='--')
        
        plt.tight_layout()

        plt.savefig(os.path.join(attn_dir, f"img/{key}_attn.png"), dpi=300)
        plt.savefig(os.path.join(attn_dir, f"pdf/{key}_attn.pdf"))
        plt.close()

def plot_tsne(x, y, color_dict, title, output_dir,ignore_ylabel=False):
    
    tsne = TSNE(n_components=2, random_state=42)
    x_tsne = tsne.fit_transform(x)
    
    x_min, x_max = x_tsne.min(0), x_tsne.max(0)
    x_norm = (x_tsne - x_min) / (x_max - x_min)

    for i, (name, color) in enumerate(color_dict.items()):
        plt.scatter(x_norm[y == i, 0], x_norm[y == i, 1], c=color, alpha=0.8, s=10, label=name)
 
    plt.xlabel("T-SNE Dimension 1")
    if not ignore_ylabel:
        plt.ylabel("T-SNE Dimension 2")

    plt.title(title)
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(output_dir, f"img/tsne.png"), dpi=300)
    plt.savefig(os.path.join(output_dir, f"pdf/tsne.pdf"))
