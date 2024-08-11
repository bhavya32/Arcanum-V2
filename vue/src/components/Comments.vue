<script setup>
import {ref, toRef, watch, defineEmits} from 'vue'
import fetchData from '../helper.js'
import {postJSON} from '../helper.js'
import Swal from 'sweetalert2'
import moment from 'moment'
const props = defineProps({
  book_id: Number,
  user: String
})
import { AuthStore } from '../stores/main.js'
var s = AuthStore()
var myCommentExists = ref(false)
var myComment = ref({})
var comments = ref([])
var noComments = ref(false)
async function init() {
    fetchData(`/api/book/${props.book_id}/comments`).then(data => {
        console.log(data)
        //comments.value = data["comments"]
        if (data["comments"].length == 0) {
            noComments.value = true
        }
        for (var i of data["comments"]) {
            if (i["user"] == props.user) {
                myCommentExists.value = true
                myComment.value = i
            } else {
                comments.value.push(i)
            }
        }

        /*if ("content" in data["my_comment"]) {
            myCommentExists.value = true
            myComment.value = data["my_comment"]
            
        }*/
    })
}

async function deleteMyComment() {
    //console.log("deleting", id)
    fetchData(`/api/comments/${props.book_id}/delete`).then(data => {
        if (data["status"] == "success") {
            myCommentExists.value = false
            myComment.value = {}
            if (comments.value.length == 0) {
                noComments.value = true
            }
        }
    })
}

async function deleteComment(id) {
    fetchData(`/api/admin/comments/${id}/delete`).then(data => {
        if (data["status"] == "success") {
            comments.value = comments.value.filter(x => x.id != id)
            if (comments.value.length == 0) {
                noComments.value = true
            }
        }
    })
}
var commentAdd = ref("")

async function addComment() {
    console.log("adding comment", commentAdd.value)
    var cmt = commentAdd.value.trim()
    if (cmt == "") {return}
    postJSON(`/api/book/${props.book_id}/comment`, {
        comment: cmt
    }).then(data => {
        if (data["status"] == "success") {
            myCommentExists.value = true
            myComment.value = {
                user: props.user,
                content: cmt,
                date: new Date(),
            }
            commentAdd.value = ""
            noComments.value = false
        }
        else {
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: data["msg"],
            })
        }
    })

}
function dt(date){
    return moment(date).fromNow()
}

init()
</script>
<template>
    <div style="margin-top: 20px; width:90%">
        <div class="comments">
            
            <table class="table table-hover">
                <tr v-if="noComments">No comments yet.</tr>
                <tr v-if="myCommentExists">
                    <td>
                        <div class="comment">
                            <div style="display:flex; flex-direction: row; justify-content: space-between;">
                                <h5><i class="bi bi-person-circle"></i> You</h5>
                                
                            </div>
                            <p class="text-muted">{{ dt(myComment.date) }} <button class="btn" @click="deleteMyComment()"><i class="bi bi-trash"></i></button></p>
                            <p>{{ myComment.content }}</p>
                        </div>
                    </td>
                </tr>
                <tr v-for="comment in comments">
                    <td>
                        <div class="comment">
                            <div style="display:flex; flex-direction: row; justify-content: space-between;">
                                <h5><i class="bi bi-person-circle"></i> {{comment.user}}</h5>
                                <h6>Rating - {{ comment.rating }}/5</h6>
                            </div>
                            <p class="text-muted">{{ dt(comment.date) }} <button v-if="s.userInfo.role == 'librarian'" class="btn" @click="deleteComment(comment.id)"><i class="bi bi-trash"></i></button></p>
                            <p>{{ comment.content }}</p>
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        <div v-show="!myCommentExists" class="add-comment">
            <textarea class="form-control" v-model="commentAdd" placeholder="Add a comment"></textarea>
            <button class="btn btn-dark" @click="addComment()">Post Comment</button>
        </div>
    </div>
</template>

<style scoped>
.comment {
    display: flex;
    flex-direction: column;
    padding:20px;
}
tr {
    
    border-top: 0px!important;
    border-bottom: 1px solid #dee2e6;
    border-radius: 20px
}
.form-control {
    margin-bottom: 10px;
    border-radius: 20px;
    min-height: 100px;
    padding:10px 20px;
}
</style>