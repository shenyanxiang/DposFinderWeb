<template>
    <div class="analysis">
        <el-main>
          <el-row>
            <el-col :span="12" :offset="6">
                <h2 class = "ml-5">Start phage-encoded depolymerase prediction using DposFinder</h2>
                <el-card class="box-card">
                <div slot="header" class="clearfix">
                    <el-radio-group v-model="inputType" @change="handleInputMethodChange">
                    <el-radio-button label="protein">Input protein</el-radio-button>
                    <el-radio-button label="genome">Input genome</el-radio-button>
                    </el-radio-group>
                <br><br>
                </div>
                <div>
                  <el-form :model="inputForm" label-position="top">
                    <el-form-item label="Choose input method">
                        <el-radio-group v-model="inputMethod">
                          <el-radio label="text">Input sequence</el-radio>
                          <el-radio v-if="inputType === 'protein'" label="file">Upload a fasta file</el-radio>
                          <el-radio v-else-if="inputType === 'genome'" label="file">Upload a fasta or genbank file</el-radio>
                        </el-radio-group>
                    </el-form-item>
                    <el-form-item :label="`Input ${inputType} sequence(s)`" v-if="inputMethod === 'text'">
                        <el-input v-model="inputForm.inputText" :autosize="{ minRows: 4, maxRows: 8 }" type="textarea" :placeholder="`>${inputType} sequence 1\n...\n>${inputType} sequence 2\n...`" clearable/>
                        <el-button type="info" style="margin-top: 10px;" @click="showExample">Show example</el-button>
                    </el-form-item>
                    <el-form-item :label="inputType === 'genome' ? 'Upload a genome FASTA or GenBank format file' : 'Upload a protein FASTA format file'" v-if="inputMethod === 'file'">
                        <el-upload
                        ref="upload"
                        :limit="1"
                        :on-exceed="handleExceed"
                        :auto-upload="false"
                        :on-change="handleFileChange"
                        style="margin-top:10px;"
                        >
                        <template #trigger>
                          <el-button slot="trigger" type="primary">Select file</el-button>
                        </template>
                        <el-button type="info" class="ml-3" @click="showFileExample">Show example</el-button>
                        </el-upload>
                    </el-form-item>
                    <el-form-item>
                        <el-row> <el-text>Plot sequence attention</el-text>&nbsp;&nbsp;&nbsp;&nbsp;<el-switch v-model="inputForm.plotAttn" /> </el-row>
                    </el-form-item>
                    <el-form-item>
                        <el-row> <el-text>Predict capsular serotype</el-text>&nbsp;&nbsp;&nbsp;&nbsp;<el-switch v-model="inputForm.predSerotype" /> </el-row>
                    </el-form-item>
                    <el-form-item v-if="inputForm.predSerotype" >
                      <el-col :span="11">
                        <el-text>—— return top k possible serotype(s)</el-text> 
                      </el-col>
                      <el-col :span="6">
                        <el-select-v2 v-model="inputForm.topK" :options="options"/>
                      </el-col>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="onSubmit">Run</el-button>
                        <el-button @click="onClear">Clear</el-button>
                    </el-form-item>
                  </el-form>
                </div>
                </el-card>
            </el-col>
          </el-row>
          <el-row>
          <el-col :span="12" :offset="6">
            <h2 class="ml-5">Retrieve Results</h2>
            <h4 class="ml-5">You can input the job id to retrieve the results or monitor the progress of the job</h4>
            <el-card class="box-card">
              <el-form label-position="top">
                <el-form-item label="Please input job id">
                  <el-input placeholder="job id" v-model="job_id" clearable/>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="JobRetrieve">Retrieve</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>
        </el-row>
        </el-main>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';
import { genFileId,ElMessage } from 'element-plus';
import type { UploadInstance, UploadProps, UploadRawFile, UploadFile } from 'element-plus';
import { v4 as uuidv4 } from 'uuid';
import { useRouter } from 'vue-router';

const router = useRouter();

const inputForm = reactive<any>({
  inputText: '',
  file: {},
  job_id: '',
  predSerotype: false,
  plotAttn: false,
  topK: 1,
});

const inputType = ref('protein');
const upload = ref<UploadInstance>();
const inputMethod = ref('text');
const predSerotype = ref(false);
const topK = ref(1);
const options = [
  { value: '1', label: '1' },
  { value: '2', label: '2' },
  { value: '3', label: '3' },
  { value: '4', label: '4' },
  { value: '5', label: '5' }
];

const showExample = async () => {
  try {
    let path;
    if (inputType.value === 'protein') {
      path = './protein_example.fasta';
    } else {
      path = './genome_example.fasta';
    }
    const response = await fetch(path);
    if (!response.ok) {
      throw new Error('HTTP error ' + response.status);
    }
    const text = await response.text();
    inputForm.inputText = text;
  } catch (error) {
    console.error('Failed to fetch protein example:', error);
  }
};

const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles();
  const file = files[0] as UploadRawFile;
  file.uid = genFileId();
  upload.value!.handleStart(file);
};

const handleFileChange = (uploadFile: UploadFile) => {
  inputForm.file.value = uploadFile;
  console.log('File:', inputForm.file.value.raw);
};

const handleInputMethodChange = (val: any) => {
  inputType.value = val;
}

const showFileExample = () => {
  const link = document.createElement('a');
  if (inputType.value === 'protein') {
    link.href = '/protein_example.fasta';
    link.download = 'protein_example.fasta';
  } else {
    link.href = '/genome_example.fasta';
    link.download = 'genome_example.fasta';
  }

  link.click();
};

const onClear = () => {
  inputForm.inputText = '';
  inputForm.file = {};
  inputMethod.value = 'text';
  inputType.value = 'protein';
  predSerotype.value = false;
};

const onSubmit = () => {
  inputForm.job_id = uuidv4();
  const formData = new FormData();
  const postUrl = `http://127.0.0.1:5001/api/analysis/${inputType.value}`
  formData.append('inputMethod', inputMethod.value);
  formData.append('job_id', inputForm.job_id);
  formData.append('plotAttn', inputForm.plotAttn);
  formData.append('predSerotype', inputForm.predSerotype);
  formData.append('topK', inputForm.topK);
  if (inputMethod.value === 'file') {
    if (inputForm.file.value.raw) {
      formData.append('file', inputForm.file.value.raw);
    } else {
      console.error('No file selected');
    }
    axios.post(postUrl, formData)
      .then((response) => {
        if (response.data.status === 404) {
          ElMessage.error(response.data.message);
        }
        else {
          router.push({ path: `/result/${inputForm.job_id}` });
      }
      });
  } else {
    formData.append(`input${inputType.value}`, inputForm.inputText);
    axios.post(postUrl, formData)
    .then((response) => {
      if (response.data.status === 404) {
        ElMessage.error(response.data.message);
      }
      else {
        router.push({ path: `/result/${inputForm.job_id}` });
      }
    }, (error) => {
      console.log(error);
    });
  }
};

const job_id = ref('');

const JobRetrieve = () => {
  console.log(job_id);
  router.push({ path: `/result/${job_id.value}` });
};
</script>

<style scoped>
.box-card {
  margin: 20px;
}
</style>