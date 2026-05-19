@Entry
@Component
struct Page066 {
  @State title: string = 'Page 66'
  
  build() {
    Column() {
      Button('Content')
      Divider('Item')
      Text('Item')
      Input('Hello')
    }
  }
}
