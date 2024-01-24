import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import i18n from "./language";
import VXETable from "vxe-table";
import "vxe-table/lib/style.css";
// import "~/styles/element/index.scss";

// import ElementPlus from "element-plus";
// import all element css, uncommented next line
// import "element-plus/dist/index.css";

// or use cdn, uncomment cdn link in `index.html`

import "~/styles/index.scss";
import "uno.css";

// If you want to use ElMessage, import it.
import "element-plus/theme-chalk/src/message.scss";

const app = createApp(App);
app.use(router);
app.use(i18n);

const { t } = i18n.global;
VXETable.config({
i18n: (key, args) => t(key, args)
});
app.use(VXETable);
// app.use(ElementPlus);
app.mount("#app");
