<script setup>
import { postData } from '../helper.js'
import router from '../router/index.js'


function addSection(form){
    console.log(form.target)
    var formData = new FormData()
    formData.append('section_name', form.target.section_name.value)
    formData.append('section_desc', form.target.section_desc.value)
    if (form.target.section_img.files.length > 0) {
        formData.append('section_img', form.target.section_img.files[0])
    }
    postData('/api/sections', formData).then(res => {
        var id = res["id"]
        router.push('/section/' + id.toString())
    })
}

</script>

<template>
    <div id="body">
    <div class="float-login container">
      <h3 class="mb-3 text-center">Create New Section</h3>
      <form enctype="multipart/form-data" id="createSection" method="POST" @submit.prevent="addSection">


        <div class="mb-3">
          <label class="text-muted mb-2" for="username-input">Section Name</label>
          <input maxlength="50" class="form-control" type="text" name="section_name" id="secname-input" required autofocus>
        </div>

        <div class="text-muted mb-4">
          <label for="section_desc">Section Description</label>
          <br><textarea maxlength="300" class="form-control" name="section_desc" form="createSection" required></textarea>
        </div>
        <div class="text-muted mb-4">
          <label for="myfile">Base Image (200px * 250px)</label>
          <input type="file" id="myfile" name="section_img" accept="image/png, image/jpeg">
        </div>
        <div class="mb-4" style="width: 100%;">
          <button type="submit" class="btn btn-dark" style="width: 100%;"> Create </button>
        </div>
      </form>
    </div>

  </div>
</template>