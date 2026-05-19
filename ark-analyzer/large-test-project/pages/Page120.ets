@Entry
@Component
struct Page120 {
  @State title: string = 'Page 120'
  
  build() {
    Column() {
      Button('Button')
      Divider('Item')
      Text('Content')
      Divider('Hello')
      Divider('Content')
    }
  }
}
