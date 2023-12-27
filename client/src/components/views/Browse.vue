<script lang="ts">
import axios from 'axios';

export default {
  data() {
    return {
      resources: [],
    };
  },
  methods: {
    getResources() {
      const path = 'http://127.0.0.1:5001/resources';
      axios.get(path)
        .then((res) => {
          this.resources = res.data.resources;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getResources();
  },
};
</script>

<template>
    <div class="browse">
        <div class="container">
            <div class="row">
            <div class="col-sm-10">
                <h1>在线课程</h1>
                <hr><br><br>
                <button type="button" class="btn btn-info btn-sm">添加课程</button>
                <br><br>
                <table class="table table-hover text-white">
                <thead>
                    <tr>
                    <th scope="col">课程</th>
                    <th scope="col">讲师</th>
                    <th scope="col">已学习</th>
                    <th></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(r, index) in resources" :key="index">
                    <td>{{ r.sn }}</td>
                    <td>{{ r.teacher }}</td>
                    <td>
                        <span v-if="r.learnt">是</span>
                        <span v-else>否</span>
                    </td>
                    <td>
                        <div class="btn-group" role="group">
                        <button type="button" class="btn btn-warning btn-sm">修改</button>
                        <button type="button" class="btn btn-danger btn-sm">删除</button>
                        </div>
                    </td>
                    </tr>
                </tbody>
                </table>
            </div>
            </div>
        </div>
    </div>
</template>

