<template>
    <div class="analysis">
      <el-main>
        <h2>Start phage-encoded depolymerase prediction using DposFinder</h2>
        <el-row>
          <el-col :span="12" :offset="6">
            <el-card class="box-card">
              <div slot="header" class="clearfix">
                <el-radio-group v-model="inputType" @change="handleInputChange">
                  <el-radio-button label="protein">Input Protein</el-radio-button>
                  <el-radio-button label="genome">Input Genome</el-radio-button>
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
                  </el-form-item>
                  <el-form-item label="Upload a protein FASTA format file" v-else>
                    <el-upload
                      ref="upload"
                      :limit="1"
                      :on-exceed="handleExceed"
                      :auto-upload="false"
                      :on-change="handleFileChange"
                    >
                      <template #trigger>
                        <el-button slot="trigger" type="primary">select file</el-button>
                      </template>
                    </el-upload>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="onSubmit">Run</el-button>
                    <el-button>Clear</el-button>
                  </el-form-item>
                </el-form>
              </div>
              <div v-else>
                <el-input placeholder="Please input genome"/>
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
import { genFileId } from 'element-plus';
import type { UploadInstance, UploadProps, UploadRawFile, UploadFile } from 'element-plus';

const proteinForm = reactive<any>({
  inputProtein: '',
  file: {},
});

const upload = ref<UploadInstance>();
const inputType = ref('protein');
const inputMethod = ref('text');
const msg = ref('');

const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles();
  const file = files[0] as UploadRawFile;
  file.uid = genFileId();
  upload.value!.handleStart(file);
};

const handleFileChange = (uploadFile: UploadFile) => {
  proteinForm.file.value = uploadFile;
  console.log('File:', proteinForm.file.value.raw);
};

const handleInputChange = (val: any) => {
  inputType.value = val;
}

const getResources = () => {
  const path = 'http://127.0.0.1:5001/api/analysis';
  axios.get(path)
    .then((res) => {
      msg.value = res.data.sequence;
    })
    .catch((error) => {
      console.error(error);
    });
};

const onSubmit = () => {
  if (inputMethod.value === 'file') {
    const formData = new FormData();
    if (proteinForm.file.value.raw) {
      formData.append('file', proteinForm.file.value.raw);
    } else {
      console.error('No file selected');
    }
    formData.append('inputMethod', inputMethod.value);
    console.log(formData);
    axios.post('http://127.0.0.1:5001/api/analysis', formData)
      .then((response) => {
        console.log(response);
        getResources();
      }, (error) => {
        console.log(error);
      });
  } else {
    console.log(proteinForm.inputProtein);
    axios.post('http://127.0.0.1:5001/api/analysis', {
      inputProtein: proteinForm.inputProtein,
      inputMethod: inputMethod.value,
    })
    .then((response) => {
      console.log(response);
      getResources();
    }, (error) => {
      console.log(error);
    });
  }
};

onMounted(getResources);
</script>

<style scoped>
.box-card {
  margin: 20px;
}
</style>