// Stablish the socket to localhost:8000
const socket = io('http://localhost:8000');
const {createApp, ref, provide, watch} = Vue;
        
// Create the equipmentList as an empty Array
let equipmentList = ref([]);

// Initialize the VueJS App component
const app = createApp({
    setup(){
        const rows  = ref(equipmentList);
                
        // Sends the equipmenList to the app component
        provide('equipmentList', equipmentList);
                
        // Watches the equipmentList for changes (updates, etc)
        watch(equipmentList, (newValue) => {
            rows.value = newValue;
        });

        return { rows }
    }
});
        
// Print in console the errors
app.config.errorHandler = (err) => {console.error(err)};
        
// Mount the app into the div id#app
app.mount('#app');
        
// Update on new data
socket.on('update', (data) => {
    equipmentList.value = data;
});