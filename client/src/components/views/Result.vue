<template>
  <div class = "result">
    <el-main>
      <div v-if="ifJobRunning">
        <el-row>
          <el-col :span="12" :offset="6">
            <el-alert title="This page will be refreshed every 10 seconds until the job is finished" type="info" show-icon />
            <el-descriptions title="Job processing monitor" :column="1" border size = "large">
              <el-descriptions-item
                label = "Job id"
                label-align="right"
                align="center"
                label-class-name = "job-id-label"
              >
                {{ job_id }}
              </el-descriptions-item>
              <el-descriptions-item
                label = "Task type"
                label-align="right"
                align="center"
              >
                {{ jobInfo.task_type }}
              </el-descriptions-item>
              <el-descriptions-item
                label = "Num. of sequences"
                label-align="right"
                align="center"
              >
                {{ jobInfo.num_seqs }}
              </el-descriptions-item>
              <el-descriptions-item
                label = "Submittion time"
                label-align="right"
                align="center"
              >
                {{ jobInfo.submit_time }}
              </el-descriptions-item>
              <el-descriptions-item
                label = "Current time"
                label-align="right"
                align="center"
              >
                {{ jobInfo.current_time }}
              </el-descriptions-item>
              <el-descriptions-item
                label = "Email"
                label-align="right"
                align="center"
              >
                {{ jobInfo.email }}
              </el-descriptions-item>
              <el-descriptions-item
                label = "Status"
                label-align="right"
                align="center"
              >
                {{ jobInfo.status }}
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
      </div>
      <div v-else>
        <div v-if="jobType">
          <el-row>
            <el-col :span="16" :offset="4">
              <h1>Depolymerase prediction result</h1>
              <el-text size="large">Job id: {{ job_id }}</el-text>
              <el-divider />
              <p>
                <vxe-button status="primary" @click="downloadSequence">Download sequences (.fasta)</vxe-button>
                <vxe-button class="ml-3" status="primary" @click="exportDataEvent">Download result table (.csv)</vxe-button>
              </p>
              <vxe-table
                ref="tableRef"
                empty-text="There were no depolymerases found in the input sequences."
                size = "medium"
                :row-config="{isCurrent: true, isHover: true}"
                :data="tableData">
                <vxe-column field="contig_id" title="Contig id"></vxe-column>
                <vxe-column field="prediction_score" title="Prediction score" :title-help="{message: '自定义帮助提示信息'}"></vxe-column>
                <vxe-column field="length" title="Length (a.a.)"></vxe-column>
                <vxe-column field="locus_tag" title="Locus tag"></vxe-column>
                <vxe-column field="location" title="Coordinates"></vxe-column>
                <vxe-column title="Detail">
                  <template #default="{ row }">
                    <vxe-button status="primary" @click="showDetail(row)">Detail</vxe-button>
                  </template>
                </vxe-column>
              </vxe-table>
              <el-dialog v-model="DetailVisible" title="Detail">
                <el-collapse v-model="activeNames">
                  <el-collapse-item title="Basic Information" name="1">
                    <div>
                      <el-descriptions :column="1" border size = "large">
                        <el-descriptions-item
                          label = "Protein Name"
                          label-align="left"
                          align="right"
                        >
                          {{ protein_id }}
                        </el-descriptions-item>
                        <el-descriptions-item
                          label = "Protein Length"
                          label-align="left"
                          align="right"
                        >
                          {{ proteinInfo.protein_length }}
                        </el-descriptions-item>
                        <el-descriptions-item
                          label = "Coordinate"
                          label-align="left"
                          align="right"
                        >
                          {{ proteinInfo.coordinate }}
                        </el-descriptions-item>
                        <el-descriptions-item
                          label = "Molecular Weight"
                          label-align="left"
                          align="right"
                        >
                          {{ proteinInfo.molecular_weight }}
                        </el-descriptions-item>
                        <el-descriptions-item
                          label = "Isoelectric Point"
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
                          label = "Instability Index"
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
                    </div>
                  </el-collapse-item>
                  <el-collapse-item title="Protein Sequence" name="2">
                    <el-text>
                      >{{ protein_id }}
                    </el-text>
                    <br>
                    <el-text>
                      {{ proteinInfo.protein_sequence }}
                    </el-text>
                  </el-collapse-item>
                  <el-collapse-item title="Sequence Attention Map" name="3">
                    <div>
                      <el-scrollbar height="400px"><el-image :src="proteinInfo.attn_url"/></el-scrollbar>
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
                  </el-collapse-item>
                  <!-- <el-collapse-item title="Secondary Structure" name="4">
                    <div class="grid-container">
                      <div class="grid-item" v-for="index in proteinInfo.secondary_structure" :key="index.pos" :style="getGridItemStyle(index.ss)">
                        <el-tooltip
                          effect="dark"
                          :content=index.pos.toString()
                          placement="top"
                        >
                          {{index.aa}}
                        </el-tooltip>
                      </div>
                    </div>
                    <br>
                    
                    </div>
                  </el-collapse-item> -->
                </el-collapse>
              </el-dialog>
            </el-col>
          </el-row>
        </div>
        <div v-else>
          <el-row>
            <el-col :span="16" :offset="4">
              <h1>Depolymerase prediction result</h1>
              <el-text size="large">Job id: {{ job_id }}</el-text>
              <el-divider />
              <p>
                <vxe-button status="primary" @click="downloadSequenceP">Download sequences (.fasta)</vxe-button>
                <vxe-button class="ml-3" status="primary" @click="exportDataEventP">Download result table (.csv)</vxe-button>
              </p>
              <vxe-table
                ref="tableRefP"
                empty-text="There were no depolymerases found in the input sequences."
                size = "medium"
                :row-config="{isCurrent: true, isHover: true}"
                :data="tableDataP">
                <vxe-column field="protein_id" title="Protein id"></vxe-column>
                <vxe-column field="prediction_score" title="Prediction score"></vxe-column>
                <vxe-column field="length" title="Length (a.a.)"></vxe-column>
                <vxe-column title="Detail">
                  <template #default="{ row }">
                    <vxe-button status="primary" @click="showDetailP(row)">Detail</vxe-button>
                  </template>
                </vxe-column>
              </vxe-table>
              <el-dialog v-model="DetailVisibleP" title="Detail">
                <el-collapse v-model="activeNames">
                  <el-collapse-item title="Basic Information" name="1">
                    <div>
                      <el-descriptions :column="1" border size = "large">
                        <el-descriptions-item
                          label = "Protein Name"
                          label-align="left"
                          align="right"
                        >
                          {{ protein_id }}
                        </el-descriptions-item>
                        <el-descriptions-item
                          label = "Protein Length"
                          label-align="left"
                          align="right"
                        >
                          {{ proteinInfo.protein_length }}
                        </el-descriptions-item>
                        <el-descriptions-item
                          label = "Molecular Weight"
                          label-align="left"
                          align="right"
                        >
                          {{ proteinInfo.molecular_weight }}
                        </el-descriptions-item>
                        <el-descriptions-item
                          label = "Isoelectric Point"
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
                          label = "Instability Index"
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
                    </div>
                  </el-collapse-item>
                  <el-collapse-item title="Protein Sequence" name="2">
                    <el-text>
                      >{{ protein_id }}
                    </el-text>
                    <br>
                    <el-text>
                      {{ proteinInfo.protein_sequence }}
                    </el-text>
                  </el-collapse-item>
                  <el-collapse-item title="Sequence Attention Map" name="3">
                    <div>
                      <el-scrollbar height="400px"><el-image :src="proteinInfo.attn_url"/></el-scrollbar>
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
                  </el-collapse-item>
                </el-collapse>
              </el-dialog>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { reactive, onMounted, onUnmounted, ref } from 'vue';
