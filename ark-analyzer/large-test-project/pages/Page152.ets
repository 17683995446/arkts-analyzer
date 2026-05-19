@Entry
@Component
struct Page152 {
  @State title: string = 'Page 152'
  
  build() {
    Column() {
      Divider('Button')
      Button('Test')
      Button('Hello')
    }
  }
}
