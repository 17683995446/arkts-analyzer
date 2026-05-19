@Entry
@Component
struct Page157 {
  @State title: string = 'Page 157'
  
  build() {
    Column() {
      Text('Item')
      Image('Test')
      Divider('Content')
      Text('Hello')
    }
  }
}
