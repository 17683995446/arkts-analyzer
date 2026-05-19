@Entry
@Component
struct Page040 {
  @State title: string = 'Page 40'
  
  build() {
    Column() {
      Divider('Button')
      Text('Item')
      Button('Button')
      Button('Test')
      Text('Content')
      Divider('Test')
      Image('Item')
      Button('Test')
      Text('Item')
      Divider('Hello')
      Button('Button')
      Divider('Button')
    }
  }
}
