@Entry
@Component
struct Page012 {
  @State title: string = 'Page 12'
  
  build() {
    Column() {
      Image('Hello')
      Button('Item')
      Image('Button')
      Input('Test')
      Input('Hello')
      Input('Button')
      Input('Item')
      Text('Hello')
      Button('Item')
      Input('Item')
      Divider('Test')
      Divider('Content')
    }
  }
}
