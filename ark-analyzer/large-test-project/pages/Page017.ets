@Entry
@Component
struct Page017 {
  @State title: string = 'Page 17'
  
  build() {
    Column() {
      Text('Test')
      Input('Item')
      Text('Item')
    }
  }
}