import { VxeTableInstance, VxeButtonEvents } from 'vxe-table';

interface RowVOP {
  protein_id: string
  prediction_score: number
  length: number
}

interface RowVO {
  contig_id: string
  locus_tag: string
  location: string
  prediction_score: number
  length: number
}

const tableDataP = ref<RowVOP[]>([])
const tableRefP = ref<VxeTableInstance<RowVOP>>()
const DetailVisibleP = ref(false);

const tableData = ref<RowVO[]>([])
const tableRef = ref<VxeTableInstance<RowVO>>()
const DetailVisible = ref(false);
const protein_id = ref('');

const activeNames = ref(['1']);
let intervalId: ReturnType<typeof setInterval>;

const props = defineProps({
  job_id: String,
});

const ifJobRunning = ref(true);
const jobType = ref(true);

const router = useRouter();

const jobInfo = reactive({
  task_type: '',
  num_seqs: '',
  submit_time: '',
  current_time: '',
  email: '',
  status: '',
});

const proteinInfo = reactive({
  protein_length: '',
  coordinate: '',
  molecular_weight: '',
  isoelectric_point: '',
  aromaticity: '',
  instability_index: '',
  flexibility: '',
  protein_sequence: '',
  attn_url: '',
  // secondary_structure: [{aa: '', ss: '', pos: ''}],
});

