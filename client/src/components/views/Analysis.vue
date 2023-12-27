<template>
    <div class="analysis">
      <el-main>
        <h2>Start phage-encoded depolymerase prediction using DposFinder</h2>
        <el-row>
          <el-col :span="12" :offset="6">
            <el-card class="box-card">
              <div slot="header" class="clearfix">
                <el-radio-group v-model="inputType" @change="handleChange">
                  <el-radio-button label="protein">Input Protein</el-radio-button>
                  <el-radio-button label="genome">Input Genome</el-radio-button>
                </el-radio-group>
              </div>
              <div v-if="inputType === 'protein'">
                <el-input placeholder="Please input protein"></el-input>
              </div>
              <div v-else>
                <el-input placeholder="Please input genome"></el-input>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </div>
</template>

<script lang="ts">
import axios from 'axios';

export default {
  data() {
    return {
      inputType: 'protein',
    };
  },
  methods: {
    handleChange(value: any) {
      console.log('Input type: ' + value);
    },
  },
};
</script>

<style scoped>
.box-card {
  margin: 20px;
}
</style>