@Entry
@Component
struct Page032 {
  @State title: string = 'Page 32'
  
  build() {
    Column() {
      Divider('Content')
      Text('Hello')
      Divider('Hello')
      Image('Button')
      Text('Content')
      Divider('Test')
      Input('Item')
    }
  }
}
