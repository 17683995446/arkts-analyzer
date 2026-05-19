@Entry
@Component
struct Page000 {
  @State title: string = 'Page 0'
  
  build() {
    Column() {
      Image('Test')
      Divider('Test')
      Divider('Button')
    }
  }
}
