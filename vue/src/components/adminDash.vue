<script setup>
import { ref, computed} from 'vue'
import {useRoute,  RouterLink} from 'vue-router'
import fetchData from '../helper.js'
import { AuthStore } from '../stores/main.js'
import router from '../router/index.js'
import API_URL from '../constants.js'
import moment from 'moment'
var s = AuthStore()
var dashVars = ref({
    issued: 0,
    req: 0,
    users: 0,
    sections: 0,
    books: 0,
    mxd: 0,
    mxc: 0,
    auto: false
})

var salesData = ref({
    labels: [],
    datasets: [
        {
            data: [],
        },
    ],
})


import { Chart as ChartJS, ArcElement, Tooltip, Legend, Colors,CategoryScale,
  LinearScale,
  PointElement,
  LineElement,} from 'chart.js'


import { Doughnut, Line} from 'vue-chartjs'
var exportDisabled = ref(false)
var showOverlay = ref(false)
var reminderDisabled = ref(false)
var exportsHistory = ref([])
var monthlyDisabled = ref(false)

const month = new Date().toLocaleString('en-us',{month:'short'})
var prevMonth = moment().subtract(1, 'months').format('MMM')

ChartJS.register(ArcElement, Tooltip,Legend,Colors,CategoryScale,
  LinearScale,
  PointElement,
  LineElement,)
const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  
};

const salesOptions = {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
     intersect: false,
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        border: {
            display: false,
        },

      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Sales'
        },
        border: {
            dash: [5, 10],
        },
      }
    }
}

var chartData = ref({
  labels: [],
  datasets: [
    {
      data: [],
    },
  ],
})

async function exportData() {
    exportDisabled.value = true
    var data = await fetchData('/api/export')
}

async function viewExports() {
    var data = await fetchData('/api/export_status')
    exportsHistory.value = data
    showOverlay.value = true
}

async function requestMonthlyReport() {
    monthlyDisabled.value = true
    var data = await fetchData('/api/month_report')
}

async function sendReminder() {
    reminderDisabled.value = true
    var data = await fetchData('/api/send_reminders')
}

fetchData('/api/adminDashboard').then(data => {
    dashVars.value = {...data}
})

fetchData('/api/admin/chart').then(data => {
    console.log(data)
    chartData.value = {
        labels: data["group"],
        datasets: [
            {
                data: data["data"],
                backgroundColor: getColors(data["data"].length)
            },
        ],
    }
})

function parseDates(data) {
    return data.map(x => new Date(x).toLocaleString('en-us',{month:"short", day:"2-digit"}))
}

fetchData("/api/sales_stats").then(data => {
    salesData.value = {
        labels: parseDates(data[0]),
        datasets: [{
            data: data[1], 
            label: "Sales", 
            borderColor: "#35353d",
            borderWidth: 3,
            tension:0.3,
            pointRadius:0
        }],
    }
})
var totalSales = computed(() => salesData.value.datasets[0].data.reduce((a, b) => a + b, 0))
var todayDate = new Date().getDate()
function getColors(length) {
    //let pallet2 = ["#0074D9", "#FF4136", "#2ECC40", "#FF851B", "#7FDBFF", "#B10DC9", "#FFDC00", "#001f3f", "#39CCCC", "#01FF70", "#85144b", "#F012BE", "#3D9970", "#111111", "#AAAAAA"];
    //let pallet = ["#FF4136", "#2ECC40", "#FF851B", "#7FDBFF", "#B10DC9", "#FFDC00", "#001f3f", "#39CCCC", "#01FF70", "#85144b", "#F012BE", "#3D9970", "#111111", "#AAAAAA"];
    let pallet = [
      '#5bc0de',
      '#337ab7',
      '#5cb85c',
      '#6f42c1',
      '#868e96'
    ]
    let colors = [];

    for (let i = 0; i < length; i++) {
        colors.push(pallet[i % (pallet.length - 1)]);
    }

    return colors;
}

async function updatePolicy(form) {
    console.log(form)
    var data = {
        MaxBorrowDays: form.target.elements.MaxBorrowDays.value,
        MaxBorrowBooks: form.target.elements.MaxBorrowBooks.value,
        AutoApprove: form.target.elements.AutoApprove.value
    }
    fetchData('/api/admin/policy?' + new URLSearchParams(data)).then(data => {
        if (data["status"] == "success") {
            fetchData('/api/adminDashboard').then(data => {
                dashVars.value = {...data}
                form.target.elements[3].classList.remove('btn-dark')
                form.target.elements[3].classList.add('btn-success')
                form.target.elements[3].innerText = "Updated"
                setTimeout(() => {
                    form.target.elements[3].classList.remove('btn-success')
                    form.target.elements[3].classList.add('btn-dark')
                    form.target.elements[3].innerText = "Update"
                }, 2000)
            })
        }
    })
}

</script>

