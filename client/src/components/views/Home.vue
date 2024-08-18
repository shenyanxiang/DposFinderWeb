<!-- /src/components/views/Home.vue -->
<template>
    <div>
        <div class="header">
        <h1>DposFinderWeb: an platform integrates Depolymerase database and Depolymerase prediction</h1>
        </div>

        <div class="container">
        <div class="content">
            <p style="text-indent: 2em;">
            DposFinderWeb has collected the reported depolymerases from literatures since 2024. Leveraging the power of 
            DposFinder model, DeepSecEdb has covered 107,428 putative depolymerases derived from various phage genomes. 
            DposFinderWeb also provides the function to predict the potential depolymerases from user-provided protein sequences 
            or genome sequences. For those depolymerases encoded by <em>Klebsiella</em> phages, DposFinder can further predict their
            specific serotypes. 
            </p>
            <!-- <div class="reference">
            </div> -->
        </div>

        <div class="buttons">
            <el-button type="primary" @click="navigatetoHelp">Learn More<el-icon class="el-icon--right"><DArrowRight /></el-icon></el-button>
        </div>

        <div class="cards">
            <div class="card">
            <img src="../../assets/database_overview.png" alt="TXSE Database" />
            <h3>Depolymerase database</h3>
            <p>Browse the curated depolymerases and predicted depolymerases.</p>
            <div class="buttons">
                <el-button type="primary" @click="navigatetoBrowse">Get Started<el-icon class="el-icon--right"><DArrowRight /></el-icon></el-button>
            </div>
            </div>
            <div class="card">
            <img src="../../assets/prediction_overview.png" alt="Secreted Protein Prediction" />
            <h3>Secreted Protein Prediction</h3>
            <p>Perform DposFinder to identify depolymerases.</p>
            <div class="buttons">
              <el-button type="primary" @click="navigateToAnalysis">Get Started<el-icon class="el-icon--right"><DArrowRight /></el-icon></el-button>
            </div>
            </div>
        </div>
        </div>
    </div>
</template>
  
<script lang="ts" setup>
  import {
  DArrowRight,
  } from '@element-plus/icons-vue'
  import { useRouter } from 'vue-router';

  const router = useRouter();

  const navigateToAnalysis = () => {
    router.push({ path: `/analysis` });
  };
  const navigatetoBrowse = () => {
    router.push({ path: `/browsemain` });
  };
  const navigatetoHelp = () => {
    router.push({ path: `/help` });
  };

</script>
  
<style scoped>
  body {
    font-family: Arial, sans-serif;
    background-color: #f5f5f5;
    margin: 0;
    padding: 0;
  }
  .header {
    padding: 40px 0;
    background-color: #f0f2f5;
    text-align: center;
  }
  .header h1 {
    font-size: 2rem;
    color: #333;
    margin-bottom: 20px;
  }
  .search-bar {
    margin: 20px 0;
  }
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    text-align: center;
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  }
  .content {
    padding: 20px;
    text-align: left;
    color: #333;
  }
  .reference {
    margin: 20px 0;
    font-size: 0.9rem;
    color: #666;
  }
  .buttons {
    display: flex;
    justify-content: flex-end;
    margin: 10px 20px;
  }
  .buttons .el-button {
    min-width: 100px;
  }
  .cards {
    display: flex;
    justify-content: space-around;
    margin-top: 40px;
  }
  .card {
    background-color: #f0f2f5;
    border-radius: 10px;
    padding: 20px;
    text-align: left;
    width: 45%;
  }
  .card img {
    width: 100%;
    border-radius: 10px;
    margin-bottom: 15px;
  }
  .card h3 {
    font-size: 1.2rem;
    margin-bottom: 10px;
  }
  .card p {
    margin-bottom: 20px;
    color: #666;
  }
</style>
  