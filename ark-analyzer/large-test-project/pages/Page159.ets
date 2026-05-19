@Entry
@Component
struct Page159 {
  @State title: string = 'Page 159'
  
  build() {
    Column() {
      Image('Test')
      Text('Content')
      Input('Test')
      Input('Content')
      Button('Content')
      Divider('Hello')
      Input('Test')
      Divider('Content')
      Text('Item')
      Text('Item')
      Text('Test')
      Input('Item')
    }
  }
}
