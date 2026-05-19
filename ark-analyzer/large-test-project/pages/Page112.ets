@Entry
@Component
struct Page112 {
  @State title: string = 'Page 112'
  
  build() {
    Column() {
      Image('Button')
      Divider('Test')
      Divider('Button')
      Input('Item')
      Input('Test')
    }
  }
}
