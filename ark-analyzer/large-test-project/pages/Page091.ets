@Entry
@Component
struct Page091 {
  @State title: string = 'Page 91'
  
  build() {
    Column() {
      Divider('Hello')
      Input('Button')
      Image('Content')
      Text('Content')
    }
  }
}
