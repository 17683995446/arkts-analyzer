@Entry
@Component
struct Page051 {
  @State title: string = 'Page 51'
  
  build() {
    Column() {
      Divider('Button')
      Input('Hello')
      Text('Hello')
      Text('Button')
      Divider('Button')
      Button('Test')
    }
  }
}
