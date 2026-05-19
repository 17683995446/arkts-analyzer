@Entry
@Component
struct Page027 {
  @State title: string = 'Page 27'
  
  build() {
    Column() {
      Image('Test')
      Divider('Hello')
      Input('Button')
      Input('Content')
      Button('Content')
    }
  }
}
