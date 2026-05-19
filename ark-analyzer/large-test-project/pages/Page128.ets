@Entry
@Component
struct Page128 {
  @State title: string = 'Page 128'
  
  build() {
    Column() {
      Input('Hello')
      Image('Hello')
      Text('Content')
      Divider('Test')
      Text('Button')
      Divider('Button')
      Text('Button')
    }
  }
}
