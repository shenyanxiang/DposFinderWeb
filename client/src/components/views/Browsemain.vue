<template>
  <div class="browsemain">
    <el-row>
      <el-col :span="16" :offset="4">
        <h1 class = "mt-6">Browse well-characterized depolymerases</h1>
        <p>we</p>
        <el-button type="info" disabled>Browse well-characterized depolymerases</el-button>
        <el-button type="info" @click="Browsepre">Browse predicted depolymerases by DposFinder</el-button>
        <br><br><br>
        <vxe-grid ref="xGrid" v-bind="gridOptions">
            <template #toolbar_tools>
                <vxe-form :data="formData" @submit="searchEvent" @reset="resetEvent">
                  <vxe-form-item field="name">
                        <template #default>
                            <vxe-input v-model="formData.name" type="text" placeholder="Please Input accession"></vxe-input>
                        </template>
                    </vxe-form-item>
                    <vxe-form-item>
                        <template #default>
                            <vxe-button type="submit" status="primary" content="Search"></vxe-button>
                            <vxe-button type="reset" content="Reset"></vxe-button>
                        </template>
                  </vxe-form-item>
                </vxe-form>
            </template>
        </vxe-grid>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router';
import { reactive, ref } from 'vue'
import { VxeGridInstance, VxeGridProps } from 'vxe-table'
import XEUtils from 'xe-utils'

const router = useRouter();

const Browsepre = () => {
  router.push('/browsepre');
};

interface RowVO {
  [key: string]: any
}

const serveApiUrl = 'http://127.0.0.1:5001'
const xGrid = ref<VxeGridInstance<RowVO>>()
const formData = reactive({
  name: ''
})

const gridOptions = reactive<VxeGridProps<RowVO>>({
  showOverflow: true,
  border: 'inner',
  height: 548,
  rowConfig: {
    keyField: 'Protein accession'
  },
  columnConfig: {
    resizable: true
  },
  printConfig: {
    columns: [
      { field: 'dpos_accession' },
      { field: 'phage' },
      { field: 'experimental' },
      { field: 'reference' },
    ]
  },
  sortConfig: {
    trigger: 'cell',
    remote: true,
    defaultSort: {
      field: 'experimental',
      order: 'desc'
    }
  },
  filterConfig: {
    remote: true
  },
  pagerConfig: {
    enabled: true,
    // currentPage: 1,
    pageSize: 15,
    pageSizes: [5, 15, 20, 50, 100, 200]
  },
  exportConfig: {
    // 默认选中类型
    type: 'csv',
    // 局部自定义类型
    types: ['csv', 'html', 'xml', 'txt'],
    // 自定义数据量列表
    modes: ['current', 'all']
  },
  proxyConfig: {
    sort: true, // 启用排序代理，当点击排序时会自动触发 query 行为
    filter: true, // 启用筛选代理，当点击筛选时会自动触发 query 行为
    // 对应响应结果 { result: [], page: { total: 100 } }
    props: {
      result: 'result', // 配置响应结果列表字段
      total: 'page.total' // 配置响应结果总页数字段
    },
    ajax: {
      // 接收 Promise 对象
      query: ({ page, sorts, filters }) => {
        const queryParams: any = Object.assign({}, formData)
        // 处理排序条件
        const firstSort = sorts[0]
        if (firstSort) {
          queryParams.sort = firstSort.field
          queryParams.order = firstSort.order
        }
        // 处理筛选条件
        filters.forEach(({ field, values }) => {
          queryParams[field] = values.join(',')
        })
        return fetch(`${serveApiUrl}/api/ex_dpos/page/list/${page.pageSize}/${page.currentPage}?${XEUtils.serialize(queryParams)}`).then(response => response.json())
      },
      // 被某些特殊功能所触发，例如：导出数据 mode=all 时，会触发该方法并对返回的数据进行导出
      queryAll: () => fetch(`${serveApiUrl}/api/ex_dpos/all`).then(response => response.json())
    }
  },
  toolbarConfig: {
    export: true,
    print: true,
    slots: {
    //   buttons: 'toolbar_buttons',
      tools: 'toolbar_tools'
    }
  },
  columns: [
    { type: 'seq', width: 60, fixed: 'left' },
    { field: 'dpos_accession', type: "html", title: 'Depolymerase accession', minWidth: 160, sortable: true},
    { field: 'phage', title: 'Phage name', minWidth: 160, sortable: true },
    { field: 'experimental', title: 'Experiment', sortable: true, minWidth: 160,
        filters: [
            { label: 'yes', value: 'yes'},
            { label: 'no', value: 'no' }
        ],
    },
    { field: 'reference', type: "html", title: 'Reference', sortable: true, minWidth: 160, 
        formatter: ({ cellValue }) => {
            return `<a href="https://doi.org/${cellValue}" target="_blank">doi:${cellValue}</a>`;
        }
    }
  ]
})


const searchEvent = () => {
  const $grid = xGrid.value
  if ($grid) {
    $grid.commitProxy('query')
  }
}

const resetEvent = () => {
  const $grid = xGrid.value
  if ($grid) {
    $grid.commitProxy('reload')
  }
}

</script>