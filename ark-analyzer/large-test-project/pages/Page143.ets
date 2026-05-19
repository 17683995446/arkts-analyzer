@Entry
@Component
struct Page143 {
  @State title: string = 'Page 143'
  
  build() {
    Column() {
      Button('Test')
      Divider('Button')
      Divider('Item')
      Input('Hello')
      Input('Content')
      Image('Item')
      Button('Item')
      Input('Test')
      Image('Test')
      Divider('Content')
      Button('Test')
    }
  }
}