const popAlert = (message: string) => {
  alert(message);
  router.push({ path: '/analysis' });
};

const exportDataEventP: VxeButtonEvents.Click = () => {
  const $table = tableRefP.value
  if ($table) {
    $table.exportData({ filename: 'result', type: 'csv' })
  }
}

const exportDataEvent: VxeButtonEvents.Click = () => {
  const $table = tableRef.value
  if ($table) {
    $table.exportData({ filename: 'result', type: 'csv' })
  }
}

const getJobInfo = async () => {
  const path = `http://127.0.0.1:5001/api/result/${props.job_id}`;
  axios.get(path)
    .then((res) => {
      // if status is 404, pop a message box and redirect to the analysis page
      if (res.data.status === 404) {
        popAlert(res.data.message);
      }
      else {
        console.log(res.data);
        jobInfo.task_type = res.data.data.task;
        jobInfo.num_seqs = res.data.data.num_sequence;
        jobInfo.submit_time = res.data.data.submit_time;
        jobInfo.current_time = res.data.data.current_time;
        jobInfo.email = res.data.data.email;
        jobInfo.status = res.data.data.status;
        if (jobInfo.task_type === 'genome-level depolymerase prediction') {
          jobType.value = true;
        }
        else {
          jobType.value = false;
        }

        if (res.data.data.status === 'Finished') {
          ifJobRunning.value = false;
          if (jobType.value) {
            tableData.value = res.data.data.rows
          }
          else {
            tableDataP.value = res.data.data.rows
          }
          clearInterval(intervalId);
        }
      }
    })
    .catch((error) => {
      console.error(error);
    });
};

