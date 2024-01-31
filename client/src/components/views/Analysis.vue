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
              <div v-if="inputType === 'protein'">
                <el-form :model="proteinForm" label-position="top">
                  <el-form-item label="Choose input method">
                    <el-radio-group v-model="inputMethod">
                      <el-radio label="text">Input sequence</el-radio>
                      <el-radio label="file">Upload a fasta file</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item label="Input protein sequence(s)" v-if="inputMethod === 'text'">
                    <el-input v-model="proteinForm.inputProtein" :autosize="{ minRows: 4, maxRows: 8 }" type="textarea" placeholder=">protein sequence 1 ..." clearable/>
                    <el-button type="info" style="margin-top: 10px;" @click="showProteinExample">Show example</el-button>
                  </el-form-item>
                  <el-form-item label="Upload a protein FASTA format file" v-else>
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
                      <el-button type="info" class="ml-3" @click="showProteinFileExample">Show example</el-button>
                    </el-upload>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="onSubmit">Run</el-button>
                    <el-button @click="onClear">Clear</el-button>
                  </el-form-item>
                </el-form>
              </div>
              <div v-else>
                <el-form :model="genomeForm" label-position="top">
                  <el-form-item label="Choose input method">
                    <el-radio-group v-model="inputMethodGenome">
                      <el-radio label="text">Input sequence</el-radio>
                      <el-radio label="file">Upload a fasta or genbank file</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item label="Input genome sequence(s)" v-if="inputMethodGenome === 'text'">
                    <el-input v-model="genomeForm.inputGenome" :autosize="{ minRows: 4, maxRows: 8 }" type="textarea" placeholder=">genome sequence..." clearable/>
                    <el-button type="info" style="margin-top: 10px;" @click="showGenomeExample">Show example</el-button>
                  </el-form-item>
                  <el-form-item label="Upload a genome FASTA or GenBank format file" v-else>
                    <el-upload
                      ref="uploadGenome"
                      :limit="1"
                      :on-exceed="handleExceedGenome"
                      :auto-upload="false"
                      :on-change="handleFileChangeGenome"
                      style="margin-top:10px;"
                    >
                      <template #trigger>
                        <el-button slot="trigger" type="primary">Select file</el-button>
                      </template>
                      <el-button type="info" class="ml-3" @click="showGenomeFileExample">Show example</el-button>
                    </el-upload>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="onSubmitGenome">Run</el-button>
                    <el-button @click="onClearGenome">Clear</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-row><h1>{{ msg }}</h1></el-row>
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

const proteinForm = reactive<any>({
  inputProtein: '',
  file: {},
  job_id: '',
});

const genomeForm = reactive<any>({
  inputGenome: '',
  file:{},
  job_id: '',
});
const inputType = ref('protein');
const upload = ref<UploadInstance>();
const uploadGenome = ref<UploadInstance>();
const inputMethod = ref('text');
const inputMethodGenome = ref('text');
const showProteinExample = async () => {
  try {
    const response = await fetch('./protein_example.fasta');
    if (!response.ok) {
      throw new Error('HTTP error ' + response.status);
    }
    const text = await response.text();
    proteinForm.inputProtein = text;
  } catch (error) {
    console.error('Failed to fetch protein example:', error);
  }
};
const showGenomeExample = async () => {
  try {
    const response = await fetch('./genome_example.fasta');
    if (!response.ok) {
      throw new Error('HTTP error ' + response.status);
    }
    const text = await response.text();
    genomeForm.inputGenome = text;
  } catch (error) {
    console.error('Failed to fetch genome example:', error);
  }
};
const msg = ref('');

const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles();
  const file = files[0] as UploadRawFile;
  file.uid = genFileId();
  upload.value!.handleStart(file);
};

const handleExceedGenome: UploadProps['onExceed'] = (files) => {
  uploadGenome.value!.clearFiles();
  const file = files[0] as UploadRawFile;
  file.uid = genFileId();
  uploadGenome.value!.handleStart(file);
};

const handleFileChange = (uploadFile: UploadFile) => {
  proteinForm.file.value = uploadFile;
  console.log('File:', proteinForm.file.value.raw);
};

const handleFileChangeGenome = (uploadFile: UploadFile) => {
  genomeForm.file.value = uploadFile;
  console.log('File:', genomeForm.file.value.raw);
};

const handleInputMethodChange = (val: any) => {
  inputType.value = val;
}

const showProteinFileExample = () => {
  const link = document.createElement('a');
  link.href = '/protein_example.fasta';
  link.download = 'protein_example.fasta';

  link.click();
};

const showGenomeFileExample = () => {
  const link = document.createElement('a');
  link.href = '/genome_example.fasta';
  link.download = 'genome_example.fasta';

  link.click();
};

const onClear = () => {
  proteinForm.inputProtein = '';
  proteinForm.file = {};
  inputMethod.value = 'text';
};

const onClearGenome = () => {
  genomeForm.inputGenome = '';
  genomeForm.file = {};
  inputMethodGenome.value = 'text';
};

const onSubmit = () => {
  proteinForm.job_id = uuidv4();
  if (inputMethod.value === 'file') {
    const formData = new FormData();
    if (proteinForm.file.value.raw) {
      formData.append('file', proteinForm.file.value.raw);
    } else {
      console.error('No file selected');
    }
    formData.append('inputMethod', inputMethod.value);
    formData.append('job_id', proteinForm.job_id);
    console.log(formData);
    axios.post('http://127.0.0.1:5001/api/analysis/protein', formData)
      .then((response) => {
        if (response.data.status === 404) {
          ElMessage.error(response.data.message);
        }
        else {
          router.push({ path: `/result/${genomeForm.job_id}` });
      }
      });
  } else {
    console.log(proteinForm.job_id);
    const formData = new FormData();
    formData.append('inputProtein', proteinForm.inputProtein);
    formData.append('inputMethod', inputMethod.value);
    formData.append('job_id', proteinForm.job_id);
    axios.post('http://127.0.0.1:5001/api/analysis/protein', formData)
    .then((response) => {
      if (response.data.status === 404) {
        ElMessage.error(response.data.message);
      }
      else {
        router.push({ path: `/result/${proteinForm.job_id}` });
      }
    }, (error) => {
      console.log(error);
    });
  }
};

const onSubmitGenome = () => {
  genomeForm.job_id = uuidv4();
  if (inputMethodGenome.value === 'file') {
    const formData = new FormData();
    if (genomeForm.file.value.raw) {
      formData.append('file', genomeForm.file.value.raw);
    } else {
      console.error('No file selected');
    }
    formData.append('inputMethod', inputMethodGenome.value);
    formData.append('job_id', genomeForm.job_id);
    axios.post('http://127.0.0.1:5001/api/analysis/genome', formData)
      .then((response) => {
        if (response.data.status === 404) {
          ElMessage.error(response.data.message);
        }
        else {
          router.push({ path: `/result/${genomeForm.job_id}` });
      }
      });
  } else {
    console.log(genomeForm.inputGenome);
    const formData = new FormData();
    formData.append('inputGenome', genomeForm.inputGenome);
    formData.append('inputMethod', inputMethodGenome.value);
    formData.append('job_id', genomeForm.job_id);
    axios.post('http://127.0.0.1:5001/api/analysis/genome', formData)
    .then((response) => {
      if (response.data.status === 404) {
        ElMessage.error(response.data.message);
      }
      else {
        router.push({ path: `/result/${genomeForm.job_id}` });
      }
    }, (error) => {
      console.log(error);
    });
  }
};

</script>

<style scoped>
.box-card {
  margin: 20px;
}
</style>