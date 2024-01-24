<script setup lang="ts">
import axios from 'axios';
import { reactive, onMounted, onUnmounted, ref } from 'vue';
import { VxeGridProps, VxePagerEvents, VXETable, VxeGridInstance, VxeGridListeners } from 'vxe-table'

interface RowVO {
  phage_id: string
  Host: string
  locus_tag: string
  coordinate: string
  prediction_score: number
  length: number
  protein_sequence: string
}

const xGrid = ref<VxeGridInstance<RowVO>>()

const gridOptions = reactive<VxeGridProps<RowVO>>({
  border: true,
  loading: false,
  height: 600,
  columns: [
    { type: 'seq', width: 50 },
    { field: 'phage_id', title: 'Phage ID'},
    { field: 'Host', title: 'Host' },
    { field: 'locus_tag', title: 'Locus Tag'},
    { field: 'coordinate', title: 'Coordinates'},
    { field: 'prediction_score', title: 'Prediction Score' },
    { field: 'length', title: 'Length' },
    { title: 'View Details', slots: { default: 'operate' }}
  ],
  columnConfig: {
    resizable: true
  },
  proxyConfig: {
    ajax: {
      query: async () => {
        const list = await getDposInfo();
        return list;
      }
    }
  }
})

const tablePage = reactive({
  total: 7759,
  currentPage: 1,
  pageSize: 10
})

const handlePageChange: VxePagerEvents.PageChange = ({ currentPage, pageSize }) => {
  tablePage.currentPage = currentPage
  tablePage.pageSize = pageSize
}

const getDposInfo = async () => {
  try {
    const path = `http://127.0.0.1:5001/api/show_dpos`;
    const response = await axios.get(path);
    console.log(response.data.data);
    return response.data.data;
  } catch (error) {
    console.log(error);
    return [];
  }
};

const gridEvents: VxeGridListeners<RowVO> = {
  pageChange ({ currentPage, pageSize }) {
    if (gridOptions.pagerConfig) {
      gridOptions.pagerConfig.currentPage = currentPage
      gridOptions.pagerConfig.pageSize = pageSize
    }
  }
}

</script>

<template>
  <div class="browsepre">
    <el-row>
      <el-col :span="16" :offset="4">
        <p>
          <vxe-button status="primary" @click="downloadSequence">Download sequences(.fasta)</vxe-button>
          <vxe-button class="ml-3" status="primary" @click="exportDataEvent">Download result table(.csv)</vxe-button>
        </p>
        <vxe-grid ref="xGrid" v-bind="gridOptions" v-on="gridEvents">
          <template #operate="{ row }">
            <vxe-button status="primary" content="Detail" @click="saveRowEvent(row)"></vxe-button>
          </template>
          <template #pager>
            <vxe-pager
              :layouts="['Sizes', 'PrevJump', 'PrevPage', 'Number', 'NextPage', 'NextJump', 'FullJump', 'Total']"
              v-model:current-page="tablePage.currentPage"
              v-model:page-size="tablePage.pageSize"
              :total="tablePage.total"
              @page-change="handlePageChange">
            </vxe-pager>
          </template>
        </vxe-grid>
      </el-col>
    </el-row>
  </div>
</template>

