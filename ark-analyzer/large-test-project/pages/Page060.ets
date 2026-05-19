@Entry
@Component
struct Page060 {
  @State title: string = 'Page 60'
  
  build() {
    Column() {
      Button('Hello')
      Image('Test')
      Text('Test')
      Divider('Hello')
    }
  }
}
