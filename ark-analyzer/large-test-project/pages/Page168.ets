@Entry
@Component
struct Page168 {
  @State title: string = 'Page 168'
  
  build() {
    Column() {
      Button('Test')
      Text('Hello')
      Image('Button')
      Button('Hello')
      Input('Button')
      Button('Hello')
      Divider('Item')
      Button('Content')
    }
  }
}
