@Entry
@Component
struct Page185 {
  @State title: string = 'Page 185'
  
  build() {
    Column() {
      Button('Button')
      Text('Test')
      Input('Button')
      Button('Item')
      Input('Test')
      Input('Item')
    }
  }
}
