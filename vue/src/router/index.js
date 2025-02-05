import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import BooksList from '../views/BooksList.vue'
import BookAdd from '@/views/BookAdd.vue'
import Book from '@/views/Book.vue'
import Error from '../views/Error.vue'
import SectionsList from '@/views/SectionsList.vue'
import Section from '@/views/Section.vue'
import SectionAdd from '@/views/SectionAdd.vue'
import EditSection from '@/views/EditSection.vue'
import EditBook from '@/views/EditBook.vue'
import UsersList from '@/views/admin/UsersList.vue'
import UserDash from '@/components/userDash.vue'
import BookRead from '@/views/BookRead.vue'
import Requests from '@/views/admin/Requests.vue'
import IssuedList from '@/views/admin/IssuedList.vue'
import Register from '@/views/Register.vue'
import EditUser from '@/views/EditUser.vue'
import { AuthStore } from '../stores/main.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/books_list',
      name: 'books_list',
      component: BooksList
    },
    {
      path: '/sections_list',
      name: 'sections_list',
      component: SectionsList
    },
    {
      path: '/book/:id',
      name: 'book',
      component: Book,
    },
    {
      path: '/book/:id/read',
      name: 'book_read',
      component: BookRead
    },
    {
      path: '/section/:id',
      name: 'section',
      component: Section
    },
    {
      path: '/users_list',
      name: 'users_list',
      component: UsersList
    },
    {
      path:  '/user/:id',
      name: 'user_dash',
      component: UserDash
    },
    {
      path: '/section/:id/edit',
      name: 'edit_section',
      component: EditSection
    },
    {
      path: '/book/:id/edit',
      name: 'edit_book',
      component: EditBook
    },
    {
      path: '/book_add',
      name: 'book_add',
      component: BookAdd
    },
    {
      path: '/create_section',
      name: 'create_section',
      component: SectionAdd
    },
    {
      path: '/requests',
      name: 'requests',
      component: Requests
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/issued_list',
      name: 'issued_list',
      component: IssuedList
    },{
      path: '/change_info',
      name: 'change_info',
      component: EditUser
    },
    {
      path: '/error',
      name: 'error',
      component: Error
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.name !== 'login' && to.name !=='home' && to.name !=='register' && !AuthStore().loggedIn) next({ name: 'login' })
  else next()
})

export default router
