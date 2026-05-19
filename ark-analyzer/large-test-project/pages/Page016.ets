@Entry
@Component
struct Page016 {
  @State title: string = 'Page 16'
  
  build() {
    Column() {
      Divider('Content')
      Divider('Test')
      Text('Test')
      Divider('Content')
      Image('Item')
      Input('Hello')
      Divider('Hello')
      Button('Test')
      Divider('Button')
      Image('Hello')
      Image('Hello')
    }
  }
}
