@Entry
@Component
struct Page064 {
  @State title: string = 'Page 64'
  
  build() {
    Column() {
      Image('Button')
      Divider('Test')
      Input('Item')
      Button('Button')
      Image('Test')
      Text('Test')
      Text('Content')
      Text('Button')
      Button('Item')
      Text('Hello')
      Button('Content')
    }
  }
}
