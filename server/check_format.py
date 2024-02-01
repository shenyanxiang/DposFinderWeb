import os
import shutil

# 指定目录路径
directory = 'dpos_db/valid_dpos'

# 遍历目录
for root, dirs, files in os.walk(directory):
    for dir_name in dirs:
        # 获取子目录的序列号
        sequence_number = dir_name

        # 构建attn目录路径
        attn_directory = os.path.join(root, dir_name, 'attn')

        # 检查attn目录是否存在
        if os.path.exists(attn_directory):
            attn_npz_directory = os.path.join(attn_directory, 'attn_npz')
            if os.path.exists(attn_npz_directory):
                new_attn_npz_name = os.path.join(attn_npz_directory, f'{sequence_number}.npz')
                for file in os.listdir(attn_npz_directory):
                    old_attn_npz_name = os.path.join(attn_npz_directory, file)
                    os.rename(old_attn_npz_name, new_attn_npz_name)

            img_directory = os.path.join(attn_directory, 'img')
            if os.path.exists(img_directory):
                new_img_name = os.path.join(img_directory , f'{sequence_number}.png')
                for file in os.listdir(img_directory):
                    old_img_name = os.path.join(img_directory, file)
                    os.rename(old_img_name, new_img_name)

            pdf_directory = os.path.join(attn_directory, 'pdf')
            if os.path.exists(pdf_directory):
                new_pdf_name = os.path.join(pdf_directory, f'{sequence_number}.pdf')
                for file in os.listdir(pdf_directory):
                    old_pdf_name = os.path.join(pdf_directory, file)
                    os.rename(old_pdf_name, new_pdf_name)