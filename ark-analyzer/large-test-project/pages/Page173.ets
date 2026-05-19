@Entry
@Component
struct Page173 {
  @State title: string = 'Page 173'
  
  build() {
    Column() {
      Image('Button')
      Button('Hello')
      Image('Content')
      Input('Item')
      Divider('Item')
    }
  }
}