<template>
    <div id="body" class="container d-flex justify-content-center flex-wrap mb-3">

        <div class="card" style="width: 18rem; margin: 20px;">

            <div class="card-body">
                <h5 class="card-title">Currently Issued</h5>
                <h1 class="card-text" style="margin-top: 20px;">{{ dashVars.issued }}</h1>
                <RouterLink to="issued_list" class="btn btn-primary stretched-link hide-slink"></RouterLink>
            </div>

        </div>
        <div class="card" style="width: 18rem; margin: 20px;">

            <div class="card-body">
                <h5 class="card-title">Pending Requests</h5>
                <h1 class="card-text" style="margin-top: 20px;">{{ dashVars.req }}</h1>
                <RouterLink to="requests" class="btn btn-primary stretched-link hide-slink"></RouterLink>
            </div>

        </div>

        <div class="card" style="width: 18rem; margin: 20px;">

            <div class="card-body">
                <h5 class="card-title">Total Users</h5>
                <h1 class="card-text" style="margin-top: 20px;">{{ dashVars.users }}</h1>
                <RouterLink to="users_list" class="btn btn-primary stretched-link hide-slink"></RouterLink>
            </div>

        </div>
        <div class="card" style="width: 18rem; margin: 20px;">

            <div class="card-body">
                <h5 class="card-title">Sections</h5>
                <h1 class="card-text" style="margin-top: 20px;">{{ dashVars.sections }}</h1>
                <RouterLink to="sections_list" class="btn btn-primary stretched-link hide-slink"></RouterLink>
            </div>

        </div>
        <div class="card" style="width: 18rem; margin: 20px;">

            <div class="card-body">
                <h5 class="card-title">Books</h5>
                <h1 class="card-text" style="margin-top: 20px;">{{ dashVars.books }}</h1>
                <RouterLink to="books_list" class="btn btn-primary stretched-link hide-slink"></RouterLink>
            </div>

        </div>
    </div>

    <div class=" container float-profile" style="margin-bottom:20px">
        <div class=" container d-flex flex-row justify-content-evenly ">
          
        
        <div style="width: 100%;">
            <h3 style="margin-top: 10px; margin-left: 10px;">Top 5 Books</h3>
            <div style="max-height: 90%">
            <Doughnut :data="chartData" :options="chartOptions" />
        </div>
            <p> (Currently Issued)</p>
        </div>
        <div class="container d-flex align-items-center justify-content-center">


            <form  @submit.prevent="updatePolicy" >
                <h3 style="margin-top: 10px;">Policy</h3>
                <div>
                    <div class="mb-3">
                        <label>Max Borrow Days</label>
                        <input type="number" name="MaxBorrowDays" class="form-control"
                            placeholder="No. of days to allow borrow." :value="dashVars.mxd" min="3" required>
                    </div>
                    <div class="mb-3">
                        <label>Max Borrow Count</label>
                        <input type="number" name="MaxBorrowBooks" class="form-control"
                            placeholder="No. of books that can be borrowed at a time." :value="dashVars.mxc" min="3" required>
                    </div>
                    <div class="mb-3">
                        <label>Auto Approve</label>
                        <select name="AutoApprove" class="form-select" required>
                            <option value="0">Off</option>
                            <option value="1" :selected="dashVars.auto">On</option>
                        </select>
                    </div>

                    <button type="submit" class="btn btn-dark" style="width: 100%;"> Update </button>

                </div>
            </form>
        </div>
    </div>
    <div class="adminbuttons">
        <button class="btn btn-dark" :disabled="exportDisabled" @click="exportData()">{{exportDisabled? "Export Request Received" :"Export Activity History"}}</button>
        <button class="btn btn-dark" @click="viewExports()">View Recent Exports</button>
        <button class="btn btn-dark" :disabled="reminderDisabled" @click="sendReminder()">{{reminderDisabled? "Reminders queued" :"Send Reminders"}}</button>
        <button class="btn btn-dark" :disabled="monthlyDisabled" @click="requestMonthlyReport()">{{monthlyDisabled? "Mailing Shortly": `Monthly Report - ${prevMonth}`}}</button>
    </div>
    </div>
    <div class="overlay" v-show="showOverlay">
          <div class="overlay-content">
            <i class="bi bi-x-lg" @click="showOverlay = false" style="position: absolute; top: 20px; right: 20px;"></i>

            <h2 class="mb-2">Recent Export Requests</h2>
            <table class="table table-hover">
                <thead>
                    <th> S. No. </th>
                    <th> Time </th>
                    <th> Status </th>
                    <th> Result </th>
                </thead>
                <tbody>
                    <tr v-for="(i, index) in exportsHistory">
                        <td>{{ index + 1 }}.</td>
                        <td>{{ (new Date(i.time.slice(0,-4))).toLocaleTimeString() }}</td>
                        <td>{{ i.status }}</td>
                        
                        <td><button class="btn btn-dark" :disabled="i.status != 'SUCCESS'" @click="window.open(API_URL + '/static/exports/'+i.result, '_blank');">Download</button></td>
                    </tr>
                </tbody>
            </table>
          </div>
    </div>
    <div class=" container float-profile">
        <div class=" container d-flex flex-row justify-content-evenly ">
          
        
        <div style="width: 100%; display:flex; flex-direction: column; align-items: center">
            <div style="width:100%;display:flex; flex-direction: row; justify-content: space-between">
            <h3 style="align-content: center">Daily Sales</h3>
            <div>
            <h3 style="margin:0px;">₹{{totalSales}}</h3>
            <p class="text-muted" style="margin:0px;">({{month}} 01 - {{month}} {{ todayDate }})</p>
            </div>
            </div>
            <div style="width: 90%">
            <Line :data="salesData" :options="salesOptions" />
        </div>
        </div>
            
        
    </div>
    
    </div>
    
    <div style="min-height: 15px"></div>
</template>

<style scoped>
.updated {
    color: green;
}
.adminbuttons {
    display: flex;
    justify-content: center;
    margin: 20px;
    button {
        margin: 10px;
    }
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.overlay-content {
  background-color: white;
  padding: 40px;
  border-radius: 10px;
  max-width: 80%;
  max-height: 50%;
  position: relative;
  overflow-y: auto
}
.card {
    box-shadow: 0px 6px 40px -32px rgba(0,0,0,0.75);
}
</style>