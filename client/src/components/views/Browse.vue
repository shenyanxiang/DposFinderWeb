<template>
    <div class="browse">
      <h1 class="ml-10">Detailed information of depolymerase {{ protein_id }}</h1>
      <el-container>
        <el-aside width="250px">
          <el-menu default-active="" class="sidebar">
            <el-menu-item index="1" data-block="block1" @click="handleMenuItemClick(1)">General information</el-menu-item>
            <el-menu-item index="2" data-block="block2" @click="handleMenuItemClick(2)">Protein sequence</el-menu-item>
            <el-menu-item index="3" data-block="block3" @click="handleMenuItemClick(3)">Sequence attention</el-menu-item>
            <el-menu-item index="4" data-block="block4" @click="handleMenuItemClick(4)">Disorder area prediction</el-menu-item>
            <el-menu-item index="5" data-block="block5" @click="handleMenuItemClick(5)">Genomic context</el-menu-item>
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
            <div slot="header" class="header">Disorder area prediction</div>
            <p>Protein disorder area predicted by <a href="https://iupred3.elte.hu/" target="_blank">IUPred3</a>. (Values above 0.5 indicate the disorder area)</p>
            <div id="disorder" style="height: 400px; width: 100%;"></div>
          </el-card>
          <el-card id="block5" class="mt-10">
            <div slot="header" class="header">Genomic context</div>
            <p>Display the upstream and downstream genes of the depolymerase by <a href="https://github.com/wilkox/gggenes" target="_blank">gggenes</a>.</p>
            <div>
              <el-image :src="proteinInfo.context_url"/>
            </div>
            <el-table :data="proteinInfo.context_table" height="300" style="width: 100%">
              <el-table-column prop="locus_tag" label="Locus tag" />
              <el-table-column prop="gene" label="Gene symbol" />
              <el-table-column prop="coordinates" label="Coordinates" />
              <el-table-column prop="protein_id" label="Protein id" :formatter="accession_formatter"/>
              <el-table-column prop="annotation" label="NCBI annotation" />
            </el-table>
          </el-card>
        </el-main>
      </el-container>
    </div>
  </template>
  
<script setup lang="ts">
import { defineProps, reactive, h } from 'vue';
import axios from 'axios';
import { onMounted } from 'vue';
import * as echarts from 'echarts';

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
    protein_sequence: '',
    context_url: '',
    context_table: [],
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
    const disorder_path = `http://127.0.0.1:5001/api/protein/${props.protein_id}/disorder`;
    axios.get(disorder_path)
    .then((res) => {
      console.log(res.data.data);
      const disorder = res.data.data;
      type EChartsOption = echarts.EChartsOption;

      var chartDom = document.getElementById('disorder')!;
      var myChart = echarts.init(chartDom);
      var option: EChartsOption;

      let data = [];
      for (let i = 0; i < disorder.length; i++) {
        data.push([disorder[i].position, disorder[i].score]);
      }

      option = {
        tooltip: {
          trigger: 'axis',
          position: function (pt) {
            return [pt[0], '10%'];
          }
        },
        toolbox: {
          feature: {
            dataZoom: {
              yAxisIndex: 'none'
            },
            restore: {},
            saveAsImage: {}
          }
        },
        xAxis: {
          type: 'category',
          min: 0,
          max: data.length
        },
        yAxis: {
          name: 'Disorder score',
          type: 'value',
          boundaryGap: [0, '100%'],
          min: 0,
          max: 1
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            start: 0,
            end: 100
          }
        ],
        series: [
          {
            type: 'line',
            smooth: false,
            symbol: 'none',
            data: data,
            markLine: {
              data: [
                {
                  yAxis: 0.5, 
                  label: {
                    show: true,
                    position: 'end',
                    formatter: '0.5' 
                  }
                }
              ]
            }
          }
        ]
      };

      option && myChart.setOption(option);
    })
    .catch((error) => {
      console.error(error);
    });
    const context_path = `http://127.0.0.1:5001/api/protein/${props.protein_id}/context`;
    axios.get(context_path, { responseType: 'arraybuffer'})
    .then((res) => {
      console.log(res.data);
      const blob = new Blob([res.data], { type: 'image/png' });
      proteinInfo.context_url = window.URL.createObjectURL(blob);
    })
    const context_table_path = `http://127.0.0.1:5001/api/protein/${props.protein_id}/context_table`;
    axios.get(context_table_path)
    .then((res) => {
      console.log(res.data);
      proteinInfo.context_table = res.data.data;
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

function accession_formatter(row: any, column: any, cellValue: any, index: number) {
  return h('a', { href: `https://www.ncbi.nlm.nih.gov/protein/${cellValue}/`, target: '_blank' }, cellValue);
}

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