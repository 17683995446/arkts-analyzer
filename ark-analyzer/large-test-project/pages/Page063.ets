@Entry
@Component
struct Page063 {
  @State title: string = 'Page 63'
  
  build() {
    Column() {
      Image('Content')
      Image('Content')
      Image('Item')
      Input('Button')
      Input('Hello')
      Text('Hello')
      Divider('Hello')
    }
  }
}