const downloadSequenceP = () => {
  const path = `http://127.0.0.1:5001/api/download/${props.job_id}/outputs/sequence_Dpos.fasta`;
  axios.get(path)
    .then((res) => {
      console.log(res.data);
      const blob = new Blob([res.data], { type: 'text/plain' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = 'sequence_Dpos.fasta';
      link.click();
    })
    .catch((error) => {
      console.error(error);
    });
};

const downloadSequence = () => {
  const path = `http://127.0.0.1:5001/api/download/${props.job_id}/outputs/sequence_screened_Dpos.fasta`;
  axios.get(path)
    .then((res) => {
      console.log(res.data);
      const blob = new Blob([res.data], { type: 'text/plain' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = 'sequence_screened_Dpos.fasta';
      link.click();
    })
    .catch((error) => {
      console.error(error);
    });
};

const showDetailP = (row: RowVOP) => {
  protein_id.value = row.protein_id
  const path = `http://127.0.0.1:5001/api/result/${props.job_id}/${protein_id.value}`;
  axios.get(path)
    .then((res) => {
      console.log(res.data);
      proteinInfo.protein_length = res.data.data.rows[0].length;
      proteinInfo.molecular_weight = res.data.data.rows[0].molecular_weight;
      proteinInfo.isoelectric_point = res.data.data.rows[0].isoelectric_point;
      proteinInfo.aromaticity = res.data.data.rows[0].aromaticity;
      proteinInfo.instability_index = res.data.data.rows[0].instability_index;
      proteinInfo.flexibility = res.data.data.rows[0].flexibility;
      proteinInfo.protein_sequence = res.data.data.rows[0].protein_sequence;
      DetailVisibleP.value = true;
    })
    .catch((error) => {
      console.error(error);
    });
  const attn_path = `http://127.0.0.1:5001/api/result/${props.job_id}/${protein_id.value}/attn`;
  axios.get(attn_path, { responseType: 'arraybuffer'})
    .then((res) => {
      console.log(res.data);
      const blob = new Blob([res.data], { type: 'image/png' });
      proteinInfo.attn_url = window.URL.createObjectURL(blob);
    })
    .catch((error) => {
      console.error(error);
    });
    // const ss_path = `http://127.0.0.1:5001/api/result/${props.job_id}/${protein_id.value}/ss`;
    // axios.get(ss_path)
    //   .then(res => {
    //     proteinInfo.secondary_structure = res.data.data;
    //   })
    //   .catch(error => {
    //     console.error(error);
    //   });
};

const showDetail = (row: RowVO) => {
  protein_id.value = `${row.contig_id}_${row.locus_tag}`
  const path = `http://127.0.0.1:5001/api/result/${props.job_id}/${protein_id.value}`;
  axios.get(path)
    .then((res) => {
      console.log(res.data);
      proteinInfo.protein_length = res.data.data.rows[0].length;
      proteinInfo.coordinate = res.data.data.rows[0].coordinate;
      proteinInfo.molecular_weight = res.data.data.rows[0].molecular_weight;
      proteinInfo.isoelectric_point = res.data.data.rows[0].isoelectric_point;
      proteinInfo.aromaticity = res.data.data.rows[0].aromaticity;
      proteinInfo.instability_index = res.data.data.rows[0].instability_index;
      proteinInfo.flexibility = res.data.data.rows[0].flexibility;
      proteinInfo.protein_sequence = res.data.data.rows[0].protein_sequence;
      DetailVisible.value = true;
    })
    .catch((error) => {
      console.error(error);
    });
  const attn_path = `http://127.0.0.1:5001/api/result/${props.job_id}/${protein_id.value}/attn`;
  axios.get(attn_path, { responseType: 'arraybuffer'})
    .then((res) => {
      console.log(res.data);
      const blob = new Blob([res.data], { type: 'image/png' });
      proteinInfo.attn_url = window.URL.createObjectURL(blob);
    })
    .catch((error) => {
      console.error(error);
    });
  // const ss_path = `http://127.0.0.1:5001/api/result/${props.job_id}/${protein_id.value}/ss`;
  // axios.get(ss_path)
  //   .then(res => {
  //     proteinInfo.secondary_structure = res.data.data;
  //   })
  //   .catch(error => {
  //     console.error(error);
  //   });
};

// const getGridItemStyle = (ss: string) => {
//   if (ss === 'H') {
//     return 'background: var(--ep-color-primary-light-5);';
//   }
//   else if (ss === 'E') {
//     return 'background: var(--ep-color-warning-light-5);';
//   }
//   else if (ss === 'C') {
//     return 'background: #c8c9cc;';
//   }
// };

onMounted(async () => {
  await getJobInfo();
  intervalId = setInterval(getJobInfo, 10000);
});

onUnmounted(() => {
  clearInterval(intervalId);
});
</script>

<style scoped>
:deep(.ep-descriptions__title) {
  font-size: 24px!important;
}
:deep(.ep-descriptions__cell) {
  font-size: 20px!important;
}
:deep(.ep-descriptions__label) {
  font-size: 20px!important;
  font-weight: bold!important;
}
:deep(.job-id-label) {
  background: var(--ep-color-success-light-9) !important;
}
:deep(.ep-dialog__title){
  font-size: 24px!important;
}
:deep(.ep-collapse-item__header){
  font-size: 20px!important;
  font-weight: bold!important;
}
:deep(.grid-container) {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(20px, 1fr));
  grid-gap: 1px;
  text-align: center;
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
