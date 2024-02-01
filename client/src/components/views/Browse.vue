<template>
    <div class="browse">
      <h1 class="ml-10">Detailed information of depolymerase {{ protein_id }}</h1>
      <el-container>
        <el-aside width="200px">
          <el-menu default-active="" class="sidebar">
            <el-menu-item index="1" data-block="block1" @click="handleMenuItemClick(1)">General information</el-menu-item>
            <el-menu-item index="2" data-block="block2" @click="handleMenuItemClick(2)">Protein sequence</el-menu-item>
            <el-menu-item index="3" data-block="block3" @click="handleMenuItemClick(3)">Sequence attention</el-menu-item>
            <el-menu-item index="4" data-block="block4" @click="handleMenuItemClick(4)">Domain prediction</el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <el-card id="block1">
            <div slot="header" class="header">General information</div>
                <el-descriptions :column="1" border size = "large" class="mt-5">
                    <el-descriptions-item
                        label = "Protein name"
                        label-align="left"
                        align="right"
                    >
                        {{ protein_id }}
                    </el-descriptions-item>
                    <el-descriptions-item
                        label = "Protein length"
                        label-align="left"
                        align="right"
                    >
                        {{ proteinInfo.protein_length }}
                    </el-descriptions-item>
                    <el-descriptions-item
                        label = "NCBI annotation"
                        label-align="left"
                        align="right"
                    >
                        {{ proteinInfo.annotation }}
                    </el-descriptions-item>
                    <el-descriptions-item
                        label = "Molecular weight"
                        label-align="left"
                        align="right"
                    >
                        {{ proteinInfo.molecular_weight }} Da
                    </el-descriptions-item>
                    <el-descriptions-item
                        label = "Isoelectric point"
                        label-align="left"
                        align="right"
                    >
                        {{ proteinInfo.isoelectric_point }}
                    </el-descriptions-item>
                    <el-descriptions-item
                        label = "Aromaticity"
                        label-align="left"
                        align="right"
                    >
                        {{ proteinInfo.aromaticity }}
                    </el-descriptions-item>
                    <el-descriptions-item
                        label = "Instability index"
                        label-align="left"
                        align="right"
                    >
                        {{ proteinInfo.instability_index }}
                    </el-descriptions-item>
                    <el-descriptions-item
                        label = "Flexibility"
                        label-align="left"
                        align="right"
                    >
                        {{ proteinInfo.flexibility }}
                    </el-descriptions-item>
                </el-descriptions>
          </el-card>
          <el-card id="block2" class="mt-10">
            <div slot="header" class="header">Protein sequence</div>
            <el-button type="primary" class="mt-3" size="default" @click="downloadSequence">Download sequence</el-button>
            <div class="mt-5">
            <el-text size="small">
                >{{ protein_id }}
            </el-text>
            <br>
            <el-text size="small">
                {{ proteinInfo.protein_sequence }}
            </el-text>
            </div>
          </el-card>
          <el-card id="block3" class="mt-10">
            <div slot="header" class="header">Sequence attention and secondary structure</div>
            <div>
                <el-scrollbar height="600px"><el-image :src="proteinInfo.attn_url"/></el-scrollbar>
            </div>
            <div class="legend">
                <div class="legend-item">
                <div class="legend-color" style="background: #FC8D62;"></div>
                <div class="legend-label">Helix</div>
                </div>
                <div class="legend-item">
                <div class="legend-color" style="background: #66C2A5;"></div>
                <div class="legend-label">Strand</div>
                </div>
                <div class="legend-item">
                <div class="legend-color" style="background: #c8c9cc;"></div>
                <div class="legend-label">Coli</div>
                </div>
            </div>
          </el-card>
          <el-card id="block4" class="mt-10">
            <div slot="header" class="header">Domain prediction</div>
            <p>predicted by InterproScan</p>
            <br><br><br><br><br><br><br><br><br><br><br><br><br><br>
          </el-card>
        </el-main>
      </el-container>
    </div>
  </template>
  
<script setup lang="ts">
import { defineProps, reactive } from 'vue';
import axios from 'axios';
import { onMounted } from 'vue';

const props = defineProps({
protein_id: String
});

const proteinInfo = reactive({
    protein_length: '',
    annotation: '',
    molecular_weight: '',
    isoelectric_point: '',
    aromaticity: '',
    instability_index: '',
    flexibility: '',
    attn_url: '',
    protein_sequence: ''
});

const handleMenuItemClick = (index: number) => {
const blockId = `block${index}`;
const blockElement = document.getElementById(blockId);
if (blockElement) {
blockElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
};

const getProteinInfo = async () => {
    const path = `http://localhost:5001/api/protein/${props.protein_id}`;
    axios.get(path)
    .then((response) => {
        console.log(response.data.data.rows[0]);
        proteinInfo.protein_length = response.data.data.rows[0].length;
        proteinInfo.annotation = response.data.data.rows[0].annotation;
        proteinInfo.molecular_weight = response.data.data.rows[0].molecular_weight;
        proteinInfo.isoelectric_point = response.data.data.rows[0].isoelectric_point;
        proteinInfo.aromaticity = response.data.data.rows[0].aromaticity;
        proteinInfo.instability_index = response.data.data.rows[0].instability_index;
        proteinInfo.flexibility = response.data.data.rows[0].flexibility;
        proteinInfo.protein_sequence = response.data.data.rows[0].protein_sequence;
    })
    const attn_path = `http://127.0.0.1:5001/api/protein/${props.protein_id}/attn`;
    axios.get(attn_path, { responseType: 'arraybuffer'})
    .then((res) => {
      console.log(res.data);
      const blob = new Blob([res.data], { type: 'image/png' });
      proteinInfo.attn_url = window.URL.createObjectURL(blob);
    })
    .catch((error) => {
      console.error(error);
    });
};

const downloadSequence = () => {
  const element = document.createElement('a');
  const fileContent = `>${props.protein_id}\n${proteinInfo.protein_sequence}`;
  const file = new Blob([fileContent], {type: 'text/plain'});
  element.href = URL.createObjectURL(file);
  element.download = `${props.protein_id}.fasta`;
  document.body.appendChild(element);
  element.click();
};

onMounted(async () => {
    await getProteinInfo();
});

</script>

<style scoped>
.sidebar {
  position: fixed;
}
:deep(.ep-descriptions__title) {
  font-size: 24px!important;
}
:deep(.ep-descriptions__cell) {
  font-size: 20px!important;
}
:deep(.ep-descriptions__label) {
  font-size: 20px!important;
  font-weight: bold!important;
  width: 300px!important;
}
.header {
  font-size: 24px!important;
  font-weight: bold!important;
}
.legend {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-right: 20px;
}

.legend-color {
  width: 20px;
  height: 20px;
  margin-right: 5px;
}

.legend-label {
  font-size: 14px;
}
</style>