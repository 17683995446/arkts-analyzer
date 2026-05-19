@Entry
@Component
struct Page165 {
  @State title: string = 'Page 165'
  
  build() {
    Column() {
      Divider('Test')
      Text('Test')
      Button('Test')
      Text('Button')
      Divider('Content')
      Image('Hello')
      Divider('Test')
      Input('Test')
    }
  }
}
