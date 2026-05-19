@Entry
@Component
struct Page082 {
  @State title: string = 'Page 82'
  
  build() {
    Column() {
      Divider('Hello')
      Divider('Button')
      Image('Content')
      Input('Button')
      Image('Button')
    }
  }
}
