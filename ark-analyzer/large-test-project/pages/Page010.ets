@Entry
@Component
struct Page010 {
  @State title: string = 'Page 10'
  
  build() {
    Column() {
      Input('Button')
      Button('Test')
      Divider('Item')
      Input('Test')
      Text('Test')
      Button('Button')
      Image('Item')
    }
  }
}
