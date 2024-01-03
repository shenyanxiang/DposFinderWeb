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
    </div>
</template>

