@Component
struct UserList {
  @State users: User[] = []
  @State loading: boolean = false
  @State selectedUser: User | null = null

  aboutToAppear() {
    this.loadUsers()
  }

  async loadUsers() {
    this.loading = true
    try {
      const response = await fetch('/api/users')
      this.users = await response.json()
    } catch (error) {
      console.error('Failed to load users:', error)
    } finally {
      this.loading = false
    }
  }

  build() {
    Column() {
      if (this.loading) {
        LoadingProgress()
          .width(50)
          .height(50)
      } else {
        List() {
          ForEach(this.users, (user: User) => {
            ListItem() {
              UserCard({
                name: user.name,
                email: user.email,
                avatar: user.avatar
              })
              .onClick(() => {
                this.selectedUser = user
              })
            }
          })
        }
        .width('100%')
      }
    }
    .width('100%')
    .height('100%')
  }
}

interface User {
  id: number
  name: string
  email: string
  avatar: string
  createdAt: string
}

export default UserList
