<template>
  <div class = "result">
    <el-main>
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
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { reactive, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  job_id: String,
});

const router = useRouter();

const jobInfo = reactive({
  task_type: '',
  num_seqs: '',
  submit_time: '',
  current_time: '',
  email: '',
  status: '',
});

const popAlert = (message: string) => {
  alert(message);
  router.push({ path: '/analysis' });
};

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

        if (res.data.status === 'finished') {
          router.push({ path: `/result/${props.job_id}` });
        }
      }
    })
    .catch((error) => {
      console.error(error);
    });
};

let intervalId: ReturnType<typeof setInterval>;

onMounted(async () => {
  // 首次调用
  await getJobInfo();

  // 每隔 10 秒调用一次
  intervalId = setInterval(getJobInfo, 10000);
});

onUnmounted(() => {
  // 当组件卸载时，清除定时器
  clearInterval(intervalId);
});
</script>

<style scoped>
:deep(.ep-descriptions__title){
  font-size: 24px!important;
}
:deep(.ep-descriptions__cell){
  font-size: 20px!important;
}
:deep(.ep-descriptions__label){
  font-size: 20px!important;
  font-weight: bold!important;
}
:deep(.job-id-label) {
  background: var(--ep-color-success-light-9) !important;
}
</style>
