<script setup>
import { ref } from 'vue'
import {useRoute,  RouterLink} from 'vue-router'
import fetchData from '../helper.js'
import { AuthStore } from '../stores/main.js'
import router from '../router/index.js'
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

import { Chart as ChartJS, ArcElement, Tooltip, Legend, Colors } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip,Legend,Colors)
const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  
};

var chartData = ref({
  labels: [],
  datasets: [
    {
      data: [],
    },
  ],
})



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
function getColors(length) {
    let pallet2 = ["#0074D9", "#FF4136", "#2ECC40", "#FF851B", "#7FDBFF", "#B10DC9", "#FFDC00", "#001f3f", "#39CCCC", "#01FF70", "#85144b", "#F012BE", "#3D9970", "#111111", "#AAAAAA"];
    let pallet = ["#FF4136", "#2ECC40", "#FF851B", "#7FDBFF", "#B10DC9", "#FFDC00", "#001f3f", "#39CCCC", "#01FF70", "#85144b", "#F012BE", "#3D9970", "#111111", "#AAAAAA"];
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
                <a href="/admin/issued" class="btn btn-primary stretched-link hide-slink"></a>
            </div>

        </div>
        <div class="card" style="width: 18rem; margin: 20px;">

            <div class="card-body">
                <h5 class="card-title">Pending Requests</h5>
                <h1 class="card-text" style="margin-top: 20px;">{{ dashVars.req }}</h1>
                <a href="{{url_for('pending_requests')}}" class="btn btn-primary stretched-link hide-slink"></a>
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

    <div class=" container d-flex flex-row justify-content-evenly float-profile">
        <div>
          
        </div>
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
    <div style="min-height: 15px"></div>
</template>

<style scoped>
.updated {
    color: green;
}
</style>