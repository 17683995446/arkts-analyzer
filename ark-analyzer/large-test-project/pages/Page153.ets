@Entry
@Component
struct Page153 {
  @State title: string = 'Page 153'
  
  build() {
    Column() {
      Text('Hello')
      Image('Test')
      Divider('Button')
      Button('Button')
      Input('Button')
      Divider('Button')
      Image('Test')
    }
  }
}
