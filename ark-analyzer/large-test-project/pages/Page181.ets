@Entry
@Component
struct Page181 {
  @State title: string = 'Page 181'
  
  build() {
    Column() {
      Text('Content')
      Input('Content')
      Text('Test')
      Text('Content')
      Input('Content')
      Divider('Content')
      Input('Hello')
      Divider('Test')
    }
  }
}
